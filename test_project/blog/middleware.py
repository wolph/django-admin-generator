"""Demo-only middleware.

`AutoLoginMiddleware` signs every visitor in as the seeded ``admin`` superuser
so the demo admin is reachable without a login step. This is obviously
**not** something you would ever ship — it exists purely to make the live demo
frictionless.
"""

from collections.abc import Callable

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpRequest, HttpResponse

_BACKEND = 'django.contrib.auth.backends.ModelBackend'


class AutoLoginMiddleware:
    def __init__(
        self, get_response: Callable[[HttpRequest], HttpResponse]
    ) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if settings.DEBUG and not request.user.is_authenticated:
            user = (
                get_user_model()
                ._default_manager.filter(username='admin')
                .first()
            )
            if user is not None:
                login(request, user, backend=_BACKEND)
        return self.get_response(request)
