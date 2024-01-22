from django.core.mail import send_mail


def sent_otp(otp, email, subject):
    send_mail(
        subject,
        f"Your otp {otp}",
        "detectingai.com@gmail.com",
        [email],
        fail_silently=False,
    )
    return True
