'use strict';

const path = require('path');
const Long = require('long');

const projectDir = path.resolve(__dirname, '../..');

const { expect } = require('chai');

const {
  TracePayload,
  AwsLambdaTags_Outcome: AwsLambdaTagsOutcome,
} = require(`${projectDir}/dist/index.cjs`);

const longValue = new Long('12313213', '12313221', true);

const testTracePayload = {
  slsTags: {
    orgId: 'abc123',
    sdk: {
      name: 'aws-lambda-sdk',
      version: '0.0.1',
    },
    platform: 'lambda',
    region: 'us-east-1',
    service: 'my-test-function',
  },
  spans: [
    {
      spanId: Buffer.from('Y2M4MWUwNjctMWNmYi00ZmYxLWE2OWItMDVhOTQ4NGZmZmFk'),
      traceId: Buffer.from('YTZkZTMxMzgtMmM0ZS00M2QxLTk0YTAtMDVmMjQ0NzJlNjg1'),
      name: 'test',
      startTimeUnixNano: longValue,
      endTimeUnixNano: longValue,
      tags: {
        aws: {
          lambda: {
            arch: 'arm64',
            isColdstart: true,
            eventType: 'aws.apigatewayv2',
            eventSource: 'aws.apigatewayv2',
            logGroup: 'abc12',
            logStreamName: 'abc123',
            maxMemory: longValue,
            name: 'my-test-function',
            requestId: 'bdb40738-ff36-48c0-9842-9befd0141cd6',
            version: '$LATEST',
            outcome: AwsLambdaTagsOutcome.OUTCOME_SUCCESS,
            apiGateway: {
              accountId: '012345678901',
              apiId: 'abc123',
              apiStage: 'dev',
              request: {
                id: '2e4d98fe-1603-477f-b976-1013e84ea4a6',
                headers: '',
                timeEpoch: longValue,
                protocol: 'HTTP/1.1',
                domain: 'abc.example.com',
                method: 'GET',
                path: '/test',
              },
            },
          },
        },
      },
    },
  ],
};

const normalizeObject = (obj) => {
  for (const [key, value] of Object.entries(obj)) {
    if (value == null) delete obj[key];
    else if (typeof value === 'object') normalizeObject(value);
  }
  return obj;
};

describe('span-schema', () => {
  it('should parse AWS Lambda Root Span', () => {
    expect(testTracePayload).to.deep.equal(
      normalizeObject(TracePayload.decode(TracePayload.encode(testTracePayload).finish()))
    );
  });
});
