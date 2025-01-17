import logging
import os
import time
import boto3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "test_dependencies"))
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

sys.path.pop()


s3_client = boto3.client("s3")
sqs = boto3.client("sqs")
sns = boto3.client("sns")
lambda_client = boto3.client("lambda")
ssm = boto3.client("ssm")
dynamodb = boto3.client("dynamodb")
sts = boto3.client("sts")

invocation_count = 0


def _sqs():
    queue_name = f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME')}-{invocation_count}.fifo"
    queue = sqs.create_queue(QueueName=queue_name, Attributes={"FifoQueue": "true"})
    queue_url = queue.get("QueueUrl")
    sqs.send_message(
        QueueUrl=queue_url,
        MessageBody="test",
        MessageGroupId=str(int(time.time() * 1000)),
        MessageDeduplicationId=str(int(time.time() * 1000)),
    )
    sqs.delete_queue(QueueUrl=queue_url)


def _sns():
    topic_name = f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME')}-{invocation_count}"
    topic = sns.create_topic(Name=topic_name)
    topic_arn = topic.get("TopicArn")
    sns.publish(TopicArn=topic_arn, Message="test")
    sns.delete_topic(TopicArn=topic_arn)


def _dynamodb():
    table_name = f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME')}-{invocation_count}"
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "country", "KeyType": "HASH"},
            {"AttributeName": "city", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "country", "AttributeType": "S"},
            {"AttributeName": "city", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    while table.get("Table", {}).get("TableStatus") != "ACTIVE":
        time.sleep(0.1)
        table = dynamodb.describe_table(TableName=table_name)

    try:
        dynamodb.put_item(
            TableName=table_name,
            Item={
                "country": {"S": "France"},
                "city": {"S": "Nice"},
                "type": {"S": "city"},
            },
        )
        from boto3.dynamodb.conditions import Key

        dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="#country = :country",
            ExpressionAttributeNames={"#country": "country"},
            ExpressionAttributeValues={":country": {"S": "France"}},
        )

        dynamodb_resource = boto3.resource("dynamodb", region_name="us-east-1")
        from boto3.dynamodb.conditions import Key

        list(
            dynamodb_resource.meta.client.get_paginator("query").paginate(
                TableName=table_name,
                KeyConditionExpression=Key("country").eq("France"),
                FilterExpression=Key("type").eq("city"),
                ProjectionExpression="country, city",
            )
        )

        class LocationModel(Model):
            class Meta:
                table_name = (
                    f"{os.environ.get('AWS_LAMBDA_FUNCTION_NAME')}-{invocation_count}"
                )

            country = UnicodeAttribute(hash_key=True)
            city = UnicodeAttribute(range_key=True)

        paris = LocationModel("France", "Paris")
        paris.save()
        if len([l for l in LocationModel.query("France")]) != 2:
            raise Exception("PynamoDB query failed")
    finally:
        dynamodb.delete_table(TableName=table_name)


def handler(event, context) -> str:
    global invocation_count
    try:
        invocation_count += 1
        sts.get_caller_identity()

        try:
            lambda_client.get_function(FunctionName="not-existing")
        except Exception:
            pass

        try:
            ssm.get_parameter(Name="/not/existing")
        except Exception:
            pass

        _sqs()
        _sns()
        _dynamodb()
        return "ok"

    except Exception as ex:
        logging.info(ex)
        raise ex
