from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.views import generic
from app.models import Locations, Group
from django.db.models import Q
from django.template.loader import render_to_string
from publicfront.views.session_message import SessionMessageView

class LocationDetail(generic.DetailView):
    def get(self, request, pk, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            try:
                location = Locations.objects.get(id=pk)
                context = {
                    'location': location
                }
                location_detail = render_to_string('public/location/location_detail.html', context)
                location_data = SessionMessageView.get_default_template(request,location_detail)
                return HttpResponse(location_data)
            except Exception as e:
                raise Http404
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def post(self,request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            sort_type = request.POST.get('sort_type')
            all_locations_groups = []
            if sort_type== "all" :
                location_groups = Group.objects.filter(type="location", is_show=1, is_searchable=1, event_id=request.session['event_user']['event_id']).order_by('group_order')
                for group in location_groups:
                    group.location = Locations.objects.filter(group_id=group.id)
                    group_dict = dict(
                        id=group.id,
                        name=group.name,
                        location=group.location
                    )
                    all_locations_groups.append(group_dict)
            else :
                group_id = sort_type
                group = Group.objects.get(id=group_id)
                group.location = Locations.objects.filter(group_id=group_id)
                group_dict = dict(
                    id=group.id,
                    name=group.name,
                    location=group.location
                )
                all_locations_groups.append(group_dict)
        data = {
                'locationsGroups': all_locations_groups
            }
        return render(request, 'public/location/location_list.html', data)

    def search_location(request, *args, **kwargs):
        sort = request.GET.get('sort')
        search_key = request.GET.get('search_key')
        all_locations_groups = []
        if sort == 'all':
            locations_group = Group.objects.filter(Q(type="location", is_show=1, is_searchable=1, event_id=request.session['event_user']['event_id']) & (Q(locations__name__icontains=search_key) | Q(name__icontains=search_key))).order_by('group_order').distinct()
        else:
            locations_group = Group.objects.filter(Q(id=sort, is_show=1, is_searchable=1, event_id=request.session['event_user']['event_id']) & (Q(locations__name__icontains=search_key) | Q(name__icontains=search_key))).order_by('group_order').distinct()
        for group in locations_group:
            group.location = Locations.objects.filter(Q(group_id=group.id)&(Q(group__name__icontains=search_key) | Q(name__icontains=search_key)))
            group_dict = dict(
                id=group.id,
                name=group.name,
                location=group.location
            )
            all_locations_groups.append(group_dict)

        data = {
                'locationsGroups': all_locations_groups
            }
        return render(request, 'public/location/location_list.html', data)