from django import forms
from app.models import Locations


class LocationForm(forms.ModelForm):
    class Meta:
        model = Locations
        fields = ['name', 'description', 'group', 'address', 'latitude', 'longitude', 'contact_name', 'contact_web',
                  'contact_email', 'contact_phone', 'map_highlight']


        


