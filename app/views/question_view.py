from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from app.models import Questions, Group, Option, QuestionPreRequisite, Travel, CurrentFilter
from app.views.gbhelper.common_helper import CommonHelper
from .common_views import GroupView, EventView
import json
from django.http import Http404
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q, Max
from app.views.gbhelper.language_helper import LanguageH



class QuestionView(generic.DetailView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'question_permission'):
            questionGroup = GroupView.get_questionGroup(request)
            for group in questionGroup:
                group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
            context = {
                'questionGroup': questionGroup,
                'questionGroup': questionGroup,
            }
            context.update(LanguageH.get_current_and_all_presets(request))
            return render(request, 'question/question.html', context)

    def post(self, request):
        response_data = {}
        if EventView.check_permissions(request, 'question_permission'):
            required = False
            if(request.POST.get('required') == "1"):
                required = True

            show_desc=request.POST.get("show_description")
            show_description = False
            if show_desc=="true":
                show_description = True

            form_data = {
                "type": request.POST.get('type'),
                "group_id": request.POST.get('group'),
                "required": required,
                "show_description":show_description
            }

            from_date=request.POST.get('from_date')
            if from_date != '':
                form_data['from_date'] = from_date
            to_date = request.POST.get('to_date')
            if to_date != '':
                form_data['to_date'] = to_date
            from_time = request.POST.get('from_time')
            if from_time != '':
                form_data['from_time'] = from_time
            to_time = request.POST.get('to_time')
            if to_time != '':
                form_data['to_time'] = to_time
            time_interval = request.POST.get('time_interval')
            if time_interval != '':
                form_data['time_interval'] = time_interval
            if "description" in request.POST:
                form_data["description"] = request.POST.get('description')
            if "min_character" in request.POST:
                form_data["min_character"] = request.POST.get('min_character')
            if "max_character" in request.POST:
                form_data["max_character"] = request.POST.get('max_character')
            default_country = request.POST.get('default_country')
            if default_country != '':
                form_data['default_answer'] = default_country
            options_list = json.loads(request.POST.get('options_list'))
            event_id = request.session['event_auth_user']['event_id']
            current_language_id = LanguageH.get_current_language_id(event_id)
            default_language_id = current_language_id
            title_lang = request.POST.get('title_lang')
            description_lang = request.POST.get('description_lang')
            if 'id' in request.POST:
                question_id = request.POST.get('id')
                current_language_id = request.POST.get('current_language_id')
                question_data = Questions.objects.get(id=question_id)
                if current_language_id == default_language_id:
                    form_data["title"] = request.POST.get('title')
                form_data = LanguageH.update_lang(current_language_id,form_data,"title_lang",title_lang,question_data.title_lang)
                form_data = LanguageH.update_lang(current_language_id,form_data,"description_lang",description_lang,question_data.description_lang)
                Questions.objects.filter(id=question_id).update(**form_data)
                for opt in options_list:
                    opt_form = {
                        "default_value": opt['default_value']
                    }
                    if 'id' in opt:
                        if current_language_id == default_language_id:
                            opt_form["option"] = opt['option']
                        option_data = Option.objects.get(id=opt['id'])
                        opt_form = LanguageH.update_lang(current_language_id,opt_form,"option_lang",opt['option_lang'],option_data.option_lang)
                        update_option =Option.objects.filter(id=opt['id']).update(**opt_form)
                    else:
                        opt_form["option"] = opt['option']
                        option_order = QuestionView.get_options_order(question_id)
                        opt_form['option_order'] = option_order
                        opt_form['question_id'] = question_id
                        opt_form = LanguageH.insert_lang(current_language_id,opt_form,"option_lang",opt['option_lang'])
                        add_option = Option(**opt_form)
                        add_option.save()
                question = Questions.objects.get(id=question_id)
                response_data['success'] = 'Question Update Successfully'
                response_data['question'] = question.as_dict()
            else:
                form_data["title"] = request.POST.get('title')
                question_order = QuestionView.get_questions_order(request.POST.get('group'))
                form_data["question_order"] = question_order
                form_data = LanguageH.insert_lang(current_language_id,form_data,"title_lang",title_lang)
                form_data = LanguageH.insert_lang(current_language_id,form_data,"description_lang",description_lang)
                question = Questions(**form_data)
                question.save()
                for opt in options_list:
                    opt_form = {
                        "option": opt['option'],
                        "default_value": opt['default_value']
                    }
                    option_order = QuestionView.get_options_order(question.id)
                    opt_form['option_order'] = option_order
                    opt_form['question_id'] = question.id
                    opt_form = LanguageH.insert_lang(current_language_id,opt_form,"option_lang",opt['option_lang'])
                    add_option = Option(**opt_form)
                    add_option.save()

                response_data['success'] = 'Question Create Successfully'
                response_data['question'] = question.as_dict()
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    def delete(request):
        response_data = {}
        if EventView.check_permissions(request, 'question_permission'):
            id = request.POST.get('id')
            question = Questions.objects.get(id=id)
            if question.actual_definition == 'firstname' or question.actual_definition == 'lastname' or question.actual_definition == 'email' \
                    or question.actual_definition == 'phone':
                response_data['error'] = 'Can not delete this question'
            else:
                event_id = request.session['event_auth_user']['event_id']
                questions = Questions.objects.filter(group__event_id=event_id).order_by('group__group_order','question_order')
                question_index = 0
                for index, item in enumerate(questions):
                    if item.id == question.id:
                        question_index = index+7
                if question_index > 0:
                    current_columns = CurrentFilter.objects.filter(event_id=event_id, table_type='attendee')
                    remove_column = 0
                    for current_column in current_columns:
                        columns = current_column.visible_columns.split('[')[1].split(']')[0]
                        visible_columns = list(map(int, columns.split(',')))
                        remove_key = 0
                        for key, column in enumerate(visible_columns):
                            if column == question_index:
                                remove_column = column
                                remove_key = key
                            elif remove_column>0 and column > remove_column:
                                visible_columns[key] = column-1
                        if remove_key > 0:
                            visible_columns.pop(remove_key)
                        CurrentFilter.objects.filter(id=current_column.id).update(visible_columns=json.dumps(visible_columns))
                question.delete()
                response_data['success'] = 'Question Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def question_duplicate(request):
        response_data = {}
        event_id = request.session['event_auth_user']['event_id']
        if EventView.check_permissions(request, 'question_permission'):
            question_id = request.POST.get('question_id')
            question = Questions.objects.get(id=question_id)

            duplicate_existance = Questions.objects.filter(title=question.title+'[Copy]',group__event_id=event_id)
            if duplicate_existance.exists():
                response_data['error'] = 'This question is already make a duplicate.'
                return HttpResponse(json.dumps(response_data), content_type='application/json')

            question.pk = None
            question.title += '[Copy]'
            question.actual_definition= None
            question.save()

            options = Option.objects.filter(question_id=question_id)
            new_options = []
            for option in options:
                option.pk = None
                option.question_id = question.id
                new_options.append(option)
            if len(new_options)>0:
                Option.objects.bulk_create(new_options)

            response_data['success'] = "Create duplicate question Successfully"
            response_data['question'] = question.as_dict()
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type='application/json')


    def delete_option(request):
        response_data = {}
        if EventView.check_permissions(request, 'question_permission'):
            id = request.POST.get('id')
            option = Option.objects.get(id=id)
            option.delete()
            response_data['success'] = 'Option Deleted Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_Questions(request, questions):
        q_list = []
        for question in questions:
            options = Option.objects.filter(question_id=question.id)
            option_list = []
            for opt in options:
                option_list.append(opt.as_dict())
            q_obj = {
                'question': question.as_dict(),
                'options': option_list
            }
            if request.session['event_auth_user']['type'] == 'super_admin':
                q_obj['access'] =  'write'
            else:
                admin_question_group_access = request.session['admin_permission']['group_permission']
                for access in admin_question_group_access:
                    if access['group']['id'] == question.group.id:
                       q_obj['access'] =  access['access_level']
            q_list.append(q_obj)
        return q_list
    def getAllQuestions(request):
        question_groups = []
        questionGroup = GroupView.get_questionGroup(request)
        for group in questionGroup:
            group.questions = Questions.objects.all().filter(group_id=group.id).order_by('question_order')
            question_list = []
            data = QuestionView.get_Questions(request, group.questions)
            question_list.append(data)
            q_obj = {
                'group': group.as_dict(),
                'questions': question_list
            }
            question_groups.append(q_obj)
        all_attendee_groups = GroupView.get_attendeeGroup(request)
        attendee_groups = []
        for group in all_attendee_groups:
            attendee_groups.append(group.as_dict())

        travels = Travel.objects.filter(travel_bound='outbound', group__event_id=request.session['event_auth_user']['event_id'])
        outbound_flights = []
        for travel in travels:
            outbound_flights.append(travel.as_dict())

        homebound_travels = Travel.objects.filter(travel_bound='homebound', group__event_id=request.session['event_auth_user']['event_id'])
        homebound_flights = []
        for home_travel in homebound_travels:
            homebound_flights.append(home_travel.as_dict())

        data = {'questionGroup' : question_groups, 'attendee_groups': attendee_groups, 'outbound_flights': outbound_flights, 'homebound_flights': homebound_flights,
                'datepicker_date_format':CommonHelper.get_datepicker_date_format(request),
                'moment_date_format':CommonHelper.get_moment_date_format(request),
                'timezone':CommonHelper.get_timezone(request)
                }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def search(request):
        search_key = request.POST.get('search_key')
        all_questions_groups = []
        if search_key:
            questions_group = Group.objects.filter(Q(type="question", is_show=1, event_id=request.session['event_auth_user']['event_id']) & (Q(questions__title__icontains=search_key))).order_by('group_order').distinct()
        else:
            questions_group = Group.objects.filter(Q(type="question",is_show=1, event_id=request.session['event_auth_user']['event_id'])).order_by('group_order').distinct()
        for group in questions_group:
            group.question = Questions.objects.filter(Q(group_id=group.id)& Q(title__icontains=search_key)).order_by('question_order')
            group_dict = dict(
                id=group.id,
                name=group.name,
                question=group.question
            )
            all_questions_groups.append(group_dict)

        data = {
                'questionGroup': all_questions_groups
            }
        return render(request, 'question/question_result.html', data)

    def set_questions_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'question_permission'):
            questions_order = json.loads(request.POST.get('questions_order'))
            for question in questions_order:
                Questions.objects.filter(id=question['question_id']).update(question_order=question['order'])
            response_data['success'] = 'Questions Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_questions_order(group_id):
        question = Questions.objects.values('question_order').filter(group_id = group_id).aggregate(Max('question_order'))
        if question['question_order__max']:
             question_order = question['question_order__max'] + 1
        else:
            question_order = 1
        return question_order

    def get_questions_option(request):
        question_id = request.POST.get('question_id')
        question = Questions.objects.get(id=question_id)
        options = Option.objects.filter(question_id=question_id).order_by('option_order')
        pre_req_questions = QuestionPreRequisite.objects.filter(question_id=question_id)
        pre_req_list = []
        for pre_req in pre_req_questions:
            pre_req_list.append(pre_req.as_dict())
        option_value = []
        for option in options:
            option_value.append(option.as_dict())
        response_data = {
            'options':option_value,
            'question': question.as_dict(),
            'pre_req_questions': pre_req_list
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_questions_all_option(request):
        question_ids = json.loads(request.POST.get('question_ids'))
        all_question_list = []
        for id in question_ids:
            question_id = id
            question = Questions.objects.get(id=question_id)
            options = Option.objects.filter(question_id=question_id).order_by('option_order')
            pre_req_questions = QuestionPreRequisite.objects.filter(question_id=question_id)
            pre_req_list = []
            for pre_req in pre_req_questions:
                pre_req_list.append(pre_req.as_dict())
            option_value = []
            for option in options:
                option_value.append(option.as_dict())

            all_question_list.append({
                'options':option_value,
                'question': question.as_dict(),
                'pre_req_questions': pre_req_list
            })
        response_data = {
            'all_question_list':all_question_list
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def option_order(request):
        response_data = {}
        if EventView.check_permissions(request, 'question_permission'):
            option_order = json.loads(request.POST.get('option_order'))
            for option in option_order:
                Option.objects.filter(id=option['option_id']).update(option_order=option['order'])
            response_data['success'] = 'Options Ordered Successfully'
        else:
            response_data['error'] = 'You do not have Permission to do this'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_options_order(question_id):
        option = Option.objects.values('option_order').filter(question_id = question_id).aggregate(Max('option_order'))
        if option['option_order__max']:
             option_order = option['option_order__max'] + 1
        else:
            option_order = 1
        return option_order



class QuestionListView(BaseDatatableView):
    model = Questions
    columns = ['id', 'title', 'type', 'required', 'id']
    order_columns = ['id', 'title', 'type', 'required','id']

class QuestionDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
          return Questions.objects.get(id=pk)
        except Questions.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        event_id = request.session['event_auth_user']['event_id']
        question = self.get_object(pk)
        options = Option.objects.filter(question_id=pk).order_by('option_order')
        option_list = []
        for option in options:
            option_list.append(option.as_dict())

        pre_req_list = []
        pre_req_questions = QuestionPreRequisite.objects.filter(question_id=question.id)
        for ques in pre_req_questions:
            pre_req_list.append(ques.as_dict())
        current_language_id = LanguageH.get_current_language_id(event_id)

        data = {
            'question' : question.as_dict(),
            'option_list': option_list,
            'pre_req_list': pre_req_list,
            'current_language_id': current_language_id
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
