from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    PaymentRequest, PaymentProof, PaymentVerification,
    PaymentStatusHistory, PaymentStatus, NotificationType,
)
from .utils import notify


@receiver(post_save, sender=PaymentRequest)
def on_payment_request_created(sender, instance, created, **kwargs):
    if created:
        PaymentStatusHistory.objects.create(
            payment_request=instance, status=instance.status,
            changed_by=instance.created_by, notes="Payment request generated.",
        )
        notify(
            notification_type=NotificationType.PAYMENT_PENDING,
            message=f"A payment of Rs. {instance.amount} is due for booking "
                     f"{instance.booking.booking_id}.",
            booking=instance.booking,
            payment_request=instance,
        )


@receiver(post_save, sender=PaymentProof)
def on_proof_submitted(sender, instance, created, **kwargs):
    if created:
        pr = instance.payment_request
        pr.status = PaymentStatus.WAITING_VERIFICATION
        pr.preferred_method = instance.method_used
        pr.save(update_fields=["status", "preferred_method", "updated_at"])
        PaymentStatusHistory.objects.create(
            payment_request=pr, status=pr.status,
            notes=f"Proof uploaded (TXN {instance.transaction_id}).",
        )
        notify(
            notification_type=NotificationType.PAYMENT_SUBMITTED,
            message=f"Your payment proof for {pr.payment_id} was submitted "
                     f"and is awaiting verification.",
            booking=pr.booking,
            payment_request=pr,
        )


@receiver(post_save, sender=PaymentVerification)
def on_verification_decided(sender, instance, created, **kwargs):
    if not created:
        return
    proof = instance.proof
    pr = proof.payment_request

    if instance.action == PaymentVerification.Action.APPROVED:
        pr.status = PaymentStatus.VERIFIED
        pr.amount_already_paid = pr.amount_already_paid + proof.amount_paid
        pr.save(update_fields=["status", "amount_already_paid", "updated_at"])
        notify(
            notification_type=NotificationType.PAYMENT_VERIFIED,
            message=f"Payment {pr.payment_id} has been verified. Thank you!",
            booking=pr.booking, payment_request=pr,
        )
    elif instance.action == PaymentVerification.Action.REJECTED:
        pr.status = PaymentStatus.REJECTED
        pr.save(update_fields=["status", "updated_at"])
        notify(
            notification_type=NotificationType.PAYMENT_REJECTED,
            message=f"Payment {pr.payment_id} was rejected: "
                     f"{instance.get_rejection_reason_display()}. Please re-submit.",
            booking=pr.booking, payment_request=pr,
        )
    else:  # re-upload requested
        pr.status = PaymentStatus.PENDING
        pr.save(update_fields=["status", "updated_at"])
        notify(
            notification_type=NotificationType.PAYMENT_REJECTED,
            message=f"Please re-upload your payment proof for {pr.payment_id}.",
            booking=pr.booking, payment_request=pr,
        )

    PaymentStatusHistory.objects.create(
        payment_request=pr, status=pr.status, changed_by=instance.verified_by,
        notes=instance.notes or instance.get_action_display(),
    )
