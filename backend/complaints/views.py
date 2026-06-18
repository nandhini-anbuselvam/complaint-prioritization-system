from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAuthorityRole, IsStudent
from notifications.services import notify

from . import services
from .models import Complaint
from .serializers import (
    ComplaintCreateSerializer,
    ComplaintDetailSerializer,
    ComplaintHistorySerializer,
    ComplaintListSerializer,
    ComplaintStatusUpdateSerializer,
)

User = get_user_model()


class IsOwnerOrAssignedAuthority(permissions.BasePermission):
    """Students can only act on their own complaints (read-only in practice);
    authorities can only act on complaints currently sitting at their level."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'student':
            return obj.created_by_id == user.id
        return obj.current_level == user.role


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.select_related('created_by', 'assigned_to').all()
    http_method_names = ['get', 'post', 'head', 'options']  # workflow actions instead of PUT/PATCH

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsStudent()]
        if self.action in ('update_status', 'escalate', 'resolve'):
            return [permissions.IsAuthenticated(), IsAuthorityRole(), IsOwnerOrAssignedAuthority()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return ComplaintCreateSerializer
        if self.action == 'list':
            return ComplaintListSerializer
        return ComplaintDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Complaint.objects.select_related('created_by', 'assigned_to')
        if user.role == 'student':
            return qs.filter(created_by=user)
        if user.role in ('hod', 'dean', 'final_authority'):
            return qs.filter(current_level=user.role)
        return qs.none()

    def perform_create(self, serializer):
        complaint = serializer.save(created_by=self.request.user)
        services.initialize_complaint(complaint)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        complaint = serializer.instance
        out = ComplaintDetailSerializer(complaint, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        complaint = self.get_object()
        serializer = ComplaintStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        notes = serializer.validated_data.get('notes', '')

        if new_status == Complaint.Status.RESOLVED:
            services.resolve(complaint, performed_by=request.user, notes=notes)
        else:
            complaint.status = new_status
            complaint.save()
            services.log_history(
                complaint, f'Status changed to {new_status}',
                performed_by=request.user, notes=notes,
            )
            notify(
                complaint.created_by,
                f"Your complaint '{complaint.title}' status changed to {new_status}.",
                complaint,
            )

        out = ComplaintDetailSerializer(complaint, context=self.get_serializer_context())
        return Response(out.data)

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        complaint = self.get_object()
        reason = request.data.get('reason', 'Manually escalated by authority')
        moved = services.escalate(complaint, performed_by=request.user, reason=reason)
        if not moved:
            return Response(
                {'detail': 'This complaint is already with the Final Authority.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        out = ComplaintDetailSerializer(complaint, context=self.get_serializer_context())
        return Response(out.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        complaint = self.get_object()
        notes = request.data.get('notes', '')
        services.resolve(complaint, performed_by=request.user, notes=notes)
        out = ComplaintDetailSerializer(complaint, context=self.get_serializer_context())
        return Response(out.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        complaint = self.get_object()
        serializer = ComplaintHistorySerializer(complaint.history.all(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        data = {
            'total': qs.count(),
            'pending': qs.filter(status=Complaint.Status.PENDING).count(),
            'in_progress': qs.filter(status=Complaint.Status.IN_PROGRESS).count(),
            'escalated': qs.filter(status=Complaint.Status.ESCALATED).count(),
            'resolved': qs.filter(status=Complaint.Status.RESOLVED).count(),
            'high_priority_open': qs.filter(
                priority=Complaint.Priority.HIGH
            ).exclude(status=Complaint.Status.RESOLVED).count(),
            'overdue': sum(1 for c in qs if c.is_overdue),
        }
        return Response(data)
