from django.db import models

class Category(models.Model):
    province = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    street = models.CharField(max_length=20)
    apartment = models.BooleanField(default=False)
    villa = models.BooleanField(default=False)
    room = models.BooleanField(default=False)
    yearly = models.BooleanField(default=False)
    yearly_fee = models.IntegerField(null=True, blank=True)
    monthly = models.BooleanField(default=False)
    deposit = models.IntegerField(null=True, blank=True)
    monthly_fee = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.province} {self.district} {self.street}"
