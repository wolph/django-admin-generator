from django.db import models


class Spam(models.Model):
    a = models.CharField(max_length=50)
