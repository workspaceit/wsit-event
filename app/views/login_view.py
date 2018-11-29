from django.shortcuts import render, redirect
from django.views import generic
from app.models import Users, Events, ContentPermission, EventAdmin, GroupPermission, CurrentEvent, Attendee
from django.contrib.auth.hashers import check_password
import os


class Login(generic.DetailView):
    def get(self, request):
        if 'is_login' in request.session and request.session['is_login']:
            return redirect('index')
        else:
            return render(request, 'access/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = Users.objects.filter(email=email)
        if user.exists():
            if check_password(password, user[0].password):
                user = user.values()
                current = CurrentEvent.objects.filter(admin_id=user[0]['id'])
                if(current.count()>0):
                    event_id = current[0].event_id
                    event_name = current[0].event.name
                    event_url = current[0].event.url
                else:
                    if user[0]['type'] == 'super_admin':
                        event = Events.objects.all()[:1].get()
                        event_id = event.id
                        event_name= event.name
                        event_url = event.url
                    else:
                        event_access = EventAdmin.objects.filter(admin_id=user[0]['id'])
                        if event_access.count():
                            event = event_access[0]
                            event_id = event.event.id
                            event_name= event.event.name
                            event_url = event.event.url
                        else:
                            event = Events.objects.all()[:1].get()
                            event_id = event.id
                            event_name= event.name
                            event_url = event.url
                    current_event = CurrentEvent(event_id=event_id,admin_id=user[0]['id'])
                    current_event.save()

                base_url = 'http://127.0.0.1:8003/'+str(event_url)

                find_users_in_attendee=Attendee.objects.filter(event_id=event_id,email=user[0]['email'])
                is_attendee = False
                if find_users_in_attendee.exists():
                    is_attendee=True
                auth_user = {
                    "id": user[0]['id'],
                    "name": user[0]['firstname'] + ' ' + user[0]['lastname'],
                    "email": user[0]['email'],
                    "type": user[0]['type'],
                    "event_id": event_id,
                    "event_name": event_name,
                    "event_url": event_url,
                    "base_url": base_url,
                    "is_attendee":is_attendee
                }
                admin_permission = Login.get_admin_permissions(request,event_id,user[0]['id'])
                request.session['event_auth_user'] = auth_user
                request.session['is_login'] = True
                request.session['admin_permission'] = admin_permission
                return redirect('index')
            else:
                return render(request, 'access/login.html',
                              {'msg': 'Authenntication failed. Password Wrong. Try Again'})
        else:
            return render(request, 'access/login.html', {'msg': 'Authenntication failed.Wrong Email. Try Again'})

    def get_admin_permissions(request,event_id,admin_id):
        event_list = []
        group_list = []
        content_list = {}
        event_permission = EventAdmin.objects.filter(admin_id=admin_id)
        for event in event_permission:
            event_list.append({'id': event.id,'event_id': event.event_id,'admin_id':event.admin_id})
        content_permission = ContentPermission.objects.filter(admin_id=admin_id, event_id=event_id)
        for content in content_permission:
            if content.content == 'event':
                content_list["event_permission"] = content.permission_dict()
            if content.content == 'attendee':
                content_list["attendee_permission"] = content.permission_dict()
            if content.content == 'deleted_attendee':
                content_list["deleted_attendee_permission"] = content.permission_dict()
            if content.content == 'session':
                content_list["session_permission"] = content.permission_dict()
            if content.content == 'question':
                content_list["question_permission"] = content.permission_dict()
            if content.content == 'travel':
                content_list["travel_permission"] = content.permission_dict()
            if content.content == 'location':
                content_list["location_permission"] = content.permission_dict()
            if content.content == 'hotel':
                content_list["hotel_permission"] = content.permission_dict()
            if content.content == 'page':
                content_list["page_permission"] = content.permission_dict()
            if content.content == 'menu':
                content_list["menu_permission"] = content.permission_dict()
            if content.content == 'template':
                content_list["template_permission"] = content.permission_dict()
            if content.content == 'css':
                content_list["css_permission"] = content.permission_dict()
            if content.content == 'file_browser':
                content_list["file_browser_permission"] = content.permission_dict()
            if content.content == 'checkpoints':
                content_list["checkpoints_permission"] = content.permission_dict()
            if content.content == 'language':
                content_list["language_permission"] = content.permission_dict()
            if content.content == 'economy':
                content_list["economy_permission"] = content.permission_dict()
            if content.content == 'filter':
                content_list["filter_permission"] = content.permission_dict()
            if content.content == 'export_filter':
                content_list["export_filter_permission"] = content.permission_dict()
            if content.content == 'photo_reel':
                content_list["photo_reel_permission"] = content.permission_dict()
            if content.content == 'message':
                content_list["message_permission"] = content.permission_dict()
            if content.content == 'setting':
                content_list["setting_permission"] = content.permission_dict()
            if content.content == 'assign_session':
                content_list["assign_session_permission"] = content.permission_dict()
            if content.content == 'assign_travel':
                content_list["assign_travel_permission"] = content.permission_dict()
            if content.content == 'assign_hotel':
                content_list["assign_hotel_permission"] = content.permission_dict()
            if content.content == 'group_registration':
                content_list["group_registration_permission"] = content.permission_dict()

        group_permission = GroupPermission.objects.filter(admin_id=admin_id)
        for group in group_permission:
            group_list.append(group.as_dict())
        admin_permission = {
            "event_permission": event_list,
            "content_permission": content_list,
            "group_permission": group_list
        }
        return admin_permission


class LogoutView(generic.DetailView):
    def get(self, request):
        # request.session.flush()
        del request.session['event_auth_user']
        del request.session['is_login']

        return redirect('login')

