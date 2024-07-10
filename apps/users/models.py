from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, auth_id, password=None, **extra_fields):
        if not auth_id:
            raise ValueError('The auth_id field must be set')
        user = self.model(auth_id=auth_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, auth_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(auth_id, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    auth_id = models.CharField(max_length=45, unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=45)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'auth_id'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users_table'
    def __str__(self):
        return self.auth_id

    def set_password(self, raw_password):
        self.password = raw_password  # 평문 비밀번호 저장

    def check_password(self, raw_password):
        return self.password == raw_password  # 평문 비밀번호 확인