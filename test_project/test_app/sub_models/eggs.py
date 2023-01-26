from django.db import models

from .meat import Spam


class Eggs(Spam):
    b = models.CharField(max_length=100)
