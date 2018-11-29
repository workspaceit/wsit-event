from django.http import HttpResponse
from django.views import generic
from app.models import Users, Attendee, Booking, RequestedBuddy
from django.db.models import Q


class MatchingView(generic.DetailView):
    def match(self):
        all_bookings = Booking.objects.all()
        for booking in all_bookings:
            all_bookings = all_bookings.exclude(id=booking.id)
            buddy_requests=RequestedBuddy.objects.filter(booking=booking)
            for buddy_request in buddy_requests:
                buddies=Attendee.objects.filter(Q())
        return HttpResponse("sdfdsf")