import django.dispatch

objectContentUpdated = django.dispatch.Signal(providing_args=["idList", "created", "deleted", "completed"])
