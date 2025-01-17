'use strict';

// eslint-disable-next-line import/no-unresolved
const { S3, SQS, SNS, DynamoDB, STS, SSM, Lambda } = require('aws-sdk');

const wait = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const s3 = new S3();
const sqs = new SQS();
const sns = new SNS();
const lambda = new Lambda();
const ssm = new SSM();
const dynamoDb = new DynamoDB();
const dynamodbDocumentClient = new DynamoDB.DocumentClient();
const sts = new STS();

let invocationCount = 0;

module.exports.handler = async () => {
  try {
    ++invocationCount;

    // STS (confirm on tracing of any AWS service)
    await sts.getCallerIdentity().promise();

    // s3.getSignedUrlPromise won't issue a real HTTP request
    // It's injected to confirm no trace span will be created for it
    await s3.getSignedUrlPromise('putObject', { Bucket: 'test', Key: 'test', Expires: 500 });

    // Test request error reporting
    try {
      await lambda.getFunction({ FunctionName: 'not-existing' }).promise();
    } catch (error) {
      // do nothing
    }
    try {
      // Special error case: https://github.com/aws/aws-sdk-js/issues/4330
      await ssm.getParameter({ Name: '/not/existing' }).promise();
    } catch (error) {
      // do nothing
    }

    // SQS
    const queueName = `${process.env.AWS_LAMBDA_FUNCTION_NAME}-${invocationCount}.fifo`;
    const { QueueUrl: queueUrl } = await sqs
      .createQueue({ QueueName: queueName, Attributes: { FifoQueue: 'true' } })
      .promise();
    await sqs
      .sendMessage({
        QueueUrl: queueUrl,
        MessageBody: 'test',
        MessageGroupId: String(Date.now()),
        MessageDeduplicationId: String(Date.now()),
      })
      .promise();
    await sqs.deleteQueue({ QueueUrl: queueUrl }).promise();

    // SNS
    const topicName = `${process.env.AWS_LAMBDA_FUNCTION_NAME}-${invocationCount}`;
    const { TopicArn: topicArn } = await sns.createTopic({ Name: topicName }).promise();
    await sns.publish({ TopicArn: topicArn, Message: 'test' }).promise();
    await sns.deleteTopic({ TopicArn: topicArn }).promise();

    // DynamoDB
    const tableName = `${process.env.AWS_LAMBDA_FUNCTION_NAME}-${invocationCount}`;
    await dynamoDb
      .createTable({
        TableName: tableName,
        AttributeDefinitions: [{ AttributeName: 'id', AttributeType: 'S' }],
        KeySchema: [{ AttributeName: 'id', KeyType: 'HASH' }],
        BillingMode: 'PAY_PER_REQUEST',
      })
      .promise();
    let status;
    do {
      await wait(100);
      status = (await dynamoDb.describeTable({ TableName: tableName }).promise()).Table.TableStatus;
    } while (status !== 'ACTIVE');
    await dynamoDb.putItem({ TableName: tableName, Item: { id: { S: 'test' } } }).promise();
    await dynamoDb
      .query({
        TableName: tableName,
        KeyConditionExpression: '#id = :id',
        ExpressionAttributeNames: { '#id': 'id' },
        ExpressionAttributeValues: { ':id': { S: 'test' } },
      })
      .promise();
    await dynamodbDocumentClient
      .query({
        TableName: tableName,
        KeyConditionExpression: '#id = :id',
        ExpressionAttributeNames: { '#id': 'id' },
        ExpressionAttributeValues: { ':id': 'test' },
      })
      .promise();
    await dynamoDb.deleteTable({ TableName: tableName }).promise();

    return 'ok';
  } catch (error) {
    console.log(error);
    throw error;
  }
};
