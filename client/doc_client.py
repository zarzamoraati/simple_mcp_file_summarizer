import asyncio
import os
import sys
from google import genai
from google.genai.types import Content, FunctionDeclaration, GenerateContentConfig, Part, Tool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Google Gemini client
client = genai.Client(api_key=os.getenv("GOOGLE_API_TOKEN"))
file_path=os.getenv("FILE_PATH")


async def run_client(server_script: str):
    # Configure MCP server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            # List available tools
            mcp_tools = await session.list_tools()
            tools = [
                Tool(
                    function_declarations=[
                        FunctionDeclaration(
                            name=tool.name,
                            description=tool.description,
                            parameters={
                                k: v for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        )
                    ]
                )
                for tool in mcp_tools.tools
            ]

            # Define the prompt
            prompt = (
                "Please summarize the content of the document located at "
                f"'{file_path}'. "
                "Use the available tool to retrieve the document content and provide a concise summary."
            )

            # Send request to Gemini with tools
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[Content(role="user", parts=[Part.from_text(text=prompt)])],
                config=GenerateContentConfig(temperature=0, tools=tools),
            )

            # Handle function call
            if response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                result = await session.call_tool(function_call.name, function_call.args)
                content = result.content[0].text if result.content else "No content returned."

                # Send tool result back to Gemini for summarization
                history = [
                    Content(role="user", parts=[Part.from_text(text=prompt)]),
                    response.candidates[0].content,
                    Content(
                        role="tool",
                        parts=[Part.from_function_response(
                            name=function_call.name,
                            response={"result": content}
                        )]
                    )
                ]
                final_response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=history,
                    config=GenerateContentConfig(temperature=0, tools=tools),
                )
                print("Summary:", final_response.text)
            else:
                print("No function call found:", response.text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python doc_client.py <path_to_server_script>")
        sys.exit(1)
    asyncio.run(run_client(sys.argv[1]))