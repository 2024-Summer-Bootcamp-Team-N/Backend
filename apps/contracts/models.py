from django.db import models
from django.conf import settings

class LatestRoomInfo(models.Model):
    location = models.CharField(max_length=255, verbose_name="방 위치")
    exclusive_overall_area = models.CharField(max_length=50, verbose_name="전용면적")
    building_use = models.CharField(max_length=100, verbose_name="건물 용도")
    latest_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="최근 사용자")
    deposit = models.CharField(max_length=50, verbose_name="보증금", null=True, blank=True)
    monthly_rent = models.CharField(max_length=50, verbose_name="월세", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시간")

    class Meta:
        verbose_name = "최근 방 정보"
        verbose_name_plural = "최근 방 정보 목록"
        ordering = ['-created_at']  # 생성 시간 기준으로 내림차순 정렬

    def __str__(self):
        return f"{self.location} - {self.latest_user.username if self.latest_user else '사용자 없음'}"

