"""URL configuration for the blog demo project."""

from django import urls
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    urls.path('admin/', admin.site.urls),
    # Send the bare homepage straight to the admin.
    urls.path(
        '',
        RedirectView.as_view(url='/admin/', permanent=False),
        name='home',
    ),
]
