import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

app = Celery('pixelcraft')

app.config_from_object('django.conf:settings', namespace='CELERY')  # xamma nastroykani confdagi setingsdan
# olshini aytyapti

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



