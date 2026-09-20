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

if "messages" not in st.session_state: 
    st.session_state.messages = []

for msg in st.session_state.messages: 
    with st.chat_message(msg["role"]): 
        st.write(msg["content"])

if question := st.chat_input("Ask about a flight"): 
    st.session_state.messages.append({"role":"user","content":question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"): 
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

            full_response = st.write_stream(response_stream())
            st.session_state.messages.append({"role":"assistant", "content":full_response})

        except BadRequestResponseError as e:
            st.error(f"OpenRouter Bad Request error: {str(e)}")
        except TooManyRequestsResponseError as e:
            st.error(f"OpenRouter rate limit exceeded: {str(e)}")