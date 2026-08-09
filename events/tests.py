from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Event, RSVP, Waitlist


class EventRSVPTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='testpass123')
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

        self.event = Event.objects.create(
            title='Test Event',
            description='A test event',
            location='New York',
            date=timezone.now() + timedelta(days=7),
            created_by=self.owner,
            max_attendees=1,
        )

    def test_rsvp_creation(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/rsvps/', {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RSVP.objects.filter(event=self.event, user=self.user1).count(), 1)

    def test_duplicate_rsvp_blocked(self):
        RSVP.objects.create(event=self.event, user=self.user1)
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/rsvps/', {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rsvp_blocked_when_event_full(self):
        RSVP.objects.create(event=self.event, user=self.user1)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/api/rsvps/', {'event': self.event.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('full', str(response.data))

    def test_waitlist_promotion_on_rsvp_delete(self):
        rsvp = RSVP.objects.create(event=self.event, user=self.user1)
        waitlist_entry = Waitlist.objects.create(event=self.event, user=self.user2)

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f'/api/rsvps/{rsvp.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(RSVP.objects.filter(event=self.event, user=self.user2).exists())
        self.assertFalse(Waitlist.objects.filter(id=waitlist_entry.id).exists())

    def test_only_owner_can_cancel_event(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(f'/api/events/{self.event.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_cancel_event(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(f'/api/events/{self.event.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_cancelled)