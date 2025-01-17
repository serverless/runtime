package slslambda

import (
	"crypto/rand"
	"encoding/base64"
	"encoding/hex"
	"fmt"

	tagsv1 "buf.build/gen/go/serverless/sdk-schema/protocolbuffers/go/serverless/instrumentation/tags/v1"
	instrumentationv1 "buf.build/gen/go/serverless/sdk-schema/protocolbuffers/go/serverless/instrumentation/v1"
	"github.com/aws/aws-sdk-go/aws"
	"google.golang.org/protobuf/proto"
)

const (
	tracePayloadPrefix     = "SERVERLESS_TELEMETRY.T."
	lambdaPlatform         = "lambda"
	sdkName                = "aws-lambda-sdk"
	rootSpanName           = "aws.lambda"
	initializationSpanName = "aws.lambda.initialization"
	invocationSpanName     = "aws.lambda.invocation"
	spanIDBytesLength      = 8
	traceIDBytesLength     = 16
	eventIDBytesLength     = 16
)

var version = "undefined"

func (w wrapper) printTrace(root *rootContext) error {
	payload, err := convertToPayload(root.spanTreeRoot, root.requestID, w.environment, w.tags)
	if err != nil {
		return fmt.Errorf("convert: %w", err)
	}
	printServerlessTelemetryLogLine(payload)
	return nil
}

func slsTags(tags tags, environment string) *tagsv1.SlsTags {
	return &tagsv1.SlsTags{
		OrgId:    string(tags.OrganizationID),
		Platform: aws.String(lambdaPlatform),
		Service:  string(tags.FunctionName),
		Region:   aws.String(string(tags.AWSRegion)),
		Sdk: &tagsv1.SdkTags{
			Name:    sdkName,
			Version: version,
		},
		Environment: &environment,
	}
}

func printServerlessTelemetryLogLine(payload *instrumentationv1.TracePayload) {
	bytes, err := proto.Marshal(payload)
	if err != nil {
		debugLog("proto marshal trace payload:", err)
	}
	fmt.Println(tracePayloadPrefix + base64.StdEncoding.EncodeToString(bytes))
}

func generateID(size int) ([]byte, error) {
	b := make([]byte, size)
	if _, err := rand.Read(b); err != nil {
		return nil, fmt.Errorf("rand read: %w", err)
	}
	dst := make([]byte, hex.EncodedLen(size))
	hex.Encode(dst, b)
	return dst, nil
}

func generateSpanID() ([]byte, error) {
	return generateID(spanIDBytesLength)
}

func generateTraceID() ([]byte, error) {
	return generateID(traceIDBytesLength)
}

func generateEventID() ([]byte, error) {
	return generateID(eventIDBytesLength)
}
