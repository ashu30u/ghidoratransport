from .models import DirectMessage, Notification


def unread_messages(request):
    if hasattr(request, "user") and request.user.is_authenticated:
        try:
            count = (
                DirectMessage.objects.filter(
                    conversation__participants=request.user,
                    is_read=False,
                )
                .exclude(sender=request.user)
                .count()
            )
            notif_count = Notification.objects.filter(
                recipient=request.user,
                is_read=False,
            ).count()
            return {
                "unread_messages_count": count,
                "unread_notifications_count": notif_count,
            }
        except Exception:
            return {
                "unread_messages_count": 0,
                "unread_notifications_count": 0,
            }
    return {
        "unread_messages_count": 0,
        "unread_notifications_count": 0,
    }

