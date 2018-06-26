from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse
import json
from app.forms import travel_form
from app.models import Travel, Locations,Notification ,TravelBoundRelation,Attendee,Group,GeneralTag,TravelTag,TravelAttendee,Answers, SessionRating, Setting
from django.http import Http404
import datetime

from app.views.gbhelper.editor_helper import EditorHelper
from .common_views import GroupView, EventView
from django.db.models import Max, Avg, Count
from publicfront.views.profile import SessionDetail
from django.db.models import Q, Max
from django.db import transaction
from app.views.gbhelper.language_helper import LanguageH


class TravelView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'travel_permission'):
            travel_groups = GroupView.get_travelGroup(request)
            for group in travel_groups:
                group.travels = Travel.objects.all().filter(group_id=group.id).order_by('travel_order')
                for travel in group.travels:
                    travel.in_queue = TravelAttendee.objects.filter(travel_id=travel.id, status='in-queue').count()
                    travel.attending = TravelAttendee.objects.filter(travel_id=travel.id, status='attending').count()
                    travel.not_attending = TravelAttendee.objects.filter(travel_id=travel.id, status='not-attending').count()
            locationGroup = GroupView.get_locationGroup(request)
            for group in locationGroup:
                group.locations = Locations.objects.all().filter(group_id=group.id)

            context = {
                'locationGroup': locationGroup,
                'travel_groups':travel_groups

            }
            editor_common_context = EditorHelper.get_editor_context(request, max_height=200)
            context.update(editor_common_context)
            context.update(LanguageH.get_current_and_all_presets(request))
            return render(request, 'travel/travel.html', context)
        else:
            raise Http404

    def post(self, request):
        if EventView.check_permissions(request, 'travel_permission'):
            form_data = {
                "description": request.POST.get('description'),
                "group_id": request.POST.get('group'),
                "departure_city": request.POST.get('departure_city'),
                "arrival_city": request.POST.get('arrival_city'),
                "departure":request.POST.get('departure'),
                "arrival": request.POST.get('arrival'),
                "reg_between_start": request.POST.get('reg_between_start'),
                "reg_between_end": request.POST.get('reg_between_end'),
                "max_attendees": request.POST.get('max_attendees'),
                "allow_attendees_queue": request.POST.get('allow_attendees_queue') == 'true',
                "location_id": request.POST.get('location'),
                "travel_bound": request.POST.get('travel_bound')
            }
            # tags = request.POST.get('tags')
            allow_attendees_queue = request.POST.get('allow_attendees_queue')
            form_data['allow_attendees_queue'] = False
            if allow_attendees_queue == '1':
                form_data['allow_attendees_queue'] = True

            travel_bound_list = json.loads(request.POST.get('travel_bound_list'))
            event_id=request.session['event_auth_user']['event_id']
            current_language_id = LanguageH.get_current_language_id(event_id)
            default_language_id = current_language_id
            name_lang = request.POST.get('name_lang')
            description_lang = request.POST.get('description_lang')
            if 'id' in request.POST:
                response = {}
                current_language_id = request.POST.get('current_language_id')
                if current_language_id == default_language_id:
                    form_data["name"] = request.POST.get('name')
                travel_id = request.POST.get('id')
                travel_old = Travel.objects.get(id=travel_id)
                form_data = LanguageH.update_lang(current_language_id, form_data, "name_lang", name_lang,
                                                  travel_old.name_lang)
                form_data = LanguageH.update_lang(current_language_id, form_data, "description_lang",
                                                  description_lang, travel_old.description_lang)
                form = travel_form.TravelForm(request.POST, instance=travel_old)
                if form.is_valid():
                    # old_capacity = travel_old.max_attendees
                    # if old_capacity < int(request.POST.get('max_attendees')):
                    #     new_capacity = int(request.POST.get('max_attendees'))
                    #     increased_capacity = new_capacity - old_capacity
                    #     attendees_in_queue = TravelAttendee.objects.filter(travel_id=travel_id,status="in-queue")[:increased_capacity]
                        # for attendee_in_queue in attendees_in_queue:
                        #     SessionDetail.notify_queue_user(session_id,attendee_in_queue.attendee_id)


                    Travel.objects.filter(id=travel_id).update(**form_data)
                    # TravelTag.objects.filter(travel_id=travel_id).delete()
                    # travel_tags = tags.split(',')
                    # for tag in travel_tags:
                    #     tag_id = tag
                    #     if tag.strip() !="" and tag !=None:
                    #         if not tag.isdigit():
                    #             general_tag = GeneralTag(name=tag, category='travel',event_id=event_id)
                    #             general_tag.save()
                    #             tag_id = general_tag.id
                    #         travel_tag_form_data = {
                    #             "travel_id" : travel_id,
                    #             "tag_id": tag_id
                    #         }
                    #         travel_tag = TravelTag(**travel_tag_form_data)
                    #         travel_tag.save()
                    travel = Travel.objects.get(id=travel_id)
                    bound_exist = []
                    if form_data['travel_bound'] == 'homebound':
                        for bound_travel in travel_bound_list:
                            if not (TravelBoundRelation.objects.filter(travel_homebound_id=travel.id, travel_outbound_id=bound_travel).exists()):
                                bound = TravelBoundRelation(travel_homebound_id=travel.id, travel_outbound_id=bound_travel)
                                bound.save()
                            bound_exist.append(bound_travel)
                        deleted_relation = TravelBoundRelation.objects.filter(travel_homebound_id=travel.id).exclude(travel_outbound_id__in=bound_exist)
                        for bound in deleted_relation:
                            bound.delete()
                    else:
                        for bound_travel in travel_bound_list:
                            if not (TravelBoundRelation.objects.filter(travel_outbound_id=travel.id, travel_homebound_id=bound_travel).exists()):
                                bound = TravelBoundRelation(travel_homebound_id=bound_travel, travel_outbound_id=travel.id)
                                bound.save()
                            bound_exist.append(bound_travel)
                        deleted_relation = TravelBoundRelation.objects.filter(travel_outbound_id=travel.id).exclude(travel_homebound_id__in=bound_exist)
                        for bound in deleted_relation:
                            bound.delete()
                    updated_session = TravelView.get_updated_travel(travel)
                    response['success'] = True
                    response['message'] = "Travel Updated"
                    response['travel'] = updated_session
                else:
                    response['success'] = False
                    response['message'] = form.errors
                return HttpResponse(json.dumps(response))
            else:
                form_data["name"] = request.POST.get('name')
                travel_order = TravelView.get_travels_order(request.POST.get('group'))
                form_data["travel_order"] = travel_order
                response = {}
                form_data = LanguageH.insert_lang(current_language_id, form_data, "name_lang", name_lang)
                form_data = LanguageH.insert_lang(current_language_id, form_data, "description_lang",description_lang)
                form = travel_form.TravelForm(request.POST or None)
                if form.is_valid():
                    travel = Travel(**form_data)
                    travel.save()
                    # travel_tags = tags.split(',')
                    # for tag in travel_tags:
                    #     if tag.strip() !="" and tag !=None:
                    #         tag_id = tag
                    #         if not tag.isdigit():
                    #             general_tag = GeneralTag(name=tag, category='travel',event_id=event_id)
                    #             general_tag.save()
                    #             tag_id = general_tag.id
                    #         travel_tag_form_data = {
                    #             "travel_id" : travel.id,
                    #             "tag_id": tag_id
                    #         }
                    #         travel_tag = TravelTag(**travel_tag_form_data)
                    #         travel_tag.save()
                    if form_data['travel_bound'] == 'homebound':
                        for bound_travel in travel_bound_list:
                            bound = TravelBoundRelation(travel_homebound_id=travel.id, travel_outbound_id=bound_travel)
                            bound.save()
                    else:
                        for bound_travel in travel_bound_list:
                            bound = TravelBoundRelation(travel_homebound_id=bound_travel, travel_outbound_id=travel.id)
                            bound.save()
                    updated_session = TravelView.get_updated_travel(travel)
                    response['success'] = True
                    response['message'] = "Travel Created"
                    response['travel'] = updated_session
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
        if EventView.check_permissions(request, 'travel_permission'):
            try:
                id = request.POST.get('id')
                travel = Travel.objects.get(id=id)
                travel.delete()
                response_data['success'] = 'Travel Deleted Successfully'
            except Exception as exception:
                print('Exception occured to delete travel.')
                print(exception)
                response_data['error'] = 'You do not have Permission to do this'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def remove_queue(request):
    #     response_data = {}
    #     travel_attendee_id = request.POST.get('travel_attendee_id')
    #     travel_id = request.POST.get('travel_id')
    #     if travel_attendee_id == 'all':
    #         travel = TravelAttendee.objects.filter(travel_id=travel_id,status="in-queue").delete()
    #         # notifications = Notification.objects.filter(new_session_id=session_id,type="session",status=0).update(status=1)
    #     else:
    #         travel_user = TravelAttendee.objects.get(id=travel_attendee_id)
    #         # notifications = Notification.objects.filter(to_attendee_id=seminar_user.attendee_id,new_session_id=session_id,type="session",status=0).update(status=1)
    #         TravelAttendee.objects.filter(id=travel_attendee_id).delete()
    #     total_queue = TravelAttendee.objects.filter(travel_id=travel_id,status="in-queue").count()
    #     response_data['total_queue'] = total_queue
    #     response_data['success'] = 'Queue Removed Successfully'
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_tags(request):
        response_data = {}
        val = request.POST.get('q')
        event_id=request.session['event_auth_user']['event_id']
        tags = GeneralTag.objects.values('name', 'id').filter(name__icontains=val, category='travel',event_id=event_id)
        my_data = []
        for tag in tags:
            arr_data = {
                'id': tag['id'],
                'text': tag['name']
            }
            my_data.append(arr_data)
        response_data['results'] = my_data
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # def travel_queue(request):
    #     travel_id = request.POST.get('travel_id')
    #     travel = Travel.objects.get(id=travel_id)
    #     attendee_queue = TravelAttendee.objects.filter(travel_id = travel_id, status = 'in-queue').order_by('queue_order')
    #     for user in attendee_queue:
    #         first_name = Answers.objects.filter(question_id=68, user_id=user.attendee_id)
    #         last_name = Answers.objects.filter(question_id=69, user_id=user.attendee_id)
    #         if first_name.exists():
    #             user.attendee.firstname = first_name[0].value
    #         if last_name.exists():
    #             user.attendee.lastname = last_name[0].value
    #     context = {
    #         "attendee_queue": attendee_queue,
    #         "travel": travel
    #     }
    #     return render(request, 'travel/edit_travel_queue.html', context)

    # def travel_deciding(request):
    #     travel_id = request.POST.get('travel_id')
    #     travel = Travel.objects.get(id=travel_id)
    #     attendee_deciding = TravelAttendee.objects.filter(travel_id = travel_id, status = 'deciding').order_by('queue_order')
    #     for user in attendee_deciding:
    #         session_timeout = Setting.objects.filter(name='notification_timeout')
    #         timeout = '0:05'
    #         if session_timeout.exists():
    #             timeout = session_timeout[0].value
    #         times = timeout.split(':')
    #         minutes = int(times[0])*60 + int(times[1])
    #         end_time = user.created + datetime.timedelta(minutes = minutes)
    #         difference = end_time - datetime.datetime.now()
    #         s = difference.total_seconds()
    #         # hours
    #         hours = s // 3600
    #         # remaining seconds
    #         s = s - (hours * 3600)
    #         # minutes
    #         minutes = s // 60
    #         # remaining seconds
    #         seconds = s - (minutes * 60)
    #         user.hours = int(hours)
    #         user.minutes = int(minutes)
    #         first_name = Answers.objects.filter(question_id=68, user_id=user.attendee_id)
    #         last_name = Answers.objects.filter(question_id=69, user_id=user.attendee_id)
    #         if first_name.exists():
    #             user.attendee.firstname = first_name[0].value
    #         if last_name.exists():
    #             user.attendee.lastname = last_name[0].value
    #     context = {
    #         "attendee_deciding": attendee_deciding,
    #         "travel": travel
    #     }
    #     return render(request, 'travel/edit_travel_deciding.html', context)


    # def queue_order(request):
    #     response_data = {}
    #     queue_order = json.loads(request.POST.get('queue_order'))
    #     travel_id = request.POST.get('travel_id')
    #     for queue in queue_order:
    #         TravelAttendee.objects.filter(id=queue['travel_id']).update(queue_order=queue['order'])
    #     response_data['success'] = 'Travel Queue Ordered Successfully'
    #     return HttpResponse(json.dumps(response_data), content_type="application/json")


    def travel_search(request):
        search_key = request.POST.get('search_key')
        all_travel_groups = []

        if search_key :
           travel_group = Group.objects.filter(Q(type="travel",is_show=1, event_id=request.session['event_auth_user']['event_id']) & (Q(travel__name__icontains=search_key))).order_by('group_order').distinct()
        else :
            travel_group = Group.objects.filter(Q(type="travel",is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by('group_order').distinct()

        for group in travel_group:
            group.travel = Travel.objects.filter(Q(group_id=group.id)&(Q(name__icontains=search_key))).order_by('travel_order')
            for travel in group.travel:
                travel.in_queue = TravelAttendee.objects.filter(travel_id=travel.id, status='in-queue').count()
                travel.attending = TravelAttendee.objects.filter(travel_id=travel.id, status='attending').count()
                travel.not_attending = TravelAttendee.objects.filter(travel_id=travel.id, status='not-attending').count()
            group_dict = dict(
                id=group.id,
                name=group.name,
                travel=group.travel
            )
            all_travel_groups.append(group_dict)


        data = {
                'travel_groups': all_travel_groups
            }
        return render(request, 'travel/travel_result.html', data)

    def get_updated_travel(travel):
        updated_travel = travel.as_dict()
        updated_travel['in_queue'] = TravelAttendee.objects.filter(travel_id=travel.id, status='in-queue').count()
        updated_travel['attending'] = TravelAttendee.objects.filter(travel_id=travel.id, status='attending').count()
        updated_travel['not_attending'] = TravelAttendee.objects.filter(travel_id=travel.id, status='not-attending').count()
        return updated_travel

    def travel_get_bound(request):
        bound = request.POST.get('bound')
        group_id = request.POST.get('group')
        travel_id = request.POST.get('travel_id')
        travel_group = Group.objects.get(id=group_id)
        if bound == 'homebound':
            if travel_id == '':
                travel_group.travels = Travel.objects.filter(travel_bound='outbound', group_id=group_id)
            else:
                travel_group.travels = Travel.objects.filter(travel_bound='outbound', group_id=group_id).exclude(id=travel_id)
            travel_bound = "Travel Outbound"
        else:
            if travel_id == '':
                travel_group.travels = Travel.objects.filter(travel_bound='homebound', group_id=group_id)
            else:
                travel_group.travels = Travel.objects.filter(travel_bound='homebound', group_id=group_id).exclude(id=travel_id)
            travel_bound = "Travel Homebound"
        context = {
            'travel_group': travel_group,
            'travel_bound': travel_bound
        }
        return render(request, 'travel/travel_bound.html', context)

    def set_travels_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'travel_permission'):
            travels_order = json.loads(request.POST.get('travels_order'))
            for travel in travels_order:
                Travel.objects.filter(id=travel['travel_id']).update(travel_order=travel['order'])
            response_data['success'] = 'Travels Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_travels_order(group_id):
        travel = Travel.objects.values('travel_order').filter(group_id = group_id).aggregate(Max('travel_order'))
        if travel['travel_order__max']:
            travel_order = travel['travel_order__max'] + 1
        else:
            travel_order = 1
        return travel_order

    def get_homebound_travel(request):
        travel_id = request.POST.get('travel_id')
        homebound_list =[]
        homebound_travel = TravelBoundRelation.objects.filter(travel_outbound_id=travel_id)
        for h_travel in homebound_travel:
            homebound_list.append(h_travel.travel_homebound_id)
        travels = Travel.objects.filter(id__in=homebound_list)
        travels_list = []
        for travel in travels:
            travels_list.append(travel.as_dict())
        response_data = {
            'homebound_flights': travels_list
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")




class TravelDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return Travel.objects.get(pk=pk)
        except Travel.DoesNotExist:
            raise Http404


    def get(self, request, pk, format=None):
        travel = self.get_object(pk)
        # travel_tags = TravelTag.objects.filter(travel_id = pk)
        # tags = []
        # for tag in travel_tags:
        #     tag_data ={}
        #     tag_data['id']=tag.tag.id
        #     tag_data['text']=tag.tag.name
        #     tags.append(tag_data)

        if travel.travel_bound == 'homebound':
            travel_bounds = TravelBoundRelation.objects.filter(travel_homebound_id=travel.id)
            all_bounds = Travel.objects.filter(travel_bound='outbound', group_id=travel.group_id)
            bound_name = "Travel OutBound"
        else:
            travel_bounds = TravelBoundRelation.objects.filter(travel_outbound_id=travel.id)
            all_bounds = Travel.objects.filter(travel_bound='homebound', group_id=travel.group_id)
            bound_name = "Travel HomeBound"

        all_bound_list = []
        for bound in all_bounds:
            all_bound_list.append(bound.as_dict())
        travel_bound_list = []
        for bound in travel_bounds:
            travel_bound_list.append(bound.as_dict())
        event_id = request.session['event_auth_user']['event_id']
        current_language_id = LanguageH.get_current_language_id(event_id)
        response = {
            'success': True,
            'travel': travel.as_dict(),
            # 'tags': tags,
            'travel_bound_list': travel_bound_list,
            'bound_name': bound_name,
            'all_bound_list': all_bound_list,
            'current_language_id': current_language_id
        }
        return HttpResponse(json.dumps(response), content_type='application/json')