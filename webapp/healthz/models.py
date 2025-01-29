from django.db import models
from django.utils.timezone import now

# Create your models here.
class HealthCheck(models.Model):
    # Primary key with auto-incremented ID
    check_id = models.AutoField(primary_key=True)

    # Datetime field with UTC timezone
    datetime = models.DateTimeField(default=now)