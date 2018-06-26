from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from app.models import Scan, Attendee, Checkpoint
import json
from datetime import datetime


class ScanView(TemplateView):
    def get(self, request):
        scans = Scan.objects.all().order_by('-scan_time')
        event_id=request.session['event_auth_user']['event_id']
        checkpoints = Checkpoint.objects.filter(event_id=event_id)
        context = {
            'scans': scans,
            'checkpoints' : checkpoints
        }
        return render(request, 'scan/scan.html', context)

    def post(self, request):
        secret_key = request.POST.get('uid')
        attendee = Attendee.objects.filter(secret_key=secret_key)
        response_data = {}
        if attendee.count() == 0:
            response_data['exists'] = False
            response_data['time'] = str(datetime.now())
        else:
            scan = Scan(attendee=attendee[0])
            scan.save()
            time = str(scan.scan_time)
            count = Scan.objects.filter(attendee_id=attendee[0].id).count()
            attendee_data = {
                'uid': attendee[0].secret_key,
                'firstname': attendee[0].firstname,
                'lastname': attendee[0].lastname,
                'passed': count,
                'time': time
            }
            response_data['exists'] = True
            response_data['attendee'] = attendee_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")



