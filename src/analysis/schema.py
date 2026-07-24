"""Canonical experiment-schema definitions shared by all analyses."""

TIME_SERIES_SCHEMA_VERSION = "fgc-ts-v1"
SUMMARY_SCHEMA_VERSION = "fgc-summary-v1"

GLOBAL_TIME_SERIES_COLUMNS = (
    "schema_version",
    "run_id",
    "scenario_id",
    "configuration_id",
    "trial",
    "sample_index",
    "time_s",
    "loop_dt_ms",
    "event",
    "battery_v",
)

EVENT_NAMES = frozenset(
    {
        "LOG_START",
        "START",
        "COMMAND_START",
        "TARGET_REACHED",
        "COMMAND_STOP",
        "STOPPED",
        "MARK",
        "END",
        "ABORT",
        "FAULT",
    }
)

GLOBAL_SUMMARY_COLUMNS = (
    "schema_version",
    "run_id",
    "scenario_id",
    "configuration_id",
    "metric_id",
    "metric_value",
    "metric_unit",
    "aggregation",
    "source",
    "validity",
    "notes",
)
