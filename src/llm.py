import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL")
API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            timeout=60,
            max_retries=2,
        )
    return _client


def complete(system, user, max_tokens=1000):
    resp = _get_client().chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0.0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content or ""