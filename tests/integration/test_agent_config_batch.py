# ABOUTME: Integration tests for batch_enabled config loading from agents.yaml.
# ABOUTME: Verifies AgentConfig has batch_enabled and get_batch_enabled_agents() works.

from autobots_devtools_shared_lib.dynagent.agents.agent_config_utils import (
    get_batch_enabled_agents,
    load_agents_config,
)


class TestBatchEnabledConfig:
    """Verify batch_enabled field is loaded from agents.yaml."""

    def test_agent_config_has_batch_enabled_attribute(self):
        """AgentConfig dataclass should have batch_enabled field."""
        agents = load_agents_config()
        # Pick any agent and verify the attribute exists
        coordinator = agents.get("coordinator")
        assert coordinator is not None
        assert hasattr(coordinator, "batch_enabled")

    def test_coordinator_is_batch_enabled(self):
        """coordinator should have batch_enabled=True in config."""
        agents = load_agents_config()
        coordinator = agents.get("coordinator")
        assert coordinator is not None
        assert coordinator.batch_enabled is True

    def test_all_five_bro_agents_are_batch_enabled(self):
        """All 5 BRO agents should have batch_enabled=True."""
        agents = load_agents_config()
        expected_batch_agents = {
            "coordinator",
            "preface_agent",
            "getting_started_agent",
            "features_agent",
            "entity_agent",
        }
        for agent_name in expected_batch_agents:
            agent = agents.get(agent_name)
            assert agent is not None, f"Agent {agent_name} not found in config"
            assert agent.batch_enabled is True, f"Agent {agent_name} should be batch_enabled"


class TestGetBatchEnabledAgents:
    """Verify get_batch_enabled_agents() returns correct set."""

    def test_returns_list_of_strings(self):
        """Function should return a list of agent names."""
        result = get_batch_enabled_agents()
        assert isinstance(result, list)
        assert all(isinstance(name, str) for name in result)

    def test_returns_exactly_five_agents(self):
        """Should return exactly 5 batch-enabled agents."""
        result = get_batch_enabled_agents()
        assert len(result) == 5

    def test_contains_all_bro_agents(self):
        """Should contain all expected BRO agents."""
        result = get_batch_enabled_agents()
        expected = {
            "coordinator",
            "preface_agent",
            "getting_started_agent",
            "features_agent",
            "entity_agent",
        }
        assert set(result) == expected

    def test_coordinator_in_result(self):
        """coordinator should be in the batch-enabled list."""
        result = get_batch_enabled_agents()
        assert "coordinator" in result

    def test_all_section_agents_in_result(self):
        """All section agents should be in the batch-enabled list."""
        result = get_batch_enabled_agents()
        section_agents = {
            "preface_agent",
            "getting_started_agent",
            "features_agent",
            "entity_agent",
        }
        assert section_agents.issubset(set(result))
