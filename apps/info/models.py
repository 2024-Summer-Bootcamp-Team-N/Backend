from django.db import models

class Region(models.Model):
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)

class Residence(models.Model):
    apartment = models.BooleanField(default=False)
    officetel = models.BooleanField(default=False)
    house = models.BooleanField(default=False)
    onetwo = models.BooleanField(default=False)

class PropertyType(models.Model):
    lease = models.BooleanField(default=False)
    monthly_rent = models.BooleanField(default=False)
    depositRangeMax = models.IntegerField(null=True, blank=True)
    priceRangeMax = models.IntegerField(null=True, blank=True)

class Option(models.Model):
    parkingNumRangeMin = models.IntegerField(null=True, blank=True)
    isShortLease = models.BooleanField(default=False)
    roomCount = models.CharField(max_length=10, null=True, blank=True)
    hasElevator = models.BooleanField(default=False)
    canParking = models.BooleanField(default=False)
    isDivision = models.BooleanField(default=False)
    isDuplex = models.BooleanField(default=False)