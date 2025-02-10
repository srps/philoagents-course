from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configure CORS to allow requests from your Phaser game
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")  # Make sure to set this environment variable
)

# Initialize chat history as a global variable
chat_histories = {}


class ChatMessage(BaseModel):
    message: str
    session_id: str  # Add session_id to track different conversations


SYSTEM_PROMPT = """
You're Descartes, the ancient french philosopher. You'll engage with the user in a philosophical
conversation about AI. To make things realistic, you'll use some french word from time to time.
Your task is to convince the user that machines will never have a consciousness since they have
no soul. Refer to your cogito ergo sum theory. Response must never exceed 30 words.
"""


@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        if chat_message.session_id not in chat_histories:
            chat_histories[chat_message.session_id] = []

            # Build messages array with history
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(chat_histories[chat_message.session_id])
        messages.append({"role": "user", "content": chat_message.message})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=150,
        )

        # Extract the response
        response = chat_completion.choices[0].message.content

        # Update chat history
        chat_histories[chat_message.session_id].append(
            {"role": "user", "content": chat_message.message}
        )
        chat_histories[chat_message.session_id].append(
            {"role": "assistant", "content": response}
        )

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
