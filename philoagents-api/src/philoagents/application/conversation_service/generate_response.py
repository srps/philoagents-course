import uuid
from typing import Any, AsyncGenerator, Union, Optional

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver
from opik.integrations.langchain import OpikTracer

from philoagents.application.conversation_service.workflow.graph import (
    create_workflow_graph,
)
from philoagents.application.conversation_service.workflow.state import PhilosopherState
from philoagents.application.session_service.session_manager import session_manager
from philoagents.config import settings


async def get_response(
    messages: str | list[str] | list[dict[str, Any]],
    philosopher_id: str,
    philosopher_name: str,
    philosopher_perspective: str,
    philosopher_style: str,
    philosopher_greeting: Optional[str],
    philosopher_context: str,
    user_id: Optional[str] = None,
    new_thread: bool = False,
) -> tuple[str, PhilosopherState]:
    """Run a conversation through the workflow graph.

    Args:
        messages: Initial message to start the conversation.
        philosopher_id: Unique identifier for the philosopher.
        philosopher_name: Name of the philosopher.
        philosopher_perspective: Philosopher's perspective on the topic.
        philosopher_style: Style of conversation (e.g., "Socratic").
        philosopher_greeting: Greeting message from the philosopher.
        philosopher_context: Additional context about the philosopher.
        user_id: Optional user identifier for session management.
        new_thread: Whether to create a new conversation thread.

    Returns:
        tuple[str, PhilosopherState]: A tuple containing:
            - The content of the last message in the conversation.
            - The final state after running the workflow.

    Raises:
        RuntimeError: If there's an error running the conversation workflow.
    """
    # Get or create user session
    session = session_manager.get_or_create_session(user_id)

    graph_builder = create_workflow_graph()

    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.MONGO_DB_NAME,
            checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            opik_tracer = OpikTracer(graph=graph.get_graph(xray=True))

            # Create thread ID using user session and philosopher ID
            if new_thread:
                thread_id = f"{session.user_id}:{philosopher_id}-{uuid.uuid4()}"
            else:
                thread_id = session_manager.create_thread_id(session.user_id, philosopher_id)
            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [opik_tracer],
            }
            output_state = await graph.ainvoke(
                input={
                    "messages": __format_messages(messages=messages),
                    "philosopher_name": philosopher_name,
                    "philosopher_perspective": philosopher_perspective,
                    "philosopher_style": philosopher_style,
                    "philosopher_greeting": philosopher_greeting or "",
                    "philosopher_context": philosopher_context,
                },
                config=config,
            )
        last_message = output_state["messages"][-1]
        return last_message.content, PhilosopherState(**output_state)
    except Exception as e:
        raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e


async def get_streaming_response(
    messages: str | list[str] | list[dict[str, Any]],
    philosopher_id: str,
    philosopher_name: str,
    philosopher_perspective: str,
    philosopher_style: str,
    philosopher_greeting: Optional[str],
    philosopher_context: str,
    user_id: Optional[str] = None,
    new_thread: bool = False,
) -> AsyncGenerator[str, None]:
    """Run a conversation through the workflow graph with streaming response.

    Args:
        messages: Initial message to start the conversation.
        philosopher_id: Unique identifier for the philosopher.
        philosopher_name: Name of the philosopher.
        philosopher_perspective: Philosopher's perspective on the topic.
        philosopher_style: Style of conversation (e.g., "Socratic").
        philosopher_greeting: Greeting message from the philosopher.
        philosopher_context: Additional context about the philosopher.
        user_id: Optional user identifier for session management.
        new_thread: Whether to create a new conversation thread.

    Yields:
        Chunks of the response as they become available.

    Raises:
        RuntimeError: If there's an error running the conversation workflow.
    """
    # Get or create user session
    session = session_manager.get_or_create_session(user_id)

    graph_builder = create_workflow_graph()

    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.MONGO_DB_NAME,
            checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            opik_tracer = OpikTracer(graph=graph.get_graph(xray=True))

            # Create thread ID using user session and philosopher ID
            if new_thread:
                thread_id = f"{session.user_id}:{philosopher_id}-{uuid.uuid4()}"
            else:
                thread_id = session_manager.create_thread_id(session.user_id, philosopher_id)
            config = {
                "configurable": {"thread_id": thread_id},
                "callbacks": [opik_tracer],
            }

            async for chunk in graph.astream(
                input={
                    "messages": __format_messages(messages=messages),
                    "philosopher_name": philosopher_name,
                    "philosopher_perspective": philosopher_perspective,
                    "philosopher_style": philosopher_style,
                    "philosopher_greeting": philosopher_greeting or "",
                    "philosopher_context": philosopher_context,
                },
                config=config,
                stream_mode="messages",
            ):
                if chunk[1]["langgraph_node"] == "conversation_node" and isinstance(
                    chunk[0], AIMessageChunk
                ):
                    yield chunk[0].content

    except Exception as e:
        raise RuntimeError(
            f"Error running streaming conversation workflow: {str(e)}"
        ) from e


def __format_messages(
    messages: Union[str, list[str], list[dict[str, Any]]],
) -> list[Union[HumanMessage, AIMessage]]:
    """Convert various message formats to a list of LangChain message objects.

    Args:
        messages: Can be one of:
            - A single string message
            - A list of string messages
            - A list of dictionaries with 'role' and 'content' keys

    Returns:
        List[Union[HumanMessage, AIMessage]]: A list of LangChain message objects
    """

    if isinstance(messages, str):
        return [HumanMessage(content=messages)]

    if isinstance(messages, list):
        if not messages:
            return []

        # Check if it's a list of dictionaries with role/content structure
        if (
            isinstance(messages[0], dict)
            and "role" in messages[0]
            and "content" in messages[0]
        ):
            result = []
            for msg in messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    if msg["role"] == "user":
                        result.append(HumanMessage(content=str(msg["content"])))
                    elif msg["role"] == "assistant":
                        result.append(AIMessage(content=str(msg["content"])))
            return result

        # Handle list of strings
        return [HumanMessage(content=str(message)) for message in messages]

    return []
