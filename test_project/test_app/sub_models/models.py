from django.db import models

from test_project.test_app.sub_models.meat import Spam


class ACollectionOfSpamAndEggsAndOtherStuff(Spam):
    this_should_be_something_really_long_a = models.CharField(max_length=100)
    this_should_be_something_really_long_b = models.CharField(max_length=100)
    this_should_be_something_really_long_c = models.CharField(max_length=100)
    this_should_be_something_really_long_d = models.CharField(max_length=100)
