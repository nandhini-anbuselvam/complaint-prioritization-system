from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Complaint, ComplaintHistory


class ComplaintHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(
        source='performed_by.username', read_only=True, default=None
    )

    class Meta:
        model = ComplaintHistory
        fields = ['id', 'action', 'notes', 'performed_by', 'performed_by_name', 'timestamp']


class ComplaintListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_name = serializers.CharField(
        source='assigned_to.username', read_only=True, default=None
    )
    ticket_number = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id', 'ticket_number', 'title', 'category', 'priority', 'status',
            'current_level', 'department', 'created_by', 'created_by_name',
            'assigned_to', 'assigned_to_name', 'created_at', 'updated_at',
            'escalation_deadline', 'is_overdue',
        ]


class ComplaintDetailSerializer(ComplaintListSerializer):
    history = ComplaintHistorySerializer(many=True, read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)

    class Meta(ComplaintListSerializer.Meta):
        fields = ComplaintListSerializer.Meta.fields + [
            'description', 'classification_confidence', 'resolved_at',
            'history', 'created_by_detail', 'assigned_to_detail',
        ]


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['id', 'title', 'description', 'department']
        read_only_fields = ['id']


class ComplaintStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Complaint.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
