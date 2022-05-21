import django.dispatch

# providing_args=["instance", "data"]
quiz_completed = django.dispatch.Signal()
