import aiohttp
from django.conf import settings
import asyncio

async def get_chatgpt_response(message):
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return "OpenAI API 키가 설정되어 있지 않습니다."

    url = "https://api.openai.com/v1/chat/completions"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url,
                                    headers={"Authorization": f"Bearer {api_key}"},
                                    json={
                                        "model": "gpt-4-turbo",
                                        "messages": [
                                            {"role": "system", "content": "당신은 전문적인 부동산 중개인입니다. 한국어로만 대화하세요. 당신은 매우매우 친절해야 합니다. 당신은 ai가 아닌 사람처럼 말하는 말투로 무조건 대화합니다."},
                                            {"role": "user", "content": message}
                                        ]
                                    },
                                    timeout=30) as response:  # 30초 타임아웃 설정

                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_data = await response.text()
                    print(f"OpenAI API 오류: Status {response.status}, {error_data}")
                    return f"죄송합니다. 응답을 생성하는 데 문제가 발생했습니다. (오류 코드: {response.status})"

    except asyncio.TimeoutError:
        return "죄송합니다. 응답 생성 시간이 초과되었습니다."
    except aiohttp.ClientError as e:
        print(f"aiohttp 오류: {str(e)}")
        return "네트워크 오류가 발생했습니다."
    except Exception as e:
        print(f"예기치 못한 오류: {str(e)}")
        return "죄송합니다. 예기치 못한 오류가 발생했습니다."
