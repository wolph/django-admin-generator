from django.db import models

from .sub_models import eggs, meat, models as sub_models_models

assert eggs
assert meat
assert sub_models_models


class DateHierarchyModel(models.Model):
    created_at = models.DateField()


class SluggedField(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
