from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.qa import answer_question
from memory import get_history, save_history
from summarizer import summarize_history
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


MAX_HISTORY = 10


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):

    # create session if new user
    session_id = request.session_id or str(uuid.uuid4())

    # load previous conversation
    history = get_history(session_id)

    # add user message
    history.append({
        "role": "user",
        "content": request.question
    })

    # summarize old messages if history too long
    if len(history) > MAX_HISTORY:

        summary = summarize_history(history[:-4])

        history = [
            {
                "role": "system",
                "content": f"Conversation summary: {summary}"
            }
        ] + history[-4:]

    # generate AI response
    result = answer_question(request.question, history)

    # store AI response
    history.append({
        "role": "assistant",
        "content": result
    })

    # save memory
    save_history(session_id, history)

    return {
        "answer": result,
        "session_id": session_id
    }