package slslambda

import (
	"context"
	"errors"
	"github.com/aws/aws-lambda-go/lambdacontext"
	instrumentationv1 "go.buf.build/protocolbuffers/go/serverless/sdk-schema/serverless/instrumentation/v1"
	"time"
)

type (
	span interface {
		Span() *basicSpan
		Close()
		ToProto(traceID, spanID, parentSpanID []byte, requestID string, tags tags) *instrumentationv1.Span
	}
	rootContext struct {
		requestID    string
		invocation   *basicSpan
		spanTreeRoot *basicSpan
	}
	errorEvent struct {
		timestamp time.Time
		error
	}
	warningEvent struct {
		timestamp time.Time
		message   string
	}
)

func newRootContext(ctx context.Context, initializationStart, invocationStart time.Time) *rootContext {
	root := newSpanWithStartTime(rootSpanName, rootSpanStartTime(initializationStart, invocationStart))
	if isColdStart(initializationStart) {
		root.children = append(root.children, newInitializationSpan(initializationStart, invocationStart))
	}
	invocation := newSpanWithStartTime(invocationSpanName, invocationStart)
	root.children = append(root.children, invocation)
	return &rootContext{
		requestID:    requestID(ctx),
		invocation:   invocation,
		spanTreeRoot: root,
	}
}

func rootSpanStartTime(initializationStart, invocationStart time.Time) time.Time {
	if isColdStart(initializationStart) {
		return initializationStart
	} else {
		return invocationStart
	}
}

func isColdStart(initializationStart time.Time) bool {
	return !initializationStart.IsZero()
}

func requestID(ctx context.Context) string {
	if lambdaContext, ok := lambdacontext.FromContext(ctx); ok {
		return lambdaContext.AwsRequestID
	}
	return ""
}

func rootFromContext(ctx context.Context) (*rootContext, error) {
	span, ok := ctx.Value(rootContextKey).(*rootContext)
	if !ok {
		return nil, errors.New("no root span in context")
	}
	return span, nil
}

func currentSpanFromContext(ctx context.Context) (*basicSpan, error) {
	span, ok := ctx.Value(currentSpanContextKey).(*basicSpan)
	if !ok {
		return nil, errors.New("no current span in context")
	}
	return span, nil
}
