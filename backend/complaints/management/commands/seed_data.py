from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from complaints import services
from complaints.models import Complaint

User = get_user_model()

DEMO_PASSWORD = 'password123'

DEMO_USERS = [
    dict(username='admin', role='final_authority', first_name='System', last_name='Admin',
         department='', is_staff=True, is_superuser=True),
    dict(username='student1', role='student', first_name='Asha', last_name='Rao', department=''),
    dict(username='student2', role='student', first_name='Vikram', last_name='Singh', department=''),
    dict(username='hod_cse', role='hod', first_name='Dr. Meena', last_name='Iyer', department='CSE'),
    dict(username='hod_ece', role='hod', first_name='Dr. Arjun', last_name='Nair', department='ECE'),
    dict(username='dean1', role='dean', first_name='Dr. Kavitha', last_name='Menon', department=''),
    dict(username='final1', role='final_authority', first_name='Prof. Ramesh', last_name='Gupta', department=''),
]

DEMO_COMPLAINTS = [
    ('Restroom not cleaned in Block A', 'The restroom on the ground floor of Block A is not clean.'),
    ('Smoke in chemistry lab', 'There is smoke coming from the laboratory during the afternoon session.'),
    ('Bus running 40 minutes late', 'College bus number 4 has been arriving 40 minutes late every day this week.'),
    ('Scholarship application stuck', 'Our scholarship application has been pending for three months with no update.'),
    ('Hostel mess food quality', 'Hostel mess food quality has been very poor for the past week.'),
]


class Command(BaseCommand):
    help = 'Creates demo users (one per role) and a few sample complaints so the app is usable immediately.'

    def handle(self, *args, **options):
        created_users = {}
        for u in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'role': u['role'], 'first_name': u['first_name'],
                    'last_name': u['last_name'], 'department': u['department'],
                    'is_staff': u.get('is_staff', False),
                    'is_superuser': u.get('is_superuser', False),
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user {user.username} ({user.role})'))
            created_users[u['username']] = user

        student = created_users['student1']
        if not Complaint.objects.exists():
            for title, description in DEMO_COMPLAINTS:
                complaint = Complaint.objects.create(
                    title=title, description=description, created_by=student,
                )
                services.initialize_complaint(complaint)
                self.stdout.write(self.style.SUCCESS(
                    f'Created complaint "{title}" -> {complaint.category}/{complaint.priority}'
                ))

        self.stdout.write(self.style.SUCCESS(
            f"\nDemo accounts ready. Password for all demo users: '{DEMO_PASSWORD}'"
        ))
        self.stdout.write('  student1 / student2   -> Student')
        self.stdout.write('  hod_cse / hod_ece      -> HOD')
        self.stdout.write('  dean1                  -> Dean')
        self.stdout.write('  final1 (or admin)      -> Final Authority')
