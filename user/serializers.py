import datetime
import random

from django.contrib.auth.hashers import make_password

from .models import MyUser
from rest_framework import serializers
from .tasks import sent_otp
from django.utils import timezone

class UserSignUpSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)  # faqat yozish mumkin korish yoq
    password2 = serializers.CharField(write_only=True)  # chunki model passwor oladi password1 yoki 2 emas

    class Meta:
        model = MyUser
        fields = ["email", "password1", "password2"]

    def create(self, validated_data):
        if validated_data["password1"] == validated_data["password2"]:
            otp = random.randint(1000, 9999)
            otp_expiry = timezone.now() + datetime.timedelta(minutes=5)

            user = MyUser.objects.create(
                email=validated_data['email'],
                password=make_password(validated_data['password1']),
                otp=otp,
                otp_expiry=otp_expiry
            )

            sent_otp(otp, validated_data['email'], 'Verify your email address')

            return user
        else:
            return serializers.ValidationError('Passwords must match')
