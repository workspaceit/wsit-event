from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Users, Attendee, EventAdmin, ContentType, Group, Events, ContentPermission, GroupPermission
import json
from datetime import datetime
from django.http import Http404
from django.views.generic import TemplateView
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.db.models import Value as V
from django.db.models.functions import Concat
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.gbhelper.language_helper import LanguageH


class AdminView(TemplateView):
    def get(self, request):
        if request.session['event_auth_user']['type'] == 'super_admin':
            admins = Users.objects.filter(type="admin")
            context = {
             'admins':admins
            }
            return render(request, 'admin/admins.html', context)
        else:
            # return render(request, 'dashboard/index.html')
            return render(request, 'dashboard/index_test.html')

    @transaction.atomic
    def post(self, request):
        response_data = {}
        form_data = {
            "firstname": request.POST.get('firstname'),
            "lastname": request.POST.get('lastname'),
            "email": request.POST.get('email'),
            "phonenumber": request.POST.get('phonenumber'),
            "company": request.POST.get('company')
        }
        events = request.POST.get('events').split(',')
        permissions = json.loads(request.POST.get('permissions'))
        password = request.POST.get('password')
        if 'id' in request.POST:
            user_id = request.POST.get('id')
            if not (Users.objects.filter(email=form_data['email']).exclude(id=user_id).exists()):
                form_data["updated"] = datetime.now()
                form_data["type"] = "admin"
                if password != '':
                    form_data["password"] = make_password(password)
                Users.objects.filter(id=user_id).update(**form_data)
                admin = Users.objects.get(id=user_id)
                event_exist = []
                for event_id in events:
                    event_exist.append(event_id)
                    if not (EventAdmin.objects.filter(admin_id=admin.id, event_id=event_id).exists()):
                        event_form_data = {
                            "event_id" : event_id,
                            "admin_id" : admin.id
                        }
                        event_permission = EventAdmin(**event_form_data)
                        event_permission.save()

                ErrorR.ex_time_init()
                deleted_event = EventAdmin.objects.filter(admin_id=admin.id).exclude(event_id__in=event_exist).delete()
                # for event in deleted_event:
                #     event.delete()
                ErrorR.ex_time()
                admin_id = user_id
                delete_content = ContentPermission.objects.filter(admin_id=admin_id).delete()
                delete_group = GroupPermission.objects.filter(admin_id=admin_id).delete()
                for permission in permissions:
                    content_event = permission['event_id']
                    for content in permission['contents']:
                        content_permission = ContentPermission(content=content['content'], access_level=content['access'], admin_id=admin_id, event_id=content_event)
                        content_permission.save()
                    for question in permission['questions']:
                        group_permission = GroupPermission(access_level=question['access'], admin_id=admin_id, group_id=question['group_id'])
                        group_permission.save()
                response_data = {
                    "success":"Admin Update Successfully",
                    "admin":admin.as_dict()
                }
                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['error'] = 'email already Exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")
        else:
            if not (Users.objects.filter(email=form_data['email']).exists()):
                form_data["updated"] = datetime.now()
                form_data["type"] = "admin"
                form_data["password"] = make_password(password)
                user = Users(**form_data)
                user.save()

                for event_id in events:
                    event_form_data = {
                        "event_id" : event_id,
                        "admin_id" : user.id
                    }
                    event_permission = EventAdmin(**event_form_data)
                    event_permission.save()
                admin_id = user.id
                for permission in permissions:
                    content_event = permission['event_id']
                    for content in permission['contents']:
                        content_permission = ContentPermission(content=content['content'], access_level=content['access'], admin_id=admin_id, event_id=content_event)
                        content_permission.save()
                    for question in permission['questions']:
                        group_permission = GroupPermission(access_level=question['access'], admin_id=admin_id, group_id=question['group_id'])
                        group_permission.save()
                response_data = {
                    "success":"Admin Create Successfully",
                    "admin":user.as_dict()
                }


                return HttpResponse(json.dumps(response_data), content_type="application/json")
            else:
                response_data['error'] = 'email already Exist'
                return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete(request):
        response_data = {}
        id = request.POST.get('id')
        attendee = Attendee.objects.get(id=id)
        attendee.delete()
        response_data['success'] = 'Attendee Deleted Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def admin_search(request):
        search_key = request.POST.get('search_key')
        if search_key :
            admins = Users.objects.annotate(fullname=Concat('firstname',V(' ') ,'lastname')).filter(Q(type="admin") & (Q(firstname__icontains=search_key) | Q(lastname__icontains=search_key) | Q(email__icontains=search_key) | Q(fullname__icontains=search_key)))
        else :
            admins = Users.objects.filter(Q(type="admin"))
        data = {
                'admins': admins
            }
        return render(request, 'admin/admin_result.html', data)

    def change_status(request):
        id = request.POST.get('id')
        status = request.POST.get('status')
        user = Users.objects.get(id=id)
        if status=="active":
          user.status="active"
        elif status=="inactive":
          user.status="inactive"
        user.save()
        response_data = {
                    "success":True,
                    "admin":user.as_dict()
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def render_permission(request):
        id = request.POST.get('id')
        contents = [
            'event',
            'attendee',
            'deleted_attendee',
            'session',
            'question',
            'travel',
            'location',
            'hotel',
            'page',
            'menu',
            'template',
            'css',
            'filter',
            'export_filter',
            'photo_reel',
            'message',
            'file_browser',
            'checkpoints',
            'language',
            'economy',
            'setting',
            'assign_session',
            'assign_travel',
            'assign_hotel',
            'group_registration'
        ]

        question_grp = Group.objects.filter(type="question",is_show=1,event_id=id)
        data = {
            "event":Events.objects.get(id=id),
            "contents":contents,
            "question_groups":question_grp

        }

        return render(request, 'admin/permission_partial.html', data)


class AdminDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            if self.request.session['event_auth_user']['type'] == 'super_admin':
                return Users.objects.filter(id=pk)
            else:
                raise Http404
        except Users.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        events = EventAdmin.objects.filter(admin_id=pk)
        event_list = []
        for event in events:
            event_data ={}
            event_data['id']=event.event.id
            event_data['text']=event.event.name
            event_list.append(event_data)

        content_permission_list = []
        group_permission_list = []
        content_permission = ContentPermission.objects.filter(admin_id = pk)
        for content in content_permission:
            content_permission_list.append(content.as_dict())
        group_permission = GroupPermission.objects.filter(admin_id = pk)
        for group in group_permission:
            group_permission_list.append(group.as_dict())
        data = {
            'user': user[0].as_dict(),
            'events': event_list,
            'content_permission': content_permission_list,
            'group_permission': group_permission_list,
            'success':True
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


