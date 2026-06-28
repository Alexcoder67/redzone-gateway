from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    days_until_event = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'created_at', 'days_until_event']

    def get_days_until_event(self, obj):
        from django.utils import timezone
        delta = obj.date - timezone.now()
        return delta.days