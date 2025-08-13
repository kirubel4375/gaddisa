"""
Views for the reports app.
"""

import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import IncidentReport
from .serializers import (
    IncidentReportSerializer,
    IncidentReportDetailSerializer,
    ReportStatusUpdateSerializer,
)

logger = logging.getLogger(__name__)


class IncidentReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for incident reports.
    
    create: Submit a new emergency incident report.
    retrieve: Get details of a specific incident report.
    list: Get a list of incident reports.
    update: Update all fields of an incident report.
    partial_update: Update specific fields of an incident report.
    destroy: Delete an incident report.
    """
    queryset = IncidentReport.objects.all()
    serializer_class = IncidentReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter reports by user if not admin.
        """
        user = getattr(self.request, 'user_profile', None)
        
        # If no user_profile, return empty queryset
        if not user:
            return IncidentReport.objects.none()
        
        # Return all reports for staff, or only user's reports for regular users
        queryset = IncidentReport.objects.all()
        
        # Apply optional filters from query parameters
        if self.request.query_params.get('status'):
            queryset = queryset.filter(status=self.request.query_params.get('status'))
        
        if self.request.query_params.get('type'):
            queryset = queryset.filter(type=self.request.query_params.get('type'))
        
        if self.request.query_params.get('search'):
            search_query = self.request.query_params.get('search')
            queryset = queryset.filter(
                Q(description__icontains=search_query) | 
                Q(location__icontains=search_query)
            )
        
        # Always filter by user unless explicitly requesting all
        if not self.request.query_params.get('all') == 'true':
            queryset = queryset.filter(user=user)
        
        return queryset
    
    def get_serializer_class(self):
        """
        Use different serializers for list/detail.
        """
        if self.action == 'retrieve':
            return IncidentReportDetailSerializer
        return IncidentReportSerializer
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        Update the status of an incident report.
        """
        report = self.get_object()
        serializer = ReportStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Update the report status
            old_status = report.status
            new_status = serializer.validated_data['status']
            
            report.status = new_status
            report.last_updated = timezone.now()
            report.save(update_fields=['status', 'last_updated'])
            
            # Log the status change
            logger.info(
                f"Report {report.id} status updated from {old_status} to {new_status} by {request.user}"
            )
            
            # Send real-time notification
            try:
                self._send_status_update_notification(report, new_status, serializer.validated_data.get('notes', ''))
            except Exception as e:
                logger.error(f"Error sending status update notification: {e}")
            
            # Create notification record in the database
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=report.user,
                    title="Report Status Updated",
                    message=f"Your report status has been updated to {report.get_status_display()}",
                    notification_type="report_status",
                    priority="medium",
                    related_report=report,
                )
            except Exception as e:
                logger.error(f"Error creating notification record: {e}")
            
            # Return the updated report
            response_serializer = self.get_serializer(report)
            return Response(response_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_status_update_notification(self, report, new_status, notes=''):
        """
        Send a real-time notification about the status change.
        """
        channel_layer = get_channel_layer()
        
        # Send to report-specific group
        async_to_sync(channel_layer.group_send)(
            f"report_{report.id}",
            {
                "type": "report_update",
                "report_id": str(report.id),
                "status": new_status,
                "message": notes or f"Report status updated to {report.get_status_display()}",
                "timestamp": timezone.now().isoformat(),
            },
        )
        
        # Also send to user's notification group
        async_to_sync(channel_layer.group_send)(
            f"notifications_{report.user.telegram_id}",
            {
                "type": "notification_message",
                "notification_id": str(report.id),
                "title": "Report Status Updated",
                "message": f"Your report status has been updated to {report.get_status_display()}",
                "notification_type": "report_status",
                "priority": "medium",
                "timestamp": timezone.now().isoformat(),
                "related_report": str(report.id),
            },
        ) 