from .models import Notification


def notify(user, message, complaint=None):
    if user is None:
        return None
    return Notification.objects.create(user=user, message=message, complaint=complaint)
