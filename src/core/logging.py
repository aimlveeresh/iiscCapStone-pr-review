"""structlog configuration with correlation-id support.

IMPORTANT: never pass `event=` as a kwarg to a bound logger — it is the reserved
positional message key in structlog. Use `sse_event=` (or another name) instead
(Build_from_Scratch.md bug #6).
"""

from __future__ import annotations

import logging
import sys
from contextvars import ContextVar

import structlog

# Correlation id propagated across async tasks via contextvars.
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)

_CONFIGURED = False

# Important log events to show (whitelist)
IMPORTANT_EVENTS = {
    # PR & Review
    "review_created",
    "review_completed",
    "review_failed",
    "review_complete",
    "fetched_pr_data",
    "graph_built",

    # Agents & Analysis
    "agent_run_complete",
    "findings_deduplicated",
    "finding_deduplicated",

    # LLM & Services
    "llm_call",
    "llm_response",

    # Infrastructure
    "chromadb_initialized",
    "chromadb_init_failed",
    "chromadb_not_installed",
    "security_rag_retrieved",
    "security_rag_fallback",
    "ingest_complete",
    "ingest_failed",

    # Fixes & Commits
    "fix_applied",
    "commit_created",
    "finding_fixed",

    # Stages
    "stage_update",

    # Errors & Warnings
    "warning",
    "error",
}


def _filter_important_logs(_logger, _method_name, event_dict):
    """Filter to only show important log events."""
    event_name = event_dict.get("event", "")
    log_level = event_dict.get("level", "INFO").upper()

    # Always show WARNING and ERROR logs
    if log_level in ("WARNING", "ERROR", "CRITICAL"):
        return True

    # Show important INFO logs
    if event_name in IMPORTANT_EVENTS:
        return True

    # Hide everything else (debug, info for unimportant events)
    return False


def set_correlation_id(value: str | None) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def _add_correlation_id(_logger, _method_name, event_dict):
    cid = _correlation_id.get()
    if cid is not None:
        event_dict.setdefault("correlation_id", cid)
    return event_dict


def configure_logging(*, level: str = "INFO", json_logs: bool = False) -> None:
    global _CONFIGURED

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    renderer = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            _add_correlation_id,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.filter_by_level,
            structlog.processors.CallsiteParameterAdder(),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    if not _CONFIGURED:
        configure_logging()
    return structlog.get_logger(name)
