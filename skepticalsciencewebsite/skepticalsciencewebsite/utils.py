from functools import update_wrapper
from django.core.exceptions import PermissionDenied
from django.forms import ClearableFileInput
from django.utils.html import conditional_escape


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


class NoLinkClearableFileInput(ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s: %(initial)s '
        '%(clear_template)s<br />%(input_text)s: %(input)s'
    )

    def get_template_substitution_values(self, value):
        """
        Return value-related substitutions.
        """
        return {
            'initial': conditional_escape(str(value).split("/")[-1]),
            'initial_url': conditional_escape(value.url),
        }