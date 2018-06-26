from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
import json
from app.forms import location_form
from app.models import Locations,Group
from django.http import Http404

from app.views.gbhelper.editor_helper import EditorHelper
from .common_views import GroupView, EventView
from django.db.models import Q, Max
from app.views.gbhelper.language_helper import LanguageH


class LocationView(generic.DetailView):

    def get(self, request):
        if EventView.check_read_permissions(request, 'location_permission'):
            locationGroup = GroupView.get_locationGroup(request)
            for group in locationGroup:
                group.locations = Locations.objects.all().filter(group_id=group.id).order_by('location_order')
            context = {
                'locationGroup': locationGroup
            }
            editor_common_context = EditorHelper.get_editor_context(request, max_height=200)
            context.update(editor_common_context)
            context.update(LanguageH.get_current_and_all_presets(request))
            return render(request, 'location/location.html', context)

    def post(self, request):
        response = {}
        if EventView.check_permissions(request, 'location_permission'):
            event_id = request.session['event_auth_user']['event_id']
            show_map_highlight_data = request.POST.get('show_map_highlight')
            show_contact_name_data = request.POST.get('show_contact_name')
            show_contact_web_data = request.POST.get('show_contact_web')
            show_contact_phone_data = request.POST.get('show_contact_phone')
            show_contact_email_data = request.POST.get('show_contact_email')
            show_map_highlight = False
            show_contact_name = False
            show_contact_web = False
            show_contact_phone = False
            show_contact_email = False
            if show_map_highlight_data=="true":
                show_map_highlight = True
            if show_contact_name_data=="true":
                show_contact_name = True
            if show_contact_web_data=="true":
                show_contact_web = True
            if show_contact_phone_data=="true":
                show_contact_phone = True
            if show_contact_email_data=="true":
                show_contact_email = True
            form_data = {
                "description": request.POST.get('description'),
                "address": request.POST.get('address'),
                "group_id": request.POST.get('group'),
                "latitude": request.POST.get('latitude'),
                "longitude": request.POST.get('longitude'),
                "show_map_highlight": show_map_highlight,
                "show_contact_name": show_contact_name,
                "show_contact_web": show_contact_web,
                "show_contact_phone": show_contact_phone,
                "show_contact_email": show_contact_email
            }
            if "map_highlight" in request.POST:
                form_data["map_highlight"] = request.POST.get('map_highlight')
            if "contact_name" in request.POST:
                form_data["contact_name"] = request.POST.get('contact_name')
            if "contact_web" in request.POST:
                form_data["contact_web"] = request.POST.get('contact_web')
            if "contact_phone" in request.POST:
                form_data["contact_phone"] = request.POST.get('contact_phone')
            if "contact_email" in request.POST:
                form_data["contact_email"] = request.POST.get('contact_email')
            current_language_id = LanguageH.get_current_language_id(event_id)
            default_language_id = current_language_id
            name_lang = request.POST.get('name_lang')
            description_lang = request.POST.get('description_lang')
            address_lang = request.POST.get('address_lang')
            contact_name_lang = request.POST.get('contact_name_lang')
            if 'id' in request.POST:
                location_id = request.POST.get('id')
                current_language_id = request.POST.get('current_language_id')
                if current_language_id == default_language_id:
                    form_data["name"] = request.POST.get('name')
                duplicate_existance = Locations.objects.filter(name=request.POST.get('name'),
                                                               group__event_id=request.session['event_auth_user'][
                                                                   'event_id']).exclude(id=location_id)
                if duplicate_existance.exists():
                    response['success'] = False
                    response['message'] = 'This location name is already exist.'
                    return HttpResponse(json.dumps(response))

                location_old = Locations.objects.get(id=location_id)
                # form_data_lang = [{
                #     "lang_key": "name_lang",
                #     "lang_value": name_lang,
                #     "current_lang": location_old.name_lang
                # },{
                #     "lang_key": "description_lang",
                #     "lang_value": description_lang,
                #     "current_lang": location_old.description_lang
                # },{
                #     "lang_key": "address_lang",
                #     "lang_value": address_lang,
                #     "current_lang": location_old.address_lang
                # },{
                #     "lang_key": "contact_name_lang",
                #     "lang_value": contact_name_lang,
                #     "current_lang": location_old.contact_name_lang
                # }]
                # form_data = LanguageH.update_lang(current_language_id, form_data, form_data_lang)

                form_data = LanguageH.update_lang(current_language_id, form_data, "name_lang", name_lang,
                                                  location_old.name_lang)
                form_data = LanguageH.update_lang(current_language_id, form_data, "description_lang",
                                                  description_lang, location_old.description_lang)
                form_data = LanguageH.update_lang(current_language_id, form_data, "address_lang",
                                                  address_lang, location_old.address_lang)
                form_data = LanguageH.update_lang(current_language_id, form_data, "contact_name_lang",
                                                  contact_name_lang, location_old.contact_name_lang)
                form = location_form.LocationForm(request.POST, instance=location_old)
                if form.is_valid():
                    Locations.objects.filter(id=location_id).update(**form_data)
                    location = Locations.objects.get(id=location_id)
                    response['success'] = True
                    response['message'] = "Location Updated"
                    response['location'] = location.as_dict()
                else:
                    response['success'] = False
                    response['message'] = form.errors
                return HttpResponse(json.dumps(response))
            else:
                form_data["name"] = request.POST.get('name')
                duplicate_existance = Locations.objects.filter(name=form_data['name'], group__event_id=request.session['event_auth_user']['event_id'])
                if duplicate_existance.exists():
                    response['success'] = False
                    response['message'] = 'This location name is already exist.'
                    return HttpResponse(json.dumps(response))

                form_data = LanguageH.insert_lang(current_language_id, form_data, "name_lang", name_lang)
                form_data = LanguageH.insert_lang(current_language_id, form_data, "description_lang", description_lang)
                form_data = LanguageH.insert_lang(current_language_id, form_data, "address_lang", address_lang)
                form_data = LanguageH.insert_lang(current_language_id, form_data, "contact_name_lang", contact_name_lang)
                location_order = LocationView.get_locations_order(request.POST.get('group'))
                form_data["location_order"] = location_order
                form = location_form.LocationForm(request.POST or None)
                if form.is_valid():
                    location = Locations(**form_data)
                    location.save()
                    response['success'] = True
                    response['message'] = "Location Created"
                    response['location'] = location.as_dict()
                else:
                    response['success'] = False
                    response['message'] = form.errors
                return HttpResponse(json.dumps(response))
        else:
            response = {}
            response['error'] = 'You do not have Permission to do this'
            return HttpResponse(json.dumps(response))

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'location_permission'):
            location_id = request.POST.get('id')
            location = Locations.objects.get(id=location_id)
            location.delete()
            response_data = {
                'success': True,
                'message': 'Location Deleted'

            }
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def search(request):
        search_key = request.POST.get('search_key')
        all_locations_groups = []
        if search_key:
            locations_group = Group.objects.filter(Q(type="location", is_show=1, event_id=request.session['event_auth_user']['event_id']) & (Q(locations__name__icontains=search_key))).order_by('group_order').distinct()
        else:
            locations_group = Group.objects.filter(Q(type="location",is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by('group_order').distinct()
        for group in locations_group:
            group.location = Locations.objects.filter(Q(group_id=group.id)& Q(name__icontains=search_key)).order_by('location_order')
            group_dict = dict(
                id=group.id,
                name=group.name,
                location=group.location
            )
            all_locations_groups.append(group_dict)
        data = {
                'locationsGroups': all_locations_groups
            }
        return render(request, 'location/location_result.html', data)

    def location_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        if EventView.check_permissions(request, 'location_permission'):
            location_id = request.POST.get('location_id')
            location = Locations.objects.get(id=location_id)

            duplicate_existance = Locations.objects.filter(name=location.name + '[Copy]', group__event_id=event_id)
            if duplicate_existance.exists():
                response_data['error'] = 'This location is already make a duplicate.'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            location.pk = None
            # if '[Copy]' not in session.name:
            location.name += '[Copy]'
            location.save()
            response_data['success'] = "Create duplicate location Successfully"
            response_data['location'] = location.as_dict()
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def set_locations_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'location_permission'):
            locations_order = json.loads(request.POST.get('locations_order'))
            for location in locations_order:
                Locations.objects.filter(id=location['location_id']).update(location_order=location['order'])
            response_data['success'] = 'Locations Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_locations_order(group_id):
        location = Locations.objects.values('location_order').filter(group_id = group_id).aggregate(Max('location_order'))
        if location['location_order__max']:
             location_order = location['location_order__max'] + 1
        else:
            location_order = 1
        return location_order



class LocationDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return Locations.objects.get(pk=pk)
        except Locations.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        location = self.get_object(pk)
        event_id = request.session['event_auth_user']['event_id']
        current_language_id = LanguageH.get_current_language_id(event_id)
        response = {
            'success': True,
            'location': location.as_dict(),
            'current_language_id': current_language_id
        }
        return HttpResponse(json.dumps(response), content_type='application/json')