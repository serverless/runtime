from serverless.aws_lambda_otel_extension.shared.constants import INSTRUMENTATION_TILDE_MAP, LOG_LEVEL_MAP, TRUTHY
from serverless.aws_lambda_otel_extension.shared.defaults import (
    DEF_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
    DEF_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS,
    DEF_SLS_EXTENSION_COLLECTOR_URL,
    DEF_SLS_EXTENSION_LOG_LEVEL,
    DEF_SLS_EXTENSION_METRICS_ENABLED,
)
from serverless.aws_lambda_otel_extension.shared.environment import (
    ENV_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
    ENV_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS,
    ENV_OTEL_PYTHON_LOG_CORRELATION,
    ENV_SLS_EXTENSION_COLLECTOR_URL,
    ENV_SLS_EXTENSION_FLUSH_TIMEOUT,
    ENV_SLS_EXTENSION_LOG_LEVEL,
    ENV_TEST_DRY_LOG,
    ENV_TEST_DRY_LOG_PRETTY,
)
from serverless.aws_lambda_otel_extension.shared.utilities import default_if_none, split_or_none

SETTINGS_SLS_EXTENSION_COLLECTOR_URL = default_if_none(ENV_SLS_EXTENSION_COLLECTOR_URL, DEF_SLS_EXTENSION_COLLECTOR_URL)

# Flag for enabling/disabling OpenTelemetry metrics collection
SETTINGS_SLS_EXTENSION_METRICS_ENABLED = DEF_SLS_EXTENSION_METRICS_ENABLED

# Process enabled/disabled instrumentation list
SETTINGS_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS = default_if_none(
    split_or_none(ENV_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS), DEF_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS
)

SETTINGS_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS = default_if_none(
    split_or_none(ENV_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS), DEF_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS
)

# Iterate through a copy of the list and expand the tidle strings.
for _instrumentation in SETTINGS_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS[:]:
    _expanded_instrumentation = INSTRUMENTATION_TILDE_MAP.get(_instrumentation)
    if _expanded_instrumentation:
        SETTINGS_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS.remove(_instrumentation)
        SETTINGS_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS.extend(_expanded_instrumentation)

for _instrumentation in SETTINGS_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS[:]:
    _expanded_instrumentation = INSTRUMENTATION_TILDE_MAP.get(_instrumentation)
    if _expanded_instrumentation:
        SETTINGS_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS.remove(_instrumentation)
        SETTINGS_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS.extend(_expanded_instrumentation)

# Reduce the set size and make it pretty for no functional reason.
SETTINGS_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS = sorted(set(SETTINGS_OTEL_PYTHON_ENABLED_INSTRUMENTATIONS))
SETTINGS_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS = sorted(set(SETTINGS_OTEL_PYTHON_DISABLED_INSTRUMENTATIONS))

# TODO: This may no longer be needed.
SETTINGS_OTEL_PYTHON_LOG_CORRELATION = ENV_OTEL_PYTHON_LOG_CORRELATION in TRUTHY

SETTINGS_SLS_EXTENSION_LOG_LEVEL = LOG_LEVEL_MAP[
    default_if_none(ENV_SLS_EXTENSION_LOG_LEVEL, DEF_SLS_EXTENSION_LOG_LEVEL).lower()
]

SETTINGS_TEST_DRY_LOG = ENV_TEST_DRY_LOG in TRUTHY
SETTINGS_TEST_DRY_LOG_PRETTY = ENV_TEST_DRY_LOG_PRETTY in TRUTHY


SETTINGS_SLS_EXTENSION_FLUSH_TIMEOUT = (
    int(ENV_SLS_EXTENSION_FLUSH_TIMEOUT) if ENV_SLS_EXTENSION_FLUSH_TIMEOUT else 30000
)
