from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Users, Attendee, Booking, RequestedBuddy, Group, Match, MatchLine
import json
from datetime import datetime
from django.http import Http404
from django.db.models import Q
from django.db import transaction


class MatchingView(generic.DetailView):
    def match(self):
        all_bookings = Booking.objects.all()
        for booking in all_bookings:
            all_bookings = all_bookings.exclude(id=booking.id)
            buddy_requests=RequestedBuddy.objects.filter(booking=booking)
            for buddy_request in buddy_requests:
                buddies=Attendee.objects.filter(Q())

        # print(all_bookings)
        return HttpResponse("sdfdsf")
        # return render(request, 'admin/admins.html')