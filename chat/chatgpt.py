# Backend/chat/chatgpt.py

import aiohttp
from django.conf import settings


async def get_chatgpt_response(message):
    api_key = settings.OPENAI_API_KEY
    url = "https://api.openai.com/v1/chat/completions"

    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                headers={"Authorization": f"Bearer {api_key}"},
                                json={
                                    "model": "gpt-3.5-turbo",
                                    "messages": [{"role": "user", "content": message}]
                                }) as response:

            if response.status == 200:
                data = await response.json()
                return data['choices'][0]['message']['content']
            else:
                return "죄송합니다. 응답을 생성하는 데 문제가 발생했습니다."