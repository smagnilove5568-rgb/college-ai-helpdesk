from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI


def detect_intent(question: str):

    prompt = f"""
Classify the user's intent.

User message:
{question}

Possible intents:
- greeting
- admission
- fee_query
- program_info
- university_info
- facilities
- placement
- unknown

Return only the intent name.
"""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = llm.invoke(prompt)

    return response.content.strip().lower()