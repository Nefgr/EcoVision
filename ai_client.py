import streamlit as st
import json
from google import genai
from google.genai import types

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Инструкция для AI: что именно мы хотим получить
PROMPT = """
Посмотри на фотографию и определи, что за отход на ней изображён.

Ответь СТРОГО в формате JSON, без лишнего текста, без markdown-обёртки, вот так:

{
  "object_name": "название объекта на русском языке",
  "category_code": "один из: plastic, glass, paper, metal, organic, e-waste, battery, mixed",
  "confidence": число от 0 до 1,
  "status": "один из: ok, low_confidence, unclear_image, multiple_objects"
}

Правила:
- если фото нечёткое или объект не разобрать — status = "unclear_image"
- если на фото несколько разных отходов — status = "multiple_objects"
- если ты не уверен в объекте (уверенность ниже 0.5) — status = "low_confidence"
- если всё понятно — status = "ok"
- category_code выбирай максимально близко к материалу объекта
- не пиши ничего, кроме JSON
"""

def analyze_image(image_bytes: bytes, mime_type: str) -> dict:
    """
    Отправляет изображение в Gemini и возвращает разобранный результат.
    image_bytes — сырые байты фото
    mime_type — например "image/jpeg" или "image/png"
    """
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                PROMPT
            ]
        )

        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            raw_text = raw_text.replace("json", "", 1).strip()

        result = json.loads(raw_text)
        result["raw_ai_text"] = raw_text
        return result

    except json.JSONDecodeError:
        return {
            "object_name": "неизвестно",
            "category_code": "mixed",
            "confidence": 0,
            "status": "unclear_image",
            "raw_ai_text": raw_text
        }

    except Exception as e:
        print(f"OSHIBKA AI: {e}")
        return {
            "object_name": "ошибка",
            "category_code": "mixed",
            "confidence": 0,
            "status": "error",
            "raw_ai_text": str(e)
        }