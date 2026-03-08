from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.qa import answer_question
from memory import get_history, save_history
from summarizer import summarize_history
import uuid
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
    # 1. Create or retrieve session_id
    session_id = request.session_id or str(uuid.uuid4())

    # 2. Update and store session state
    state = session_states.get(session_id, {})
    state = update_state(state, request.question)
    session_states[session_id] = state

    # 3. Load previous conversation
    history = get_history(session_id)

    # 4. Add user message to history
    history.append({
        "role": "user",
        "content": request.question
    })

    # 5. Summarize old messages if history too long
    if len(history) > MAX_HISTORY:
        summary = summarize_history(history[:-4])
        history = [
            {
                "role": "system",
                "content": f"Conversation summary: {summary}"
            }
        ] + history[-4:]

    # 6. Generate AI response (Passing State to RAG)
    result = answer_question(request.question, history, state)

    # 7. Store AI response and save memory
    history.append({
        "role": "assistant",
        "content": result
    })
    save_history(session_id, history)

    return {
        "answer": result,
        "session_id": session_id
    }