"""
Serializers for the reports app.
"""

from rest_framework import serializers
from .models import IncidentReport
from emergency_bot.agencies.models import Agency


class IncidentReportSerializer(serializers.ModelSerializer):
    """
    Serializer for IncidentReport model.
    """
    class Meta:
        model = IncidentReport
        fields = [
            'id', 'type', 'description', 'voice_note_url',
            'location', 'latitude', 'longitude', 'status',
            'submitted_at', 'last_updated'
        ]
        read_only_fields = ['id', 'submitted_at', 'last_updated']
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = None
        
        # Try to get user from request context
        if request and hasattr(request, 'user_profile'):
            user = request.user_profile
        
        if not user:
            raise serializers.ValidationError(
                {"user": "A valid user profile is required to submit a report."}
            )
        
        # Add user to validated data
        validated_data['user'] = user
        
        # Set IP address and device info for audit
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['device_info'] = request.META.get('HTTP_USER_AGENT', '')
        
        # Create and return the report
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class IncidentReportDetailSerializer(IncidentReportSerializer):
    """
    Detailed serializer for IncidentReport with nearby agencies.
    """
    nearby_agencies = serializers.SerializerMethodField()
    
    class Meta(IncidentReportSerializer.Meta):
        fields = IncidentReportSerializer.Meta.fields + ['nearby_agencies']
    
    def get_nearby_agencies(self, obj):
        """Get nearby agencies based on report location"""
        from emergency_bot.agencies.serializers import AgencySerializer
        
        # Find agencies within 10km of the incident
        nearby_agencies = []
        for agency in Agency.objects.filter(active=True):
            distance = agency.calculate_distance(obj.latitude, obj.longitude)
            if distance <= 10:  # 10km radius
                agency_data = AgencySerializer(agency).data
                agency_data['distance_km'] = round(distance, 2)
                nearby_agencies.append(agency_data)
        
        # Sort by distance
        return sorted(nearby_agencies, key=lambda x: x['distance_km'])[:5]


class ReportStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating an incident report status.
    """
    status = serializers.ChoiceField(choices=IncidentReport.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True) 