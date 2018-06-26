from django import forms
from app.models import Session


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'group', 'start', 'end', 'reg_between_start', 'reg_between_end',
                  'allow_attendees_queue', 'location']
