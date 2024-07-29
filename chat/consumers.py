import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .chatgpt import get_chatgpt_response
from asgiref.sync import sync_to_async
import asyncio
import uuid

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = str(uuid.uuid4())  # 고유한 세션 ID 생성
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        try:
            # 타임아웃 설정 (60초)
            response = await asyncio.wait_for(get_chatgpt_response(message, self.session_id), timeout=60.0)
        except asyncio.TimeoutError:
            response = "죄송합니다. 응답 시간이 초과되었습니다."
        except Exception as e:
            response = f"오류가 발생했습니다: {str(e)}"

        await self.send(text_data=json.dumps({
            'message': response
        }))

    @sync_to_async
    def get_db_info(self):
        # 여기에 데이터베이스 쿼리 로직을 구현합니다.
        # 예: return RoomInfo.objects.all()[:5]
        pass