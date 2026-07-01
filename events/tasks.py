from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_rsvp_confirmation(user_email, event_title):
    send_mail(
        f"RSVP Confirmation for {event_title}",
        f"You have successfully RSVP'd to {event_title}.",
        'fanaticfanduel009@gmail.com',
        [user_email],
    )

@shared_task
def send_waitlist_confirmation(user_email, event_title, position):
    send_mail(
        f"You're now on the Waitlist for {event_title}!",
        f"You have been added to the waitlist for {event_title}. Your current position is #{position}. Good Luck!",
        'fanaticfanduel009@gmail.com',
        [user_email],
    )

@shared_task
def send_waitlist_promoted(user_email, event_title):
    send_mail(
        f"You're now confirmed for {event_title}!",
        f"Good news! A spot has opened up and you have been moved from the waitlist and confirmed for {event_title}. We look forward to seeing you there!",
        'fanaticfanduel009@gmail.com',
        [user_email],
    )
