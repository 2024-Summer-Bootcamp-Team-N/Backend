from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import crawl_latest_url
import logging

logger = logging.getLogger(__name__)

class GenerateAndCrawlView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Celery 태스크 시작 및 결과 대기
            task = crawl_latest_url.delay()
            result = task.get(timeout=300)  # 타임아웃 설정, 필요에 따라 조정

            # 결과 반환
            if 'error' in result:
                return Response({"error": result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"크롤링 작업 중 오류 발생: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)