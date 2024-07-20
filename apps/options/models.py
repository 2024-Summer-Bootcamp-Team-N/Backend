from django.db import models

class RoomInfo(models.Model):
    room_info = models.TextField()
    price = models.TextField()
    link = models.URLField()
    def __str__(self):
        return self.room_info

class RoomDetailInfo(models.Model):
    room = models.OneToOneField(RoomInfo, on_delete=models.CASCADE, related_name='details')
    location = models.TextField()
    exclusive_overall_area = models.TextField()
    maintenance_fee = models.TextField()
    room_type = models.TextField()
    num_rooms_bathrooms = models.TextField()
    floor_building_floors = models.TextField()
    direction = models.TextField()
    parking_availability = models.TextField()
    total_parking_spaces = models.TextField()
    heating_type = models.TextField()
    building_use = models.TextField()  # 건축물용도
    move_in_date = models.TextField()
    approval_date = models.TextField()
    initial_registration_date = models.TextField()
    image_url = models.URLField()