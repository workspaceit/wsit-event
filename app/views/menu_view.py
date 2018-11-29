from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Users, MenuItem, PageContent, MenuPermission, Events, RuleSet
from datetime import timedelta
from django.http import Http404
from django.views.generic import TemplateView
from django.db import transaction
from .common_views import GroupView,CommonContext, EventView
import json
from django.db.models import Q
from app.views.gbhelper.language_helper import LanguageH


class MenuView(TemplateView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'menu_permission'):
            MenuItems = MenuItem.objects.filter(event_id=request.session['event_auth_user']['event_id']).order_by('level','rank').distinct()
            groups = GroupView.get_menuGroup(request)
            filterGroup = GroupView.get_filterGroup(request)
            for group in filterGroup:
                group.rules = RuleSet.objects.filter(group_id=group.id).order_by('rule_order').exclude(name='quick-filter')
            mainMenu = MenuItem.objects.filter(( Q(menupermission__rule__group__event_id=request.session['event_auth_user']['event_id']) | Q(event_id=request.session['event_auth_user']['event_id'])),level=1).order_by('rank').distinct()
            all_menu = MenuView.get_menu(request,mainMenu)
            all_pages = PageContent.objects.filter(event_id=request.session['event_auth_user']['event_id'], is_show=1)
            event = Events.objects.get(id=request.session['event_auth_user']['event_id'])
            event_end_date = event.end + timedelta(days=1)

            common_context = CommonContext.get_all_common_context(request)

            context = {
                'MenuItems': MenuItems,
                'groups': groups,
                'all_menu': all_menu,
                'all_pages':all_pages,
                'event_end_date': event_end_date,
            }
            context.update(common_context)
            filter_context= CommonContext.get_filter_context(request)
            context.update(filter_context)
            context.update(LanguageH.get_current_and_all_presets(request))
            return render(request, 'menu/menus.html', context)

    def get_menu(request, mainMenu):
        for menu in mainMenu:
            menu.items = MenuItem.objects.filter(parent_id=menu.id).order_by('rank')
            for item in menu.items:
                item.items = MenuItem.objects.filter(parent_id=item.id).order_by('rank')
                if item.items.count() > 0:
                   # print(item.items.count())
                   MenuView.get_menu(request, item.items)

        return mainMenu

    @transaction.atomic
    def post(self, request):
        response_data = {}
        if EventView.check_permissions(request, 'menu_permission'):
            external_url = request.POST.get('url')
            if external_url != '':
                if '//' not in external_url:
                    external_url = '//'+external_url
            form_data = {
                "url": external_url,
                "start_time": request.POST.get('start_time'),
                "end_time": request.POST.get('end_time'),
                "is_visible": request.POST.get('is_visible'),
                "available_offline": request.POST.get('available_offline'),
                "allow_unregistered": request.POST.get('allow_unregistered'),
                "last_updated_by_id": request.session['event_auth_user']['id']
            }
            accept_login = request.POST.get('accept_login')
            form_data['accept_login'] = False
            if accept_login == 'true':
                form_data['accept_login'] = True
            only_speaker = request.POST.get('only_speaker')
            form_data['only_speaker'] = False
            if only_speaker == 'true':
                form_data['only_speaker'] = True
            groups = json.loads(request.POST.get('group_id'))
            url = request.POST.get('url')
            uid_include = request.POST.get('uid_include')
            is_visible = request.POST.get('is_visible')
            is_available = request.POST.get('available_offline')
            allow_unregistered = request.POST.get('allow_unregistered')
            form_data['uid_include'] = False
            if uid_include == '1':
                form_data['uid_include'] = True
            form_data['is_visible'] = False
            if is_visible == '1':
                form_data['is_visible'] = True

            form_data['available_offline'] = False
            if is_available == 'true':
                form_data['available_offline'] = True

            form_data['allow_unregistered'] = False
            if allow_unregistered == 'true':
                form_data['allow_unregistered'] = True

            parent_id =request.POST.get('parent')
            content_id = request.POST.get('content_id')
            if content_id != '':
                form_data['url'] = request.POST.get('content_url')
            else:
                content_id = None
            if content_id == '':
                content_id = None
            form_data['content_id'] = content_id
            level = 1
            rank = 1
            response_data['parent_changed'] = False
            event = Events.objects.get(id=request.session['event_auth_user']['event_id'])
            form_data['event_id'] = request.session['event_auth_user']['event_id']
            current_language_id = LanguageH.get_current_language_id(request.session['event_auth_user']['event_id'])
            default_language_id = current_language_id
            title_lang = request.POST.get('title_lang')
            # if MenuView.urlpath_exists(url, content_id, event.url):
            if 'id' in request.POST:
                current_language_id = request.POST.get('current_language_id')
                if current_language_id == default_language_id:
                    form_data["title"] = request.POST.get('title')
                menuitem_id = request.POST.get('id')
                menu = MenuItem.objects.get(id=menuitem_id)
                form_data = LanguageH.update_lang(current_language_id, form_data, "title_lang", title_lang, menu.title_lang)
                menuitem_already_exists = MenuItem.objects.filter(url=form_data['url'], event_id=request.session['event_auth_user']['event_id']).exclude(id=menuitem_id)
                if not menuitem_already_exists.exists():
                    if parent_id != str(0) and parent_id != str(menu.parent_id):
                        response_data['parent_changed'] = True
                        menuitem = MenuItem.objects.get(id=parent_id)
                        level = menuitem.level + 1
                        form_data["parent_id"] = parent_id

                        childItems = MenuItem.objects.filter(parent_id=parent_id).last()
                        if childItems :
                            rank = childItems.rank + 1

                        form_data["rank"] = rank
                        form_data["level"] = level

                    MenuItem.objects.filter(id=menuitem_id).update(**form_data)
                    menu_item = MenuItem.objects.get(id=menuitem_id)
                    MenuPermission.objects.filter(menu_id=menu.id).delete()
                    if groups:
                        for group in groups:
                            permission = MenuPermission(menu_id=menu.id, rule_id=group)
                            permission.save()
                    else:
                        permission = MenuPermission(menu_id=menu.id, rule_id= None)
                        permission.save()
                    response_data['success'] = 'Menu Item Updated Successfully'
                    response_data['menu_item'] = menu_item.as_dict()
                    return HttpResponse(json.dumps(response_data), content_type="application/json")
                else:
                    response_data['error'] = 'Menu Item Url already Exists'

            else:
                form_data["title"] = request.POST.get('title')
                form_data = LanguageH.insert_lang(current_language_id, form_data, "title_lang", title_lang)
                menuitem_already_exists = MenuItem.objects.filter(url=form_data['url'], event_id=request.session['event_auth_user']['event_id'])
                if not menuitem_already_exists.exists():
                    if parent_id != str(0):
                        menuitem = MenuItem.objects.get(id=parent_id)
                        level = menuitem.level + 1
                        form_data["parent_id"] = parent_id

                        childItems = MenuItem.objects.filter(parent_id=parent_id).last()
                        if childItems :
                            rank = childItems.rank + 1
                    else:
                         menuitem = MenuItem.objects.filter(level=1).last()
                         if menuitem :
                             rank = menuitem.rank +1


                    form_data["rank"] = rank
                    form_data["level"] = level
                    form_data['created_by_id'] = request.session['event_auth_user']['id']
                    menu= MenuItem(**form_data)
                    menu.save()
                    if groups:
                        for group in groups:
                            permission = MenuPermission(menu_id=menu.id, rule_id=group)
                            permission.save()
                    else:
                        permission = MenuPermission(menu_id=menu.id, rule_id= None)
                        permission.save()

                    response_data['success'] = 'Menu Item created Successfully'

                    response_data['menu_item'] = menu.as_dict()
                else:
                    response_data['error'] = 'Menu Item Url already Exists'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def urlpath_exists(name, content_id, event_url):
        from django.core.urlresolvers import reverse
        if content_id == '' or content_id == None:
            try:
                reverse(name, kwargs={'event_url':event_url})
                return True
            except Exception:
                return False
        else:
            return True


    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'menu_permission'):
            id = request.POST.get('id')
            menu_item = MenuItem.objects.get(id=id)
            childs = MenuItem.objects.filter(parent_id=id)
            siblings = MenuItem.objects.filter(level=menu_item.level, rank__gt=menu_item.rank)
            last_rank = menu_item.rank
            rank = menu_item.rank
            for child in childs:
                parent = MenuItem.objects.filter(level=child.level-1).first()
                MenuItem.objects.filter(id=child.id).update(level=child.level-1, parent_id=parent.parent_id, rank=rank)
                rank = rank + 1
                last_rank = rank
            for menu in siblings:
                MenuItem.objects.filter(id=menu.id, parent_id=menu_item.parent_id).update(rank=last_rank)
                last_rank = last_rank + 1
            menu_item.delete()
            response_data['success'] = 'Menu Item Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")


    def set_menus_order(request):
        response_data = {}
        menu_list = json.loads(request.POST.get('menu_list'))
        level = 1
        rank = 1
        for menu in menu_list:
            MenuItem.objects.filter(id=menu['id']).update(level=level, rank=rank, parent_id=None)
            rank = rank + 1
            if 'children' in menu:
                child_level = 2
                child_rank = 1
                for child_menu in menu['children']:
                    MenuItem.objects.filter(id=child_menu['id']).update(level=child_level, rank=child_rank, parent_id=menu['id'])
                    child_rank = child_rank + 1
                    if 'children' in child_menu:
                        child2_level = 3
                        child2_rank = 1
                        for child2_menu in child_menu['children']:
                            MenuItem.objects.filter(id=child2_menu['id']).update(level=child2_level, rank=child2_rank, parent_id=child_menu['id'])
                            child2_rank = child2_rank + 1
        response_data['success'] = "Menu Sortable Successfully"
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def get_parents(request):
        parent_items = MenuItem.objects.filter(event_id=request.session['event_auth_user']['event_id']).order_by('level','rank').distinct()
        parent_list = []
        for item in parent_items:
            parent_list.append(item.as_dict())
        data = {
            'parent_items': parent_list,
            'success': True
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

class MenuItemDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return MenuItem.objects.get(id=pk)
        except Users.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        menuitem = self.get_object(pk)

        parent_items = MenuItem.objects.filter(event_id=request.session['event_auth_user']['event_id']).exclude(id=pk).order_by('level','rank').distinct()
        parent_list = []
        for item in parent_items:
            parent_list.append(item.as_dict())
        menu_groups = MenuPermission.objects.filter(menu_id=pk)
        groups = []
        for group in menu_groups:
            group_data ={}
            if group.rule:
                group_data['id']=group.rule.id
                group_data['text']=group.rule.name
                groups.append(group_data)
        event_id = request.session['event_auth_user']['event_id']
        current_language_id = LanguageH.get_current_language_id(event_id)
        data = {
            'menuitem': menuitem.as_dict(),
            'parent_items':parent_list,
            'groups': groups,
            'success': True,
            'current_language_id': current_language_id
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
