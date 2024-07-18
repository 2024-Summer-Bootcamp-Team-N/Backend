from django.db import models

class RoomInfo(models.Model):
    room_info = models.TextField()
    price = models.TextField()
    link = models.URLField()
    def __str__(self):
        return self.room_info

