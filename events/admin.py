from django.contrib import admin
from .models import Event, RSVP, Waitlist
# Register your models here.
admin.site.register(Event)
admin.site.register(RSVP)
admin.site.register(Waitlist)