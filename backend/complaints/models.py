from django.conf import settings
from django.db import models
from django.utils import timezone


class Complaint(models.Model):

    class Category(models.TextChoices):
        INFRASTRUCTURE = 'Infrastructure', 'Infrastructure'
        ACADEMIC = 'Academic', 'Academic'
        SAFETY = 'Safety', 'Safety'
        HOSTEL = 'Hostel', 'Hostel'
        LIBRARY = 'Library', 'Library'
        TRANSPORT = 'Transport', 'Transport'
        ADMINISTRATIVE = 'Administrative', 'Administrative'
        RAGGING_HARASSMENT = 'Ragging & Harassment', 'Ragging & Harassment'
        OTHER = 'Other', 'Other'

    class Priority(models.TextChoices):
        HIGH = 'High', 'High'
        MEDIUM = 'Medium', 'Medium'
        LOW = 'Low', 'Low'

    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        IN_PROGRESS = 'In Progress', 'In Progress'
        ESCALATED = 'Escalated', 'Escalated'
        RESOLVED = 'Resolved', 'Resolved'

    class Level(models.TextChoices):
        HOD = 'hod', 'Department Authority (HOD)'
        DEAN = 'dean', 'Dean'
        FINAL_AUTHORITY = 'final_authority', 'Final Authority'

    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.CharField(max_length=40, choices=Category.choices, default=Category.OTHER)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    classification_confidence = models.FloatField(default=0.0)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    current_level = models.CharField(max_length=20, choices=Level.choices, default=Level.HOD)

    department = models.CharField(max_length=100, blank=True, default='')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='complaints_filed', on_delete=models.CASCADE
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='complaints_assigned',
        null=True, blank=True, on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    escalation_deadline = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.id} {self.title} ({self.priority}/{self.status})'

    @property
    def is_overdue(self):
        return (
            self.status not in (self.Status.RESOLVED,)
            and self.escalation_deadline is not None
            and timezone.now() > self.escalation_deadline
        )

    @property
    def ticket_number(self):
        return f'CMP-{self.created_at.year}-{self.id:04d}' if self.id and self.created_at else None


class ComplaintHistory(models.Model):
    complaint = models.ForeignKey(Complaint, related_name='history', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    notes = models.TextField(blank=True, default='')
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name_plural = 'Complaint history'

    def __str__(self):
        return f'{self.complaint_id}: {self.action}'
