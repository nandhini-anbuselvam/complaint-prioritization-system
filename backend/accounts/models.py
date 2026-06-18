from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user with a role used to drive the whole complaint workflow.

    - student: raises complaints
    - hod: first responder, handles complaints for their department
    - dean: handles complaints escalated past the HOD
    - final_authority: last stop for complaints escalated past the Dean
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        HOD = 'hod', 'Department Authority (HOD)'
        DEAN = 'dean', 'Dean'
        FINAL_AUTHORITY = 'final_authority', 'Final Authority'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    department = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
