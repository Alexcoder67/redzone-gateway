from rest_framework import serializers
from .models import Event, RSVP, Waitlist
from django.utils import timezone

class EventSerializer(serializers.ModelSerializer):
    days_until_event = serializers.SerializerMethodField()
    rsvp_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'date', 'created_at', 'days_until_event', 'created_by', 'rsvp_count', 'is_cancelled', 'max_attendees']
        read_only_fields = ['created_by']

    def get_days_until_event(self, obj):
        delta = obj.date - timezone.now()
        return delta.days

    def get_rsvp_count(self, obj):
        count = obj.rsvps.count()
        if count == 1:
            return f"1 Person has RSVP'd to this event"
        return f"{count} People have RSVP'd to this event"

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Please choose a valid date for this activity.")
        return value

class RSVPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSVP
        fields = ['id', 'event', 'user', 'created_at']
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        event = data.get('event')
        if RSVP.objects.filter(user=user, event=event).exists():
            raise serializers.ValidationError("You have already RSVP'd to this event.")
        if event.max_attendees is not None:
            if event.rsvps.count() >= event.max_attendees:
                raise serializers.ValidationError("This event is full. Would you like to join the Waitlist instead?")
        return data

class WaitlistSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Waitlist
        fields = ['id', 'event', 'user', 'created_at']
        read_only_fields = ['user']
    
    def validate(self, data):
        user = self.context['request'].user
        event = data.get('event')
        if Waitlist.objects.filter(user=user, event=event).exists() == True:
            raise serializers.ValidationError("You are already on the waitlist for this event.")
        if not RSVP.objects.filter(user=user, event=event).exists() == False:
            raise serializers.ValidationError("You have already RSVP'd to this event, no need to join the waitlist.")
        return data