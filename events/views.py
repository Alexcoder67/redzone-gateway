from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Event, RSVP, Waitlist
from .serializers import EventSerializer, RSVPSerializer, WaitlistSerializer
from rest_framework import filters
from .permissions import IsOwnerOrReadOnly

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

class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class WaitlistViewSet(viewsets.ModelViewSet):
    queryset = Waitlist.objects.all().order_by('created_at')
    serializer_class = WaitlistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)