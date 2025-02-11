from langchain_core.messages import HumanMessage
from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver

from philoagents.application.conversation_service.workflow.graph import (
    create_workflow_graph,
)
from philoagents.settings import settings


async def get_response(
    message: str,
    philosopher_id: str,
    philosopher_name: str,
    philosopher_perspective: str,
    philosopher_style: str,
    philosopher_context: str,
) -> str:
    """
    Run a conversation through the workflow graph.

    Args:
        message: Initial message to start the conversation
        philosopher_name: Name of the philosopher
        philosopher_perspective: Philosopher's perspective on the topic
        philosopher_style: Style of conversation (e.g., "Socratic")
        philosopher_context: Additional context about the philosopher

    Returns:
        PhilosopherState: The final state after running the workflow
    """
    graph_builder = create_workflow_graph()

    try:
        async with AsyncMongoDBSaver.from_conn_string(
            conn_string=settings.MONGO_URI,
            db_name=settings.MONGO_DB_NAME,
            checkpoint_collection_name=settings.MONGO_STATE_CHECKPOINT_COLLECTION,
            writes_collection_name=settings.MONGO_STATE_WRITES_COLLECTION,
        ) as checkpointer:
            graph = graph_builder.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": philosopher_id}}
            output_state = await graph.ainvoke(
                {
                    "messages": [HumanMessage(content=message)],
                    "philosopher_name": philosopher_name,
                    "philosopher_perspective": philosopher_perspective,
                    "philosopher_style": philosopher_style,
                    "philosopher_context": philosopher_context,
                },
                config,
            )
        last_message = output_state["messages"][-1]
        return last_message.content
    except Exception as e:
        raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e
