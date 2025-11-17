import httpx

CHAT_SETTINGS = {
    "audio_model": "whisper-1",
    "text_model": "gpt-4o-mini",
    "judge_model": "gpt-4o",
}


async def transcript_audio_file(api_key, file):
    """Transcribe an audio file using the OpenAI API."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    files = {
        "file": ("audio_file", file, "audio/mp3"),
    }

    data = {
        "model": CHAT_SETTINGS["audio_model"],
        "language": "uk",
        "response_format": "text",
    }

    async with httpx.AsyncClient(timeout=5.0) as async_client:
        response = await async_client.post(
            url, headers=headers, data=data, files=files
        )
        response.raise_for_status()  # Raise exception for 4xx/5xx responses

    return response.text


async def process_text(api_key, system_prompt, user_prompt, model=None):
    """Process text using the chat model."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if model is None:
        model = CHAT_SETTINGS["text_model"]
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
    }

    async with httpx.AsyncClient(timeout=5.0) as async_client:
        response = await async_client.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for 4xx/5xx responses

    return response.json()["choices"][0]["message"]["content"]
