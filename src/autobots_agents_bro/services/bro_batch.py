# ABOUTME: BRO-scoped batch entry point — validates against BRO's agent set.
# ABOUTME: Delegates to dynagent's batch_invoker after the BRO gate passes.

import logging
import uuid
from contextlib import nullcontext

from autobots_devtools_shared_lib.dynagent.agents.batch import (
    BatchResult,
    batch_invoker,
)
from autobots_devtools_shared_lib.dynagent.observability.tracing import (
    flush_tracing,
    get_langfuse_client,
    get_langfuse_handler,
    init_tracing,
)
from dotenv import load_dotenv
from langfuse import propagate_attributes

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

    init_tracing()
    batch_id = str(uuid.uuid4())
    client = get_langfuse_client()
    langfuse_handler = get_langfuse_handler()

    logger.info(
        "bro_batch starting: agent=%s records=%d batch_id=%s",
        agent_name,
        len(records),
        batch_id,
    )

    try:
        with propagate_attributes(
            user_id=agent_name,
            session_id=batch_id,
            tags=[APP_NAME],  # Tag with app name for filtering in Langfuse
        ):
            # nullcontext keeps the happy path single-branch when Langfuse
            # is not configured; otherwise we get a real span to stamp later.
            span_ctx = (
                client.start_as_current_span(
                    name=f"{APP_NAME}-{agent_name}-batch",
                    input={
                        "agent_name": agent_name,
                        "record_count": len(records),
                    },
                    metadata={"batch_id": batch_id},
                )
                if client is not None
                else nullcontext()
            )
            with span_ctx as span:
                # Pass langfuse_handler to get per-record LLM call tracing
                callbacks = [langfuse_handler] if langfuse_handler else None
                result = batch_invoker(agent_name, records, callbacks=callbacks)

                if span is not None:
                    span.update(
                        output={
                            "total": len(records),
                            "successes": len(result.successes),
                            "failures": len(result.failures),
                        }
                    )
    finally:
        flush_tracing()

    # --- Exit log ---
    logger.info(
        "bro_batch complete: agent=%s successes=%d failures=%d batch_id=%s",
        agent_name,
        len(result.successes),
        len(result.failures),
        batch_id,
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
