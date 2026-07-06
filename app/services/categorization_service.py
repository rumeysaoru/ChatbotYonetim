import json
import time

from google import genai
from google.genai import types

from app.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def categorize_entry(content: str, existing_categories: list[str]) -> dict:
    client = _get_client()

    category_list_text = (
        ", ".join(existing_categories)
        if existing_categories
        else "(henüz hiç kategori yok)"
    )

    prompt = f"""Sen bir üniversite veri giriş sisteminde kategori sınıflandırma asistanısın.

Mevcut kategoriler:
{category_list_text}

Metin:
"{content}"

Görev:
- Eğer metin mevcut kategorilerden birine uyuyorsa sadece "matched_category" doldur.
- Eğer uymuyorsa kısa (maks 3 kelime) yeni kategori öner ve "suggested_new_category" doldur.
- İkisini aynı anda doldurma.

Sadece JSON döndür:
{{"matched_category": null, "suggested_new_category": null}}"""

    max_retries = 3
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )

            result = json.loads(response.text)

            print("AI SONUCU:", result)

            return {
                "matched_category": result.get("matched_category"),
                "suggested_new_category": result.get("suggested_new_category"),
            }

        except Exception as e:
            last_error = e
            print(f"AI HATA (deneme {attempt + 1}):", e)

            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))

    print("AI TÜM DENEMELER BAŞARISIZ:", last_error)

    return {
        "matched_category": None,
        "suggested_new_category": None,
    }