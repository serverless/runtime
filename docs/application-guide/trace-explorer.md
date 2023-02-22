<!--
title: Trace Explorer
menuText: Trace Explorer
description: Using Explorer and understanding Traces and Spans.
menuOrder: 5
-->

# Trace Explorer

Traces, Spans, Logs, Errors, and Warnings are captured and made available in
Trace Explorer for your AWS Lambda functions when [Instrumentation](./instrumentation.md)
is enabled.

Serverless Console provides a set of tools to analyzing Traces.

## Trace Explorer List

Similar to the [Metrics View](./metrics.md), the Trace Explorer provides a
starting point for troubleshooting AWS Lambda function invocations across your
org. You can use the rich filters to narrow in on errors, warnings, and
performance issues across all of your AWS Lambda functions across your org.

## Filters

Filtering allows you to narrow in on particular behavior and time frame for 
to isolate invocations. You can filter on:

- **Error & Warning Types** - Errors and Warnings can be captured in the trace,
these includes user defined as well as SDK defined errors and warnings. More
details on each Error & Warning type is available below.
- **Error & Warning Messages** - When an Error or Warning is captured
automatically or manually using the Serverless SDK, a message string is saved
with the Error/Warning. You can filter for the Traces based on the Error or
Warning messages that were captured in the trace. Traces are filtered if any of
the Errors or Warnins in the Trace contained the message string.
- **Resource** - You can select the specific resource by AWS ARN, like a
specific Lambda function.
- **Environment**, **Namespace** - These properties are inferred from the
CloudFormation stack when Instrumentation is added, or they are set manually
on the Integration settings page. Once set, you can filter the traces based on
these properties set on the function.
- **AWS Account**, **Region** - Serverless Console collects information for all
instrumented Lambda functions across AWS accounts and regions; you  can filter
on any of these properties.
- **Timeframe** - Any timeframe within the last 30 days can be used.


## Error & Warning Types

- `ERROR_TYPE_UNCAUGHT` - The Lambda function handler had a fatal error and
caused the invocation to fail.
- `ERROR_TYPE_CAUGHT_USER` - The Lambda function handler had an error that was
captured using the SDK. This can include Error objects or strings that were
captured implicitely (e.g. `console.error`) or explicitely using the provided
SDK methods.
- `ERROR_TYPE_CAUGHT_SDK_USER` - An internal SDK error that was reported due to
misuse of the SDK. These errors do not cause handler failures, but misusage of
the SDK may result in partial collection. For example, using the `setTag` method
with invalid inputs will result in this type of error, and the tag will not be
set.
- `ERROR_TYPE_CAUGHT_SDK_INTERNAL` - This is an internal SDK error. These errors
will not cause handler failures. This type of error is rare and monitored by
Serverless.
- `WARNING_TYPE_USER` - This is a warning message that was generated in the
handler and collected by the SDK. For example, `console.warn("record lookup
failed")`, would result in this type of warning.
- `WARNING_TYPE_SDK_USER` - This is an internal SDK warning that was reported
due to misuse of the SDK.
- `WARNING_TYPE_SDK_INTERNAL` - An internal SDK warning that was reported due to
an internal issue not caused by user input. These are non-fatal issues that may
result in partial data collection. For example, if a binary input payload is
used then DevMode may not be able to ingest the payload resulting in this type
of warning.


## Trace Details

Trace Details provides a way to look at the details of an individual AWS Lambda
Invocation trace, including the spans, tags, logs, errors, and warnings.

The Trace details are deep-linked so you can easily share the URL with your
team when collaboratively troubleshooting.

The pane on the right, the Inspector, presents the details about the Trace. If
a Span, Error, or Warning are selected from the timeline, then the Inspector
will shows details about the selected item.

The Inspector for the trace will present details about the trace as tags. These
tags include information about the runtime, like `Cold Start`, `Request ID`,
and `Arch`, as well as metrics like `Memory Used`, `Billed ms`, `Invoke`. Check
out the tooltips for details on each of the tags.

### Spans

A Trace contains a set of Spans associated with and displayed in the style of a 
Gantt Chart. This chart provides you with context for when, and how long various
subsequent interactions took. 

A span can be selected from the timeline to view the details of the span in the
Inspector.

### Logs

Logs are also collected and made available in the Trace details. To view the
logs for the Lambda invocation, select the root span, `aws.lambda`.

If the logs are structured and formatted as JSON, they will be parsed and
displayed with pretty formatting.

### Errors & Warnings

Errors and Warnings, like Spans, are displayed on the timeline. Errors and
Warnings can be selected to view the details.

Errors and warnings include a `name`, `message`, and `stack` when available.
The Node.js SDK captures the stacktraces for all requests when possible. It also
captures `Error` objects, so the `name`, `message`, and `stack` from the `Error`
are made available as an error in the Inspector.