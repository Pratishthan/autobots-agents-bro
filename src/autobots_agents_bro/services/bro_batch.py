# ABOUTME: BRO-scoped batch entry point — validates against BRO's agent set.
# ABOUTME: Delegates to dynagent's batch_invoker after the BRO gate passes.

import logging

from autobots_devtools_shared_lib.dynagent.agents.batch import (
    BatchResult,
    batch_invoker,
)
from autobots_devtools_shared_lib.dynagent.observability.tracing import init_tracing
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# Application name for tracing and identification
APP_NAME = "bro_batch"


def _get_bro_batch_agents() -> list[str]:
    """Load batch-enabled agents from agents.yaml."""
    from autobots_devtools_shared_lib.dynagent.agents.agent_config_utils import (
        get_batch_enabled_agents,
    )

    return get_batch_enabled_agents()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def bro_batch(agent_name: str, records: list[str]) -> BatchResult:
    """Run a batch through dynagent, gated to BRO batch-enabled agents only.

    Args:
        agent_name: Must be a batch-enabled agent from agents.yaml.
        records:    Non-empty list of plain-string prompts.

    Returns:
        BatchResult forwarded from batch_invoker.

    Raises:
        ValueError: If agent_name is not batch-enabled or records is empty.
    """
    bro_agents = _get_bro_batch_agents()

    if agent_name not in bro_agents:
        raise ValueError(
            f"Agent '{agent_name}' is not enabled for batch processing. "
            f"Valid batch-enabled agents: {', '.join(bro_agents)}"
        )

    if not records:
        raise ValueError("records must not be empty")

    # Initialize tracing (one-time singleton)
    init_tracing()

    # BRO entry logging
    logger.info(
        "bro_batch starting: agent=%s records=%d",
        agent_name,
        len(records),
    )

    # Delegate to batch_invoker with BRO metadata
    result = batch_invoker(
        agent_name,
        records,
        enable_tracing=True,
        trace_metadata={
            "app_name": APP_NAME,  # Preserves span name: "bro_batch-{agent_name}-batch"
            "user_id": agent_name,
            "tags": [APP_NAME],
        },
    )

    # BRO exit logging
    logger.info(
        "bro_batch complete: agent=%s successes=%d failures=%d",
        agent_name,
        len(result.successes),
        len(result.failures),
    )

    return result


# ---------------------------------------------------------------------------
# Manual smoke runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from autobots_agents_bro.agents.bro_tools import register_bro_tools

    register_bro_tools()

    smoke_prompts = [
        "What is a Component Vision Document and how do I create one?",
        "Walk me through the preface section of a vision document.",
        "What agents are available in this system?",
    ]

    batch_result = bro_batch("coordinator", smoke_prompts)
    for record in batch_result.results:
        if record.success:
            print(f"Record {record.index} succeeded:\n{record.output}\n")
        else:
            print(f"Record {record.index} failed:\n{record.error}\n")
