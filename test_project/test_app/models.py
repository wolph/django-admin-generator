from django.db import models


class Spam(models.Model):
    a = models.CharField(max_length=50)


class Eggs(Spam):
    b = models.CharField(max_length=100)


class ACollectionOfSpamAndEggsAndOtherStuff(Spam):
    this_should_be_something_really_long_a = models.CharField(max_length=100)
    this_should_be_something_really_long_b = models.CharField(max_length=100)
    this_should_be_something_really_long_c = models.CharField(max_length=100)
    this_should_be_something_really_long_d = models.CharField(max_length=100)


class DateHierarchyModel(models.Model):
    created_at = models.DateField()


class SluggedField(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

