"""Persistent cross-session memory using Dakera MCP.

Demonstrates the three memory tiers discussed in issue #12:
  - Short-term:  mcp-agent Context object (in-process, ephemeral)
  - Session:     Dakera dakera_session_start / dakera_store
  - Long-term:   Dakera dakera_recall (semantic search, decay-weighted)

Prereq:
    docker run -d -p 3000:3000 \\
        -e DAKERA_API_KEY=demo \\
        dakera/dakera:latest
    uvx dakera-mcp  # confirms the MCP server starts

Usage:
    # First run: research and store
    DAKERA_API_URL=http://localhost:3000 DAKERA_API_KEY=demo python main.py

    # Second run: notice the agent recalls prior findings from Dakera
    DAKERA_API_URL=http://localhost:3000 DAKERA_API_KEY=demo python main.py
"""

import asyncio
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM

app = MCPApp(name="persistent_memory_agent")


async def research_phase() -> None:
    """Phase 1: Research a topic and persist findings to Dakera.

    The agent explicitly uses dakera_store to save each key finding.
    These memories persist across process restarts.
    """
    async with app.run() as mcp_app:
        agent = Agent(
            name="researcher",
            instruction="""You are a research assistant with persistent memory.

When you discover important information, store it immediately using dakera_store
with a clear, self-contained summary. Use dakera_session_start at the beginning
of each session and dakera_session_end when done.

Start by calling dakera_recall with query "prior research findings" to check
what you already know before starting new research.""",
            server_names=["dakera", "fetch"],
        )

        async with agent:
            llm = await agent.attach_llm(AnthropicAugmentedLLM)
            result = await llm.generate_str(
                "Research the current state of multi-agent AI frameworks in 2025. "
                "Find the top 3 frameworks by adoption and their key architectural differences. "
                "Store each finding as a separate memory entry using dakera_store.",
            )
            print(f"[Phase 1 — Research complete]\n{result[:500]}...\n")


async def recall_phase() -> None:
    """Phase 2: A fresh agent recalls what Phase 1 stored.

    This simulates a new process / container restart. The agent has no
    in-process state from Phase 1 but can recall via Dakera.
    """
    async with app.run() as mcp_app:
        agent = Agent(
            name="analyst",
            instruction="""You are an analyst with access to persistent memory.

Always start by calling dakera_recall to retrieve relevant prior knowledge
before answering. Your analysis should build on what was previously stored.""",
            server_names=["dakera"],
        )

        async with agent:
            llm = await agent.attach_llm(AnthropicAugmentedLLM)
            result = await llm.generate_str(
                "Based on prior research about multi-agent AI frameworks, "
                "which framework would you recommend for a production enterprise deployment "
                "and why? Use dakera_recall to check prior findings first.",
            )
            print(f"[Phase 2 — Recall + Analysis]\n{result}")


async def main() -> None:
    print("=== Phase 1: Research (storing to Dakera) ===\n")
    await research_phase()

    print("\n--- Simulating new agent session (process restart equivalent) ---\n")
    print("=== Phase 2: Recall (reading from Dakera) ===\n")
    await recall_phase()


if __name__ == "__main__":
    asyncio.run(main())
