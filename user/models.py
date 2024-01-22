from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

GENDER_CHOICES = (("male", "male"), ("female", "female"))


class UserManager(BaseUserManager):  # --> createsuperuserda bu ishlaydi
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("User mast have a email")
        user = self.model(email=email)  # --> user model
        user.set_password(password)  # --> set password paswordni hashlaydi

        user.save(using=self._db)
        return user

    #
    def create_superuser(self, email, password):
        user = self.create_user(email=email, password=password)
        user.is_active = True  # --> user activligni bilish
        user.is_staff = True  # --> admin panelga kirish uch
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):  # --> Userni 0 dan yozamiz AbstractBaseUser da
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=60, unique=True, null=True)
    phone_number = models.CharField(max_length=15, null=True)
    country = models.CharField(max_length=100, null=True)
    data_birth = models.DateField(null=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, null=True)
    password = models.CharField(max_length=500)

    otp = models.CharField(max_length=6, null=True)  # emailga keladgan genrated cod
    otp_max_try = models.IntegerField(default=3, null=True)  # cod terish uch 3 urunish
    otp_max_out = models.DateTimeField(null=True)  # --> 3 tadan kop xato cod kiritsa 1 soat block boladi owa vaqat
    otp_expiry = models.DateTimeField(null=True)  # --> codni amal qilish vaqti

    is_active = models.BooleanField(default=False)  # --> activmi yoqmi bilish un
    is_staff = models.BooleanField(default=False)  # --> admin panelga kirish uchun

    roles = (('writer', 'writer'), ('moderator', 'moderator'))
    role = models.CharField(null=True, choices=roles, max_length=10)

    USERNAME_FIELD = 'email'  # authenticated [username=username, password=password] username orniga -
    # email yozamiz chunki email bn royxatdan otadgan signi yozamiz

    objects = UserManager()  # --> userni ozimiz yozganimiz uchun Superuserni ham ozimiz yozamiz
    # objects = BaseUserManager()
