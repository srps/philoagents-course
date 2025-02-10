from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from philoagents.application.conversation_service.workflow.edges import (
    should_summarize_conversation,
)

from philoagents.application.conversation_service.workflow.nodes import (
    conversation_node,
    summarize_conversation_node,
)
from philoagents.application.conversation_service.workflow.state import PhilosopherState


@lru_cache(maxsize=1)
def create_workflow_graph():
    graph_builder = StateGraph(PhilosopherState)

    # Add all nodes
    graph_builder.add_node("conversation_node", conversation_node)
    graph_builder.add_node("summarize_conversation_node", summarize_conversation_node)

    # Define the flow
    graph_builder.add_edge(START, "conversation_node")

    # Check for summarization after any response
    graph_builder.add_conditional_edges(
        "conversation_node", should_summarize_conversation
    )
    graph_builder.add_edge("summarize_conversation_node", END)

    return graph_builder


# import asyncio
# from langchain_core.messages import HumanMessage

# async def run_conversation(
#     message: str,
#     philosopher_name: str,
#     philosopher_perspective: str,
#     philosopher_style: str,
#     philosopher_context: str
# ) -> PhilosopherState:
#     """
#     Run a conversation through the workflow graph.

#     Args:
#         message: Initial message to start the conversation
#         philosopher_name: Name of the philosopher
#         philosopher_perspective: Philosopher's perspective on the topic
#         philosopher_style: Style of conversation (e.g., "Socratic")
#         philosopher_context: Additional context about the philosopher

#     Returns:
#         PhilosopherState: The final state after running the workflow
#     """
#     graph_builder = create_workflow_graph()
#     graph = graph_builder.compile()

#     try:
#         output_state = await graph.ainvoke({
#             "messages": [HumanMessage(content=message)],
#             "philosopher_name": philosopher_name,
#             "philosopher_perspective": philosopher_perspective,
#             "philosopher_style": philosopher_style,
#             "philosopher_context": philosopher_context
#         })
#         return output_state
#     except Exception as e:
#         raise RuntimeError(f"Error running conversation workflow: {str(e)}") from e

# async def main():
#     state = await run_conversation(
#         message="Hello, how are you?",
#         philosopher_name="Socrates",
#         philosopher_perspective="AI is a tool for good",
#         philosopher_style="Socratic, inquisitive, probing, persistent",
#         philosopher_context="Socrates is a philosopher who is known for his Socratic method."
#     )
#     print(state)

# if __name__ == "__main__":
#     asyncio.run(main())
