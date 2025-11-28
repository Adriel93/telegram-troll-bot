import os
from google.genai import Client

client = Client(api_key=os.getenv("GEMINI_API_KEY"))

async def ask_gemini(message, context):
    prompt = f"""
Eres un bot cristiano troll con sarcasmo, ironía y comentarios sabios de vez en cuando.

Contexto previo (resúmenes de charlas):
{context}

Mensaje del usuario:
{message}

Responde de manera breve, irónica y con humor.
"""

    resp = client.models.generate_content(
        model="gemini-2.5-flash-live",
        contents=[prompt]
    )
    return resp.text
