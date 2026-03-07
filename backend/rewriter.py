from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def rewrite_query(question, history):

    # build short conversation context
    chat_context = ""
    for msg in history[-4:]:
        chat_context += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
You are a query rewriting assistant for a university chatbot.

Conversation history:
{chat_context}

User question:
{question}

Rewrite the user's question so it becomes a clear standalone search query.
Do not answer the question. Only rewrite it.

Rewritten query:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You rewrite questions for better database search."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()