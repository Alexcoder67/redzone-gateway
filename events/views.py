from rest_framework import viewsets, permissions
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, RSVP, Waitlist
from .serializers import EventSerializer, RSVPSerializer, WaitlistSerializer
from rest_framework import filters
from .permissions import IsOwnerOrReadOnly
from .tasks import send_rsvp_confirmation, send_waitlist_confirmation, send_waitlist_promoted, send_event_cancelled, send_event_cancelled_host

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location']
    search_fields = ['title', 'description']
    ordering_fields = ['date', 'created_at']

    def perform_create(self, serializer):

        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        event = self.get_object()
        event.is_cancelled = True
        event.save()

        for rsvp in event.rsvps.all():
            send_event_cancelled.delay(rsvp.user.email, event.title)

        for entry in event.waitlist.all():
            send_event_cancelled.delay(entry.user.email, event.title)

        send_event_cancelled_host.delay(event.created_by.email, event.title)

        return Response({'status': 'Event cancelled', 'is_cancelled': event.is_cancelled})
    
    @action(detail=False, methods=['get'])
    def my_events(self, request):
        events = Event.objects.filter(created_by=request.user).order_by('date')
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)   

class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        rsvp = serializer.save(user=self.request.user)
        send_rsvp_confirmation.delay(
            rsvp.user.email,
            rsvp.event.title
        )

    def perform_destroy(self, instance):
        event = instance.event
        instance.delete()

        next_in_line = Waitlist.objects.filter(event=event).order_by('created_at').first()
        if next_in_line:
            RSVP.objects.create(user=next_in_line.user, event=event)
            send_waitlist_promoted.delay(next_in_line.user.email, event.title)
            next_in_line.delete() 

    @action(detail=False, methods=['get'])
    def my_rsvps(self, request):
        rsvps = RSVP.objects.filter(user=request.user).order_by('created_at')
        serializer = self.get_serializer(rsvps, many=True)
        return Response(serializer.data)     

        

class WaitlistViewSet(viewsets.ModelViewSet):
    queryset = Waitlist.objects.all().order_by('created_at')
    serializer_class = WaitlistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        entry = serializer .save(user=self.request.user)
        position = Waitlist.objects.filter(
            event=entry.event,
            created_at__lte=entry.created_at
        ).count()
        send_waitlist_confirmation.delay(
                entry.user.email,
                entry.event.title,
                position
                )
        
    @action(detail=False, methods = ['get'])
    def my_position(self, request):
        event_id = request.query_params.get('event_id')
        waitlist = Waitlist.objects.filter(event_id=event_id).order_by('created_at')
        for position, entry in enumerate(waitlist, start=1):
            if entry.user == request.user:
                return Response ({'position': position})

        return Response({'message': 'You are not on the waitlist for this event.'})

    @action(detail=False, methods=['get'])
    def my_waitlist(self, request):
        entries = Waitlist.objects.filter(user=request.user).order_by('created_at')
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)
    

