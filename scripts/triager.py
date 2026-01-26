import asyncio
import re
from pathlib import Path

import yaml
from copilot import CopilotClient, SessionConfig
from copilot.generated.session_events import SessionEvent, SessionEventType
from copilot.types import (
    CopilotClientOptions,
    CustomAgentConfig,
    MCPRemoteServerConfig,
    MessageOptions,
)


def parse_agent_file(file_path: Path) -> dict:
    """Parse an .agent.md file, extracting YAML frontmatter and markdown content."""
    content = file_path.read_text()

    # Match YAML frontmatter between --- delimiters
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not frontmatter_match:
        return {"prompt": content, "tools": []}

    frontmatter_yaml = frontmatter_match.group(1)
    markdown_content = frontmatter_match.group(2).strip()

    frontmatter = yaml.safe_load(frontmatter_yaml)

    # Transform tool names from 'namespace/tool' to 'namespace_tool' format
    tools = frontmatter.get("tools", [])
    transformed_tools = [tool.replace("/", "_") for tool in tools]

    return {
        "description": frontmatter.get("description"),
        "tools": transformed_tools,
        "prompt": markdown_content,
    }


async def main():
    options = CopilotClientOptions(
        log_level="info",
    )
    client = CopilotClient(options=options)
    await client.start()

    prompt = "Find a stale issue to triage."
    print(f"[INFO] Asking Copilot: {prompt}")

    # Load and parse the triager agent definition from file
    agent_file = Path(__file__).parent.parent / ".github" / "agents" / "triager.agent.md"
    agent_config = parse_agent_file(agent_file)

    session_config = SessionConfig(
        model="claude-sonnet-4.5",
        custom_agents=[
            CustomAgentConfig(
                name="triager",
                description=agent_config.get("description", ""),
                # tools=agent_config.get("tools", []), # question: how do these need to be namespaced for MCP servers?
                tools=["*"],
                prompt=agent_config["prompt"],
                mcp_servers={
                    # GitHub MCP server for github/* tools
                    "github": MCPRemoteServerConfig(
                        type="http",
                        url="https://api.githubcopilot.com/mcp/",
                        tools=["*"],
                    ),
                    # Azure/Microsoft Learn MCP server for azure-mcp/* tools
                    "azure-mcp": MCPRemoteServerConfig(
                        type="http",
                        url="https://learn.microsoft.com/api/mcp",
                        tools=["*"],
                    ),
                },
            )
        ],
    )

    session = await client.create_session(config=session_config)

    # Set up event handling
    def handle_event(event: SessionEvent):
        if event.type == SessionEventType.ASSISTANT_MESSAGE:
            print(f"\n🤖 {event.data.content}\n")
        elif event.type == SessionEventType.TOOL_EXECUTION_START:
            print(f"  ⚙️  {event.data.tool_name}")

    session.on(handle_event)

    message_options = MessageOptions(prompt=prompt)
    await session.send_and_wait(options=message_options, timeout=300.0)

    # Interactive loop
    print('\n💡 Ask follow-up questions or type "exit" to quit.\n')
    print()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        if user_input:
            message_options = MessageOptions(prompt=user_input)
            await session.send_and_wait(options=message_options, timeout=300.0)

    await session.destroy()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
