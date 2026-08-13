from django.db import models
from datetime import date

class Occasion(models.Model):
    SOURCE_CHOICES = (
        ('google_calendar', 'Google Calendar'),
        ('manual', 'Manual'),
        ('automatic', 'Imported/Automatic'),
    )

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected/Skipped'),
    )

    APPROVAL_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected/Skipped'),
    )

    # Basic Info
    name = models.CharField(max_length=150)            # e.g. "Hareli Festival"
    date = models.DateField(default=date.today)         # Exact date e.g. 2026-08-17
    month = models.IntegerField(default=1)              # 1-12 (preserved for compatibility)
    day = models.IntegerField(default=1)                # 1-31 (preserved for compatibility)
    description = models.TextField(blank=True, null=True)

    # Source & Unique Tracking
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='manual')
    external_event_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    import_date = models.DateTimeField(auto_now_add=True, null=True)

    # Messaging & Media
    message = models.TextField(blank=True, help_text="Final greeting message to send to customers")
    ai_message = models.TextField(blank=True, help_text="AI generated greeting message")
    poster = models.ImageField(upload_to='occasion_posters/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Status & Approval (Mandatory Admin Approval Workflow)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_approval')
    approval_status = models.CharField(max_length=30, choices=APPROVAL_CHOICES, default='pending')

    # Schedule & Dispatch History
    scheduled_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    last_sent_year = models.IntegerField(blank=True, null=True)

    # Audit Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ['date', 'month', 'day']

    def save(self, *args, **kwargs):
        if self.date:
            self.month = self.date.month
            self.day = self.date.day
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.date or f'{self.day}/{self.month}'})"



class OccasionSettings(models.Model):
    show_on_website = models.BooleanField(
        default=True,
        verbose_name="Show Occasion Banner on Website",
        help_text="Global ON/OFF toggle switch to show or hide Special Occasion banners on the website homepage."
    )
    auto_sync_enabled = models.BooleanField(default=True, help_text="Auto-sync upcoming occasions from Google Calendar")
    advance_import_days = models.IntegerField(default=1, help_text="Import occasions ~1 day in advance")
    ai_generation_enabled = models.BooleanField(default=True, help_text="Generate AI greetings for imported occasions")
    admin_approval_required = models.BooleanField(default=True, help_text="Mandatory admin review & approval before sending")
    auto_sending_enabled = models.BooleanField(default=False, help_text="Auto send approved occasions on scheduled date")
    default_sending_time = models.TimeField(default="08:35:00", help_text="Default daily dispatch time (8:35 AM)")
    customer_sending_enabled = models.BooleanField(default=True, help_text="Enable customer notification dispatches")
    duplicate_protection_enabled = models.BooleanField(default=True, help_text="Prevent duplicate sending to same customer")
    default_source = models.CharField(max_length=50, default="Google Calendar")

    def __str__(self):
        status_str = "ON" if getattr(self, 'show_on_website', True) else "OFF"
        return f"Smart Occasion Global Settings (Website Banner: {status_str})"

    class Meta:
        verbose_name = "Occasion System Setting"
        verbose_name_plural = "Occasion System Settings"