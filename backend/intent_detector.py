from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def detect_intent(question: str):

    prompt = f"""
You are classifying a student's intent for a university helpdesk.

Possible intents:
- admission
- fees
- course_information
- location
- hostel
- placement
- greeting
- general

User question:
{question}

Return ONLY the intent name.
"""

    response = llm.invoke(prompt)

    return response.content.strip().lower()