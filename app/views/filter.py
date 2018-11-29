import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.http import Http404
from django.db.models import Q, Max, F

from app.views.gbhelper.filter_helper import FilterHelper
from .common_views import EventView, CommonContext
from app.models import Attendee, Group, RuleSet, UsedRule
from app.views.gbhelper.error_report_helper import ErrorR
import time


class FilterView(generic.DetailView):
    def get(self, request):
        return render(request, '')

    @staticmethod
    def recur_filter(request, filters, match_condition,matched_attendees=[]):
        event_id = request.session['event_auth_user']['event_id']
        return FilterHelper.get_attendee_using_filter(event_id, filters, match_condition, matched_attendees=[])


    def get_filtered_attendees(request, rule_id):
        start_time = time.time()
        attendees=[]
        try:
            rule = RuleSet.objects.get(id=rule_id)
            if rule:
                filters = json.loads(rule.preset)
                q = Q()
                if filters:
                    match_condition = '0'
                    if 'matchFor' in filters[0][0]:
                        match_condition = filters[0][0]['matchFor']
                    elif rule.matchfor:
                        match_condition = rule.matchfor

                    if match_condition == '2':
                        q &= Q(id__in=FilterView.recur_filter(request, filters, match_condition))
                    elif match_condition == '1':
                        q = Q(id=-11)
                        q |= Q(id__in=FilterView.recur_filter(request, filters, match_condition))
                    else:
                        q = Q(id=-11)
                    attendees = Attendee.objects.filter(q)
                    # ErrorR.okblue(attendees.query)
                    if rule.is_limit:
                        limit = 0
                        if rule.limit_amount>0:
                            limit=rule.limit_amount
                        import itertools
                        top5 = itertools.islice(attendees, limit)
                        return list(top5)
        except Exception as e:
            ErrorR.efail(e)
        ErrorR.warn(time.time() - start_time)
        return attendees


    def get_filtered_attendees_count(request, rule_id):
        return len(FilterView.get_filtered_attendees(request, rule_id))

    def post(self, request):
        response_data = {}
        filters = json.loads(request.POST.get('filters'))
        rule = request.POST.get('rule_id')
        if rule != '':
            if not (UsedRule.objects.filter(rule_id=rule, user_id=request.session['event_auth_user']['id']).exists()):
                used_rule = UsedRule(rule_id=rule, user_id=request.session['event_auth_user']['id'])
                used_rule.save()
                total_used = UsedRule.objects.filter(user_id=request.session['event_auth_user']['id'])
                if total_used.count() > 3:
                    total_used[0].delete()

        results = FilterView.get_filtered_attendees(request,rule)
        #cubjub need to add limit

        attendee_list = []
        for result in results:
            attendee_list.append(result.as_dict())
        response_data['success'] = 'Filtered'
        response_data['attendees'] = attendee_list
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_filter(request):
        response_data = {}
        if EventView.check_permissions(request, 'filter_permission'):
            filters = request.POST.get('filters')
            preset_name = request.POST.get('preset_name')

            is_limit = False
            if request.POST.get('is_limit')=="1":
                is_limit = True
            limit_amount = request.POST.get('limit_amount')
            main_matchfor = request.POST.get('matchfor')
            form_data = {
                'name': preset_name,
                'preset': filters,
                'is_limit': is_limit,
                'limit_amount': limit_amount,
                'created_by_id': request.session['event_auth_user']['id']
            }
            if main_matchfor:
                form_data['matchfor'] = main_matchfor
            if 'id' in request.POST:
                group_id = request.POST.get('group_id')
                form_data['group_id' ]= group_id
                rule_id = request.POST.get('id')
                old_filter = RuleSet.objects.get(id=rule_id)
                if old_filter.name == 'quick-filter':
                    form_data['name'] = 'quick-filter'
                if not (RuleSet.objects.filter(name=preset_name,group__event_id=request.session['event_auth_user']['event_id']).exclude(id=rule_id).exists()):
                    RuleSet.objects.filter(id=rule_id).update(**form_data)
                    filter = RuleSet.objects.get(id=rule_id)
                    response_data['filter'] = filter.as_dict()
                    response_data['success'] = 'Attendee Filter Successfully Updated'
                else:
                    response_data['error'] = 'Filter Name Already Exist'
            else:
                event_id=request.session['event_auth_user']['event_id']
                if preset_name == 'quick-filter':
                   type = request.POST.get('type')
                   quick_filter_group = Group.objects.filter(name='temporary-filter',event_id=event_id)

                   if not type:
                       old_filter= RuleSet.objects.filter(name=preset_name,created_by_id=request.session['event_auth_user']['id'],group__event_id=event_id)

                       if old_filter.exists():
                           RuleSet.objects.filter(id=old_filter[0].id).update(**form_data)
                           response_data['success'] = 'Quick Filter Successfully updated'
                           response_data['quick_filter'] = old_filter[0].as_dict()
                       else :
                           if quick_filter_group.exists():
                               form_data['group_id']=quick_filter_group[0].id
                               filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                               form_data["rule_order"] = filter_order
                               quick_filter = RuleSet(**form_data)
                               quick_filter.save()
                               response_data['success'] = 'Quick Filter Successfully saved'
                               response_data['quick_filter'] = quick_filter.as_dict()
                           else:
                               response_data['error'] = 'Quick Filter group not availables'
                   else:
                       if type=="menu":
                          menu_filter = RuleSet.objects.filter(name__contains='menu-filter', group__event_id=event_id).order_by('-id')[:1]
                          if menu_filter.exists():
                             filer_count =  menu_filter[0].name.split("-")[2]
                             new_filter_num = int(filer_count)+1
                             new_filter_name = "menu-filter-"+str(new_filter_num)
                             form_data['name']=new_filter_name
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                          else:
                             form_data['name']="menu-filter-1"
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                       if type=="export":
                          menu_filter = RuleSet.objects.filter(name__contains='export-filter', group__event_id=event_id).order_by('-id')[:1]
                          if menu_filter.exists():
                             filer_count =  menu_filter[0].name.split("-")[2]
                             new_filter_num = int(filer_count)+1
                             new_filter_name = "export-filter-"+str(new_filter_num)
                             form_data['name']=new_filter_name
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                          else:
                             form_data['name']="export-filter-1"
                             form_data['group_id']=quick_filter_group[0].id
                             filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                             form_data["rule_order"] = filter_order
                             quick_filter = RuleSet(**form_data)
                             quick_filter.save()
                             response_data['success'] = 'Quick Filter Successfully saved'
                             response_data['quick_filter'] = quick_filter.as_dict()

                       if type=="page":
                         page_filter = RuleSet.objects.filter(name__contains='page-filter', group__event_id=event_id).order_by('-id')[:1]
                         if page_filter.exists():
                            filer_count =  page_filter[0].name.split("-")[2]
                            new_filter_num = int(filer_count)+1
                            new_filter_name = "page-filter-"+str(new_filter_num)
                            form_data['name']=new_filter_name
                            form_data['group_id']=quick_filter_group[0].id
                            filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                            form_data["rule_order"] = filter_order
                            quick_filter = RuleSet(**form_data)
                            quick_filter.save()
                            response_data['success'] = 'Quick Filter Successfully saved'
                            response_data['quick_filter'] = quick_filter.as_dict()

                         else:
                            form_data['name']="page-filter-1"
                            form_data['group_id']=quick_filter_group[0].id
                            filter_order = FilterView.get_filters_order(quick_filter_group[0].id)
                            form_data["rule_order"] = filter_order
                            quick_filter = RuleSet(**form_data)
                            quick_filter.save()
                            response_data['success'] = 'Quick Filter Successfully saved'
                            response_data['quick_filter'] = quick_filter.as_dict()





                else:
                    group_id = request.POST.get('group_id')
                    form_data['group_id' ]= group_id
                    filter_order = FilterView.get_filters_order(group_id)
                    form_data["rule_order"] = filter_order
                    if not (RuleSet.objects.filter(name=preset_name, group__event_id=event_id).exists()):
                        rule_set = RuleSet(**form_data)
                        rule_set.save()
                        response_data['filter'] = rule_set.as_dict()
                        response_data['success'] = 'Attendee Filter Successfully Saved'
                    else:
                        response_data['error'] = 'Filter Name Already Exist'



        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_filter(request):
        user_id = request.session['event_auth_user']['id']
        user_rules = RuleSet.objects.filter(created_by_id=user_id)
        context = {
            'user_rules': user_rules
        }
        return render(request, 'attendee/filter_set.html', context)

    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'filter_permission'):
            id = request.POST.get('id')
            filter = RuleSet.objects.get(id=id)
            if filter.name == 'quick-filter':
                response_data['warning'] = "You can't delete the Quick Filter"
            else:
                rule = RuleSet.objects.get(id=id)
                rule.delete()
                response_data['success'] = 'Filter Preset Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def filters(request):
        if EventView.check_read_permissions(request, 'filter_permission'):
            context = {}
            filter_context= CommonContext.get_filter_context(request)
            context.update(filter_context)
            return render(request, 'filter/filter.html', context)

    def search(request):
        search_key = request.POST.get('search_key')
        all_filters_groups = []
        if search_key:
            filters_group = Group.objects.filter(
                Q(type="filter", is_show=1, event_id=request.session['event_auth_user']['event_id']) & (Q(ruleset__name__icontains=search_key))).order_by(
                'group_order').distinct()
        else:
            filters_group = Group.objects.filter(Q(type="filter", is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by('group_order').distinct()
        for group in filters_group:
            group.filters = RuleSet.objects.filter(Q(group_id=group.id) & Q(name__icontains=search_key)).order_by('rule_order')
            group_dict = dict(
                id=group.id,
                name=group.name,
                filters=group.filters
            )
            all_filters_groups.append(group_dict)
        data = {
            'filterGroup': all_filters_groups
        }
        return render(request, 'filter/filter_result.html', data)

    def filter_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        if EventView.check_permissions(request, 'filter_permission'):
            filter_id = request.POST.get('filter_id')
            filter = RuleSet.objects.get(id=filter_id)

            duplicate_existance = RuleSet.objects.filter(name=filter.name + '[Copy]', group__event_id=event_id)
            if duplicate_existance.exists():
                response_data['error'] = 'This export is already make a duplicate.'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            filter.pk = None
            # if '[Copy]' not in session.name:
            filter.name += '[Copy]'
            filter.created_by_id=request.session['event_auth_user']['id']
            filter.save()
            response_data['success'] = "Create duplicate filter Successfully"
            response_data['filter'] = filter.as_dict()
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type='application/json')

    def set_filters_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'filter_permission'):
            filters_order = json.loads(request.POST.get('filters_order'))
            for filter in filters_order:
                RuleSet.objects.filter(id=filter['filter_id']).update(rule_order=filter['order'])
            response_data['success'] = 'Filters Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def quick_filter_exists(request):
        event_id=request.session['event_auth_user']['event_id']
        admin_id=request.session['event_auth_user']['id']
        response_data ={}
        quick_filter = RuleSet.objects.filter(name='quick-filter',created_by_id=admin_id,group__event_id=event_id)
        if quick_filter.exists():
            response_data['status']= True
            response_data['filter']=quick_filter[0].as_dict()
        else:
            response_data['status']= False

        return HttpResponse(json.dumps(response_data),content_type="application/json")



    def get_filters_order(group_id):
        filter = RuleSet.objects.values('rule_order').filter(group_id = group_id).aggregate(Max('rule_order'))
        if filter['rule_order__max']:
             rule_order = filter['rule_order__max'] + 1
        else:
            rule_order = 1
        return rule_order


class FilterDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return RuleSet.objects.get(pk=pk)
        except RuleSet.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        rule = self.get_object(pk)
        response = {
            'success': True,
            'rule': rule.as_dict()
        }
        return HttpResponse(json.dumps(response), content_type='application/json')
