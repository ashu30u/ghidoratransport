import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('occasions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OccasionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_sync_enabled', models.BooleanField(default=True, help_text='Auto-sync upcoming occasions from Google Calendar')),
                ('advance_import_days', models.IntegerField(default=30, help_text='Import occasions ~30 days in advance')),
                ('ai_generation_enabled', models.BooleanField(default=True, help_text='Generate AI greetings for imported occasions')),
                ('admin_approval_required', models.BooleanField(default=True, help_text='Mandatory admin review & approval before sending')),
                ('auto_sending_enabled', models.BooleanField(default=False, help_text='Auto send approved occasions on scheduled date')),
                ('default_sending_time', models.TimeField(default='10:00:00', help_text='Default daily dispatch time')),
                ('customer_sending_enabled', models.BooleanField(default=True, help_text='Enable customer notification dispatches')),
                ('duplicate_protection_enabled', models.BooleanField(default=True, help_text='Prevent duplicate sending to same customer')),
                ('default_source', models.CharField(default='Google Calendar', max_length=50)),
            ],
            options={
                'verbose_name': 'Occasion System Setting',
                'verbose_name_plural': 'Occasion System Settings',
            },
        ),
        migrations.AlterModelOptions(
            name='occasion',
            options={'ordering': ['date', 'month', 'day']},
        ),
        migrations.AddField(
            model_name='occasion',
            name='ai_message',
            field=models.TextField(blank=True, help_text='AI generated greeting message'),
        ),
        migrations.AddField(
            model_name='occasion',
            name='approval_status',
            field=models.CharField(choices=[('pending', 'Pending Review'), ('approved', 'Approved'), ('rejected', 'Rejected/Skipped')], default='pending', max_length=30),
        ),
        migrations.AddField(
            model_name='occasion',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='occasion',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='occasion',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='occasion',
            name='external_event_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='occasion',
            name='import_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='occasion',
            name='scheduled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='occasion',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='occasion',
            name='source',
            field=models.CharField(choices=[('google_calendar', 'Google Calendar'), ('manual', 'Manual'), ('automatic', 'Imported/Automatic')], default='manual', max_length=30),
        ),
        migrations.AddField(
            model_name='occasion',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('rejected', 'Rejected/Skipped')], default='pending_approval', max_length=30),
        ),
        migrations.AddField(
            model_name='occasion',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='occasion',
            name='day',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='occasion',
            name='message',
            field=models.TextField(blank=True, help_text='Final greeting message to send to customers'),
        ),
        migrations.AlterField(
            model_name='occasion',
            name='month',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='occasion',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]
