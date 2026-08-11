from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.conf import settings

from .models import (
    PaymentRequest, PaymentProof, PaymentVerification,
    PaymentStatusHistory, PaymentStatus, NotificationType, Receipt
)
from .utils import notify, generate_receipt_pdf


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
            notes=f"Proof uploaded (TXN {instance.transaction_id or 'No TXN ID'}).",
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
    booking = pr.booking

    if instance.action == PaymentVerification.Action.APPROVED:
        pr.status = PaymentStatus.VERIFIED
        
        # Safe Decimal addition
        already_paid = Decimal(str(pr.amount_already_paid or 0))
        paid_amount = Decimal(str(proof.amount_paid if proof.amount_paid is not None else pr.amount))
        
        pr.amount_already_paid = already_paid + paid_amount
        pr.save(update_fields=["status", "amount_already_paid", "updated_at"])

        # 🌟 Auto-generate PDF Receipt & Send Email
        try:
            receipt, _ = Receipt.objects.get_or_create(payment_request=pr)
            pdf_content = generate_receipt_pdf(pr)
            receipt.pdf_file.save(pdf_content.name, pdf_content, save=True)

            # 📩 Send Email to Customer if email is provided
            if booking.email:
                try:
                    subject = f"🚚 Payment Verified & Receipt — Ghidora Transport (Booking #{booking.booking_id})"
                    body = f"""Dear {booking.name},

Thank you for your payment! Your payment has been successfully VERIFIED.

Payment ID: {pr.payment_id}
Booking ID: {booking.booking_id}
Amount Paid: Rs. {paid_amount:.2f}
Total Amount Paid So Far: Rs. {pr.amount_already_paid:.2f}
Remaining Balance: Rs. {pr.remaining_amount:.2f}
Payment Status: VERIFIED

Please find your official payment receipt attached with this email.

Thank You,
Ghidora Transport
Phone: +91 7489297841 / +91 6266014139
"""
                    email_msg = EmailMessage(
                        subject=subject,
                        body=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[booking.email],
                    )
                    receipt.pdf_file.open('rb')
                    email_msg.attach(
                        f"Receipt_{booking.booking_id}.pdf",
                        receipt.pdf_file.read(),
                        "application/pdf"
                    )
                    email_msg.send(fail_silently=True)
                    print(f"✅ Receipt email sent successfully to {booking.email}")
                except Exception as mail_err:
                    print("❌ Email sending failed:", mail_err)
        except Exception as err:
            print("❌ Receipt PDF generation error:", err)

        notify(
            notification_type=NotificationType.PAYMENT_VERIFIED,
            message=f"Payment {pr.payment_id} has been verified. Thank you!",
            booking=booking, payment_request=pr,
        )
    elif instance.action == PaymentVerification.Action.REJECTED:
        pr.status = PaymentStatus.REJECTED
        pr.save(update_fields=["status", "updated_at"])
        notify(
            notification_type=NotificationType.PAYMENT_REJECTED,
            message=f"Payment {pr.payment_id} was rejected. Please re-submit proof.",
            booking=booking, payment_request=pr,
        )

    PaymentStatusHistory.objects.create(
        payment_request=pr, status=pr.status, changed_by=instance.verified_by,
        notes=instance.notes or instance.get_action_display(),
    )