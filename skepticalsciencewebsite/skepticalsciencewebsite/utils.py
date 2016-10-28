from django.core.exceptions import PermissionDenied
from functools import update_wrapper


def same_user(user_field): # args of the decorator

    def decorator(func): # function

        def wrapped(self, *args, **kwargs): # args of the function
            if self.request.user != eval("self.object."+user_field):
                raise PermissionDenied
            return func(self, *args, **kwargs)

        return wrapped

    return decorator


def check_status(status, status_name):

    def decorator(func):

        def wrapped(self, *args, **kwargs):
            if status != eval("self.object."+status_name):
                raise PermissionDenied
            return func(self, *args, **kwargs)

        return wrapped

    return decorator




