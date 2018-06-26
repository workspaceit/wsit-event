from django import forms
from app.models import Travel


class TravelForm(forms.ModelForm):
    class Meta:
        model = Travel
        fields = ['name', 'description', 'group', 'departure', 'arrival', 'reg_between_start', 'reg_between_end', 'max_attendees',
                  'allow_attendees_queue', 'location']
