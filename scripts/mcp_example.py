import asyncio

from copilot import CopilotClient, SessionConfig
from copilot.generated.session_events import SessionEvent, SessionEventType
from copilot.types import CopilotClientOptions, MCPRemoteServerConfig, MessageOptions


async def main():
    options = CopilotClientOptions(
        log_level="info",
    )
    client = CopilotClient(options=options)
    await client.start()

    prompt = "Check README.md and make sure that the information about Azure AI Search is correct per the current documentation."
    print(f"[INFO] Asking Copilot: {prompt}")

    session_config = SessionConfig(
        model="claude-sonnet-4.5",
        mcp_servers={
            # Microsoft Learn MCP server (remote)
            "microsoft-learn": MCPRemoteServerConfig(
                type="http", url="https://learn.microsoft.com/api/mcp", tools=["*"]
            )
        },
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
    response = await session.send_and_wait(options=message_options, timeout=300.0)
    print(response.data.content)

    await session.destroy()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
