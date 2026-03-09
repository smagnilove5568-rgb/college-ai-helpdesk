from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.qa import answer_question
from memory import get_history, save_history
from summarizer import summarize_history
import uuid
# Updated imports
from intent_detector import detect_intent
from state_manager import update_state

# Global session storage
session_states = {}

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

    session_id = request.session_id or str(uuid.uuid4())

    history = get_history(session_id)

    # detect intent
    intent = detect_intent(request.question)

    # load conversation state
    state = {}
    if history and "state" in history[0]:
        state = history[0]["state"]

    # update state
    state = update_state(state, intent, request.question)

    # greeting handling
    if intent == "greeting":
        return {
            "answer": "Hello! 👋 I'm the SAGE University assistant. How can I help you today?",
            "session_id": session_id
        }

    # admission clarification
    if intent == "admission" and "program" not in state:
        return {
            "answer": "Sure! Which program are you interested in? (BCA, BTech, MBA, etc.)",
            "session_id": session_id
        }

    # store user message
    history.append({
        "role": "user",
        "content": request.question
    })

    # summarize if history too long
    if len(history) > MAX_HISTORY:

        summary = summarize_history(history[:-4])

        history = [
            {
                "role": "system",
                "content": f"Conversation summary: {summary}",
                "state": state
            }
        ] + history[-4:]

    # generate answer from RAG
    result = answer_question(request.question, history)

    history.append({
        "role": "assistant",
        "content": result
    })

    save_history(session_id, history)

    return {
        "answer": result,
        "session_id": session_id
    }