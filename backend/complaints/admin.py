from django.contrib import admin

from .models import Complaint, ComplaintHistory


class ComplaintHistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('action', 'notes', 'performed_by', 'timestamp')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'priority', 'status', 'current_level',
        'created_by', 'assigned_to', 'created_at', 'escalation_deadline',
    )
    list_filter = ('category', 'priority', 'status', 'current_level')
    search_fields = ('title', 'description')
    inlines = [ComplaintHistoryInline]
