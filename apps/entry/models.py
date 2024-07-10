from django.db import models

class Regions(models.Model):
    province = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    street = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.province} {self.district} {self.street}"

class Residences(models.Model):
    apartment = models.BooleanField(default=False)
    officetel = models.BooleanField(default=False)
    house = models.BooleanField(default=False)
    onetwo = models.BooleanField(default=False)

class Types(models.Model):
    LEASE = models.BooleanField(default=False)
    MONTHLY_RENT = models.BooleanField(default=False)
    depositRangeMax = models.CharField(max_length=20, default="0")
    priceRangeMax = models.CharField(max_length=20, default="0")



class Options(models.Model):
    class ParkingChoices(models.IntegerChoices):
        NO_PREFERENCE = 0, '상관없음'
        ONE_OR_MORE = 1, '1대 이상'
        TWO_OR_MORE = 2, '2대 이상'

    class RoomChoices(models.IntegerChoices):
        NO_PREFERENCE = 0, '상관없음'
        ONE = 1, '1개'
        TWO = 2, '2개'
        THREE = 3, '3개'
        FOUR_OR_MORE = 4, '4개 이상'

    canParking = models.BooleanField(default=False)
    hasElevator = models.BooleanField(default=False)
    parkingNumRangeMin = models.IntegerField(choices=ParkingChoices.choices, default=ParkingChoices.NO_PREFERENCE)
    roomCount = models.IntegerField(choices=RoomChoices.choices, default=RoomChoices.NO_PREFERENCE)
    isDivision = models.BooleanField(default=False)
    isShortLease = models.BooleanField(default=False)
    isDuplex = models.BooleanField(default=False)

    def __str__(self):
        return f"Options {self.id}"