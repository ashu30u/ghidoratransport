import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ghidora_transport.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory, Client
from occasions.models import OccasionRecipient, OccasionSettings, Occasion
from payments.models import PaymentRequest, PaymentProof, PaymentVerification, Receipt, PaymentStatus, PaymentType
from booking.models import Booking
from decimal import Decimal
from django.utils import timezone
from payments.utils import mark_payment_all_done_and_send_receipt
from occasions.services import dispatch_occasion_notifications

User = get_user_model()

def run_tests():
    # Clean previous test booking if any
    Booking.objects.filter(email="amit.test@gmail.com").delete()
    print("--- 1. Testing OccasionRecipient Admin & Dispatch Logic ---")
    # Clean test recipient if exists
    OccasionRecipient.objects.filter(email="admin_test_recipient@gmail.com").delete()
    
    recipient = OccasionRecipient.objects.create(
        email="admin_test_recipient@gmail.com",
        name="Test Vip Recipient",
        is_active=True,
        notes="Added via verification test"
    )
    print(f"Created OccasionRecipient: {recipient}")
    assert OccasionRecipient.objects.filter(email="admin_test_recipient@gmail.com", is_active=True).exists()

    # Verify recipient is picked up in send_occasion_to_customers raw emails
    active_recipients = list(OccasionRecipient.objects.filter(is_active=True).values_list('email', flat=True))
    assert "admin_test_recipient@gmail.com" in active_recipients, "Recipient not in active recipients list"
    print(f"Active Occasion Recipients include: {active_recipients}")

    print("\n--- 2. Testing Payment 'All Done' & Receipt Generation & Email ---")
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('test_admin', 'admin@ghidoratransport.com', 'adminpass123')
    
    # Create test booking
    booking = Booking.objects.create(
        name="Amit Kumar Test",
        email="amit.test@gmail.com",
        phone="9876543210",
        pickup="Delhi",
        destination="Jaipur",
        distance=250.0,
        fare=4500.0,
        vehicle_type="Mahindra Pickup",
        journey_date=timezone.now().date(),
        status="Pending"
    )

    from django.core.files.uploadedfile import SimpleUploadedFile

    # Create PaymentRequest
    payment_request = PaymentRequest.objects.create(
        booking=booking,
        amount=Decimal("4500.00"),
        total_fare=Decimal("4500.00"),
        status=PaymentStatus.SUBMITTED,
        payment_type=PaymentType.FULL,
        due_date=timezone.now() + timezone.timedelta(days=2),
        created_by=admin_user
    )

    # Create PaymentProof
    dummy_screenshot = SimpleUploadedFile("proof_sample.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82", content_type="image/png")
    proof = PaymentProof.objects.create(
        payment_request=payment_request,
        screenshot=dummy_screenshot,
        transaction_id="TXN1234567890TEST",
        amount_paid=Decimal("4500.00"),
        payment_date=timezone.now().date(),
        payment_time=timezone.now().time(),
        bank_name="HDFC Bank",
        upi_app_used="Google Pay"
    )

    print(f"Created Payment Request: {payment_request.payment_id}, Proof: {proof.id}")

    # Call mark_payment_all_done_and_send_receipt
    rf = RequestFactory()
    request = rf.get(f'/payments/admin-panel/all-done/{payment_request.payment_id}/')
    request.user = admin_user

    result = mark_payment_all_done_and_send_receipt(
        payment_request=payment_request,
        proof=proof,
        verified_by=admin_user,
        request=request
    )

    print(f"mark_payment_all_done result: {result}")
    assert result.get("success") is True, f"Failed to mark all done: {result}"

    # Refresh payment request and proof
    payment_request.refresh_from_db()
    proof.refresh_from_db()

    print(f"Updated Payment Request status: {payment_request.status}")
    print(f"Updated Payment Request amount_already_paid: {payment_request.amount_already_paid}")
    assert payment_request.status in [PaymentStatus.VERIFIED, PaymentStatus.COMPLETED]
    assert payment_request.amount_already_paid == Decimal("4500.00")

    # Check Verification
    verification = getattr(proof, 'verification', None)
    assert verification is not None, "Verification was not created"
    print(f"Verification action: {verification.action}")
    assert verification.action == PaymentVerification.Action.APPROVED

    # Check Receipt
    receipt = Receipt.objects.filter(payment_request=payment_request).first()
    assert receipt is not None, "Receipt was not created"
    print(f"Receipt ID: {receipt.receipt_id}")
    print(f"Receipt PDF: {receipt.pdf_file.name}")
    print(f"Receipt is_sent: {receipt.is_sent}")
    print(f"Receipt sent_to_email: {receipt.sent_to_email}")
    assert receipt.is_sent is True
    assert receipt.sent_to_email == "amit.test@gmail.com"
    assert receipt.pdf_file and receipt.pdf_file.name

    print("\n--- 3. Testing Django Admin Panel URLs (HTTP 200) ---")
    client = Client()
    client.force_login(admin_user)

    admin_urls = [
        "/admin/occasions/occasionrecipient/",
        "/admin/occasions/occasionrecipient/add/",
        "/admin/payments/paymentproof/",
        "/admin/payments/paymentrequest/",
        "/admin/payments/receipt/",
        f"/payments/admin-panel/verify/{payment_request.payment_id}/",
    ]

    for url in admin_urls:
        resp = client.get(url)
        print(f"GET {url} -> Status: {resp.status_code}")
        assert resp.status_code == 200, f"URL {url} failed with status {resp.status_code}"

    print("\n--- 4. Cleanup Test Data ---")
    recipient.delete()
    if receipt and receipt.pdf_file:
        try:
            if os.path.exists(receipt.pdf_file.path):
                os.remove(receipt.pdf_file.path)
        except Exception:
            pass
    payment_request.delete() # cascades to proof, verification, receipt
    booking.delete()
    print("All test data cleaned successfully!")
    print("\nALL TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
