from rest_framework import serializers
from .models import Event
from django.utils import timezone

class EventSerializer(serializers.ModelSerializer):
    days_until_event = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'created_at', 'days_until_event', 'created_by']
        read_only_fields = ['created_by']
        
    def get_days_until_event(self, obj):
        from django.utils import timezone
        delta = obj.date - timezone.now()
        return delta.days

    def validate_date(self, value ):
        if value < timezone.now():
            raise serializers.ValidationError("Please choose a valid date for this activity.")
        return value