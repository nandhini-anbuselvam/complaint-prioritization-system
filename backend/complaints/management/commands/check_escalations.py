from django.core.management.base import BaseCommand
from django.utils import timezone

from complaints import services
from complaints.models import Complaint


class Command(BaseCommand):
    help = (
        'Checks all open complaints and escalates any that have passed their '
        'escalation_deadline to the next authority level. Intended to be run '
        'on a schedule (e.g. via cron every few minutes, or Celery beat).'
    )

    def handle(self, *args, **options):
        now = timezone.now()
        overdue = Complaint.objects.exclude(status=Complaint.Status.RESOLVED).filter(
            escalation_deadline__lt=now
        )

        escalated_count = 0
        for complaint in overdue:
            moved = services.escalate(
                complaint,
                performed_by=None,
                reason=f'Auto-escalated: SLA deadline ({complaint.priority} priority) exceeded',
            )
            if moved:
                escalated_count += 1
                self.stdout.write(self.style.WARNING(
                    f'Escalated complaint #{complaint.id} "{complaint.title}" '
                    f'to {complaint.get_current_level_display()}'
                ))
            else:
                self.stdout.write(self.style.NOTICE(
                    f'Complaint #{complaint.id} is overdue but already with Final Authority.'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Escalation check complete. {escalated_count} complaint(s) escalated.'
        ))
