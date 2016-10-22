from django.apps import AppConfig


class CustompaymentConfig(AppConfig):
    name = 'custompayment'

    def ready(self):
        from custompayment import signals
