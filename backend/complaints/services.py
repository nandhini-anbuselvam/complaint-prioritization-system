from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications.services import notify

from .models import Complaint, ComplaintHistory

User = get_user_model()

LEVEL_ORDER = [Complaint.Level.HOD, Complaint.Level.DEAN, Complaint.Level.FINAL_AUTHORITY]


def deadline_for_priority(priority):
    hours = settings.ESCALATION_DEADLINES_HOURS.get(priority, 72)
    return timezone.now() + timezone.timedelta(hours=hours)


def pick_assignee(level, department=''):
    """Pick a user for the given authority level. Prefers a department match
    for HOD-level complaints when a department was supplied; otherwise picks
    the first available user with that role."""
    qs = User.objects.filter(role=level)
    if level == Complaint.Level.HOD and department:
        dept_match = qs.filter(department__iexact=department).first()
        if dept_match:
            return dept_match
    return qs.order_by('id').first()


def log_history(complaint, action, performed_by=None, notes=''):
    return ComplaintHistory.objects.create(
        complaint=complaint, action=action, performed_by=performed_by, notes=notes
    )


def initialize_complaint(complaint):
    """Called right after a student creates a complaint: runs NLP
    classification, assigns to an HOD, and sets the SLA deadline."""
    from .ml.classifier import classify

    result = classify(f'{complaint.title}. {complaint.description}')

    complaint.category = result['category']
    complaint.priority = result['priority']
    complaint.classification_confidence = result['confidence']
    complaint.current_level = Complaint.Level.HOD
    complaint.status = Complaint.Status.PENDING
    complaint.assigned_to = pick_assignee(Complaint.Level.HOD, complaint.department)
    complaint.escalation_deadline = deadline_for_priority(complaint.priority)
    complaint.save()

    note = f"Classified as '{complaint.category}' with priority '{complaint.priority}'"
    if result['safety_override']:
        note += ' (safety keyword override applied)'
    log_history(complaint, 'Complaint submitted & auto-classified', complaint.created_by, note)

    if complaint.assigned_to:
        log_history(
            complaint, f'Assigned to HOD {complaint.assigned_to.username}',
            performed_by=None,
        )
        notify(
            complaint.assigned_to,
            f"New {complaint.priority} priority complaint assigned to you: '{complaint.title}'",
            complaint,
        )
    notify(
        complaint.created_by,
        f"Your complaint '{complaint.title}' was classified as {complaint.category} "
        f"({complaint.priority} priority) and sent to the HOD.",
        complaint,
    )
    return complaint


def escalate(complaint, performed_by=None, reason='SLA deadline exceeded'):
    """Moves a complaint to the next authority level. Returns False if it's
    already at the final authority (nothing further to escalate to)."""
    current_index = LEVEL_ORDER.index(complaint.current_level)
    if current_index >= len(LEVEL_ORDER) - 1:
        return False

    next_level = LEVEL_ORDER[current_index + 1]
    complaint.current_level = next_level
    complaint.status = Complaint.Status.ESCALATED
    complaint.assigned_to = pick_assignee(next_level, complaint.department)
    complaint.escalation_deadline = deadline_for_priority(complaint.priority)
    complaint.save()

    log_history(
        complaint,
        f'Escalated to {complaint.get_current_level_display()}',
        performed_by=performed_by,
        notes=reason,
    )
    notify(
        complaint.created_by,
        f"Your complaint '{complaint.title}' was escalated to "
        f"{complaint.get_current_level_display()}.",
        complaint,
    )
    if complaint.assigned_to:
        notify(
            complaint.assigned_to,
            f"Escalated complaint assigned to you: '{complaint.title}' "
            f"({complaint.priority} priority)",
            complaint,
        )
    return True


def resolve(complaint, performed_by=None, notes=''):
    complaint.status = Complaint.Status.RESOLVED
    complaint.resolved_at = timezone.now()
    complaint.save()
    log_history(complaint, 'Complaint resolved', performed_by=performed_by, notes=notes)
    notify(
        complaint.created_by,
        f"Good news - your complaint '{complaint.title}' has been resolved.",
        complaint,
    )
