from functools import wraps
from django.views.decorators.cache import cache_page, cache_control


def cache_on_auth(timeout):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return cache_control(no_cache=True)(cache_page(timeout)(view_func)(request, *args, **kwargs))
            else:
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator