import streamlit as st
from langchain_core.messages import AIMessageChunk

try:
    from openrouter.errors.badrequestresponse_error import BadRequestResponseError
    from openrouter.errors.toomanyrequestsresponse_error import TooManyRequestsResponseError
except ImportError:
    BadRequestResponseError = Exception
    TooManyRequestsResponseError = Exception

from agent_tools import agent

st.title("✈️ AI Flight Tracker")

question = st.text_input(
    "Ask about a flight",
    placeholder="Example: What is the status of IGO1045?"
)

if st.button("Track Flight"):

    if question:

        try:

            def response_stream():
                """Yields text tokens from the agent's streamed response."""
                for chunk, metadata in agent.stream(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": question
                            }
                        ]
                    },
                    stream_mode="messages",
                ):
                    # Only yield content from AI message chunks that belong
                    # to the final model response (not tool-call steps).
                    if (
                        isinstance(chunk, AIMessageChunk)
                        and chunk.content
                        and not chunk.tool_calls
                        and not chunk.tool_call_chunks
                    ):
                        yield chunk.content

            st.write_stream(response_stream())

        except BadRequestResponseError as e:
            st.error(f"OpenRouter Bad Request error: {str(e)}")
        except TooManyRequestsResponseError as e:
            st.error(f"OpenRouter rate limit exceeded: {str(e)}")