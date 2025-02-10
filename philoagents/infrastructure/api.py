from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from philoagents.application.conversation_service.generate_response import get_response
from philoagents.domain.philosopher_factory import PhilosopherFactory

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    message: str
    philosopher_id: str


@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        # Create workflow graph
        philosopher_factory = PhilosopherFactory()
        philosopher = philosopher_factory.get_philosopher(chat_message.philosopher_id)

        response = await get_response(
            message=chat_message.message,
            philosopher_id=chat_message.philosopher_id,
            philosopher_name=philosopher.name,
            philosopher_perspective=philosopher.perspective,
            philosopher_style=philosopher.style,
            philosopher_context="",
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
