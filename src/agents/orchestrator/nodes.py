"""LangGraph node functions with SSE event publishing."""

from __future__ import annotations

import time
from typing import Any

from src.agents.bug_detection.agent import BugDetectionAgent
from src.agents.fix.agent import FixAgent
from src.agents.orchestrator.state import PRReviewState
from src.agents.performance.agent import PerformanceAgent
from src.agents.security.agent import SecurityAgent
from src.agents.style.agent import StyleAgent
from src.core.constants import (
    AGENT_BUG,
    AGENT_PERFORMANCE,
    AGENT_SECURITY,
    AGENT_STYLE,
)
from src.core.logging import get_logger
from src.models.review import AgentResult, ReviewStatus

logger = get_logger(__name__)


def _publish_event(review_id: str, event_type: str, data: dict[str, Any]) -> None:
    """Publish SSE event (stub; integration happens in main.py)."""
    logger.debug("sse_event", review_id=review_id, sse_event=event_type, **data)


async def initialize(state: PRReviewState) -> dict[str, Any]:
    """Initialize the review state."""
    return {"status": ReviewStatus.FETCHING, "findings": [], "agent_results": {}, "fix_results": [], "errors": []}


async def fetch_pr(state: PRReviewState) -> dict[str, Any]:
    """Fetch PR metadata (already done, but update status)."""
    return {"status": ReviewStatus.ANALYZING}


async def check_success(state: PRReviewState) -> dict[str, Any]:
    """Check if we have the PR data we need."""
    if not state.get("pr_info") or not state.get("files"):
        return {"status": ReviewStatus.FAILED, "errors": ["Failed to fetch PR data"]}
    return {}


async def analyze_security(state: PRReviewState) -> dict[str, Any]:
    """Run SecurityAgent in parallel."""
    started = time.monotonic()
    agent = SecurityAgent()
    findings = await agent.run(state["files"])
    duration = time.monotonic() - started
    return {
        "findings": findings,
        "agent_results": {
            AGENT_SECURITY: AgentResult(
                agent_name=AGENT_SECURITY,
                status="completed",
                findings=findings,
                duration_seconds=duration,
            ).model_dump()
        },
    }


async def analyze_bug(state: PRReviewState) -> dict[str, Any]:
    """Run BugDetectionAgent in parallel."""
    started = time.monotonic()
    agent = BugDetectionAgent()
    findings = await agent.run(state["files"])
    duration = time.monotonic() - started
    return {
        "findings": findings,
        "agent_results": {
            AGENT_BUG: AgentResult(
                agent_name=AGENT_BUG,
                status="completed",
                findings=findings,
                duration_seconds=duration,
            ).model_dump()
        },
    }


async def analyze_style(state: PRReviewState) -> dict[str, Any]:
    """Run StyleAgent in parallel."""
    started = time.monotonic()
    agent = StyleAgent()
    findings = await agent.run(state["files"])
    duration = time.monotonic() - started
    return {
        "findings": findings,
        "agent_results": {
            AGENT_STYLE: AgentResult(
                agent_name=AGENT_STYLE,
                status="completed",
                findings=findings,
                duration_seconds=duration,
            ).model_dump()
        },
    }


async def analyze_performance(state: PRReviewState) -> dict[str, Any]:
    """Run PerformanceAgent in parallel."""
    started = time.monotonic()
    agent = PerformanceAgent()
    findings = await agent.run(state["files"])
    duration = time.monotonic() - started
    return {
        "findings": findings,
        "agent_results": {
            AGENT_PERFORMANCE: AgentResult(
                agent_name=AGENT_PERFORMANCE,
                status="completed",
                findings=findings,
                duration_seconds=duration,
            ).model_dump()
        },
    }


async def aggregate_findings(state: PRReviewState) -> dict[str, Any]:
    """Sync point after parallel agents; aggregate results."""
    findings = state.get("findings", [])
    return {
        "status": ReviewStatus.FIXING if findings else ReviewStatus.COMPLETED,
    }


async def should_apply_fixes(state: PRReviewState) -> str:
    """Conditional: proceed to fixes if any findings exist."""
    findings = state.get("findings", [])
    if not findings:
        return "skip_fixes"
    return "apply_fixes"


async def apply_fixes(state: PRReviewState) -> dict[str, Any]:
    """Run FixAgent (requires PR info for GitHub API)."""
    pr_info = state["pr_info"]
    findings = state.get("findings", [])
    files = state["files"]

    agent = FixAgent()
    # FixAgent needs GitHub service setup (will be injected in main.py)
    fix_results, _updated_files = await agent.run(
        files, findings, pr_info.owner, pr_info.repo, pr_info.head_branch or "main"
    )
    return {"fix_results": fix_results, "status": ReviewStatus.COMPLETED}


async def finalize(state: PRReviewState) -> dict[str, Any]:
    """Final aggregation and logging."""
    findings = state.get("findings", [])
    fix_results = state.get("fix_results", [])
    logger.info(
        "review_complete",
        pr_number=state["pr_info"].pr_number,
        total_findings=len(findings),
        total_fixes=len([r for r in fix_results if r.get("success")]),
    )
    return {"status": ReviewStatus.COMPLETED}
