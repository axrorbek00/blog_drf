import datetime

from django.shortcuts import render
from django.utils import timezone
from .models import MyUser
from .serializers import UserSignUpSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema  # ->bu bn swaggerda iwlasa boladi postmen xam kk emas
from rest_framework_simplejwt.tokens import RefreshToken
import random
from .tasks import sent_otp


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }


class UserSignupView(APIView):  # -> royxatdan otyotgan userga kod jinatish
    @swagger_auto_schema(request_body=UserSignUpSerializer)  # --> swagger APIviewga ishlamaydi, bu dekaratr bn iwlaydi
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "otp is send please check", "user_id": user.id},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUser(APIView):  # --> userga kelgan kodni tekwiriw
    def patch(self, request, pk):  # --> 1 fildni ozgartiramiz is_activ ni truga wunga patch iwlatamiz
        data = request.data
        otp = data.get('otp')
        user = MyUser.objects.get(pk=pk)

        if user.otp_max_out < datetime.datetime.now():  # max_out blokdan chiqiw vaqti < hozrgi vaqtdan

            if (
                    int(user.otp) == otp
                    and timezone.now() < user.otp_expiry  # --> otp kod amal qiliw vaqti
                    and user.otp_max_try >= 1  # 3 tadan kop xato kod jonatolmaydi
                    and user.is_active == False
            ):
                user.otp_max_try = 3  # user hama wartlardan togri otgach
                user.otp_expiry = None
                user.otp_max_out = None
                user.is_active = True
                user.save()
                # token = get_tokens_for_user(user=user)

                # JWT token

                return Response(
                    {
                        'message': 'User is activated',
                        # 'access': token['access'],
                        # 'refresh': token['refresh'],
                    }
                )
            else:
                return Response({"error": "otp is not valid or user active "})

        return Response({"error": "You are in blocking time "})


#
#
class ReGenerateCode(APIView):
    def get(self, request, pk):
        user = MyUser.objects.get(pk=pk)

        if user.otp_max_out > timezone.now():
            return Response({"message": "Your are in blocking time "})

        elif user.otp_max_out < timezone.now() and user.otp_max_try > 0:
            user.otp_max_out = 3
            user.otp_max_out = None
            user.save()

            user.otp_max_out -= 1

            otp = random.randint(1000, 9999)
            user.otp = otp
            user.otp_expiry = timezone.now() + datetime.timedelta(minutes=5)

            sent_otp(otp, user.email, 'Verify your email address')
            return Response({'message': 'Regenerated code is sent.'})

        elif user.otp_max_try < 1:
            user.otp_max_out = timezone.now() + datetime.timedelta(minutes=60)
            user.save()
            return Response({"message": "You are blocked"})

        else:
            user.otp_max_try -= 1
            otp = random.randint(1000, 9999)
            user.otp = otp
            user.otp_expiry = timezone.now() + datetime.timedelta(minutes=5)
            user.save()

            sent_otp(otp, user.email, 'Verify your email address')
            return Response({'message': 'regenerated code is sent.'})
