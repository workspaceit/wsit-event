import json
from django.views import generic
from app.models import SeminarsUsers, SessionTags, SeminarSpeakers, RequestedBuddy, Elements, MatchLine, Option
from django.template.loader import render_to_string
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey
from app.views.gbhelper.common_helper import CommonHelper
from app.models import OrderItems
from django.db.models import F, Sum

class DetailsData(generic.DetailView):

    def get_sessions_data_by_attendee(request, sessions, session_rules, attendee_id):
        element = Elements.objects.filter(slug="sessions")
        for session in sessions:
            session.speakers = SeminarSpeakers.objects.filter(session=session.id)
            session.tags = SessionTags.objects.filter(session=session.id)
            session.status = ""
            rebates = OrderItems.objects.filter(order__attendee_id=attendee_id, item_type='rebate', rebate_for_item_type='session', rebate_for_item_id=session.id).aggregate(total=Sum('rebate_amount'))
            if rebates['total'] is not None:
                session.rebate_amount = (-1)*rebates['total']
            else:
                session.rebate_amount = 0

            status = SeminarsUsers.objects.filter(session_id=session.id, attendee_id=attendee_id)
            if status.exists():
                session.status = status[0].status
            session = LanguageKey.get_session_data_by_language(request,session)
        language_for_session =  LanguageKey.get_lang_key(request, element[0].id)
        language_for_economy =  LanguageKey.catch_lang_key_obj(request, 'economy')
        language_for_session['langkey'].update(language_for_economy['langkey'])
        context = {
            'sessions': sessions,
            'session_rules': session_rules,
            "language": language_for_session

        }
        return render_to_string('public/element/email_sessions.html', context)

    def get_travel_data_by_attendee(request, travels, travel_rules):
        element = Elements.objects.filter(slug="travels")
        for travel in travels:
            travel = LanguageKey.get_travel_data_by_language(request,travel)
        context = {
            'travels': travels,
            'travel_rules': travel_rules,
            "language": LanguageKey.get_lang_key(request, element[0].id)
        }
        return render_to_string('public/element/email_travels.html', context)

    def get_hotels_data_by_attendee(request, hotels, hotel_rules, attendee_id):
        element = Elements.objects.filter(slug="hotels")
        for hotel in hotels:
            hotel.buddy = RequestedBuddy.objects.filter(booking_id=hotel.id)
            actual_buddy = MatchLine.objects.filter(booking_id=hotel.id)
            if actual_buddy.exists():
                hotel.actualbuddy = MatchLine.objects.filter(match_id=actual_buddy[0].match_id).exclude(
                    id=actual_buddy[0].id)
            hotel.room = LanguageKey.get_room_data_by_language(request,hotel.room)
            rebates = OrderItems.objects.filter(order__attendee_id=attendee_id, item_type='rebate',
                                                rebate_for_item_type='hotel', rebate_for_item_id=hotel.room.id).aggregate(total=Sum('rebate_amount'))
            if rebates['total'] is not None:
                hotel.room.rebate_amount = (-1) * rebates['total']
            else:
                hotel.room.rebate_amount = 0
        language_for_hotel = LanguageKey.get_lang_key(request, element[0].id)
        language_for_economy = LanguageKey.catch_lang_key_obj(request, 'economy')
        language_for_hotel['langkey'].update(language_for_economy['langkey'])
        context = {
            'hotels': hotels,
            'hotel_rules': hotel_rules,
            "language": language_for_hotel
        }
        return render_to_string('public/element/email_hotels.html', context)

    def get_question_data_by_attendee(request, questionAnswer, question_rules, attendee, modal=False):
        for answer in questionAnswer['answers']:
            answer.question = LanguageKey.get_question_data_by_language(request,answer.question)
            try:
                if answer.question.type == 'checkbox':
                    checkbox_answers = answer.value.split('<br>')
                    checkbox_answer_list= []
                    for checkbox_answer in checkbox_answers:
                        answer_lang = Option.objects.filter(option=checkbox_answer.strip(), question_id=answer.question_id).first()
                        answer_data = LanguageKey.get_option_data_by_language(request,answer_lang)
                        checkbox_answer_list.append(answer_data.option)
                    answer.value = '<br>'.join(checkbox_answer_list)
                elif answer.question.type == 'select' or answer.question.type == 'radio_button':
                    answer_lang = Option.objects.filter(option=answer.value, question_id=answer.question_id).first()
                    answer_data = LanguageKey.get_option_data_by_language(request,answer_lang)
                    answer.value = answer_data.option
                elif answer.question.type == 'date':
                    date_str = answer.value
                    answer.value = CommonHelper.converStringToDate(date_str)
                elif answer.question.type == 'time':
                    time_str = answer.value
                    answer.value = CommonHelper.converStringToTime(time_str)
                elif answer.question.type == 'date_range':
                    value = json.loads(answer.value)
                    value[0] = CommonHelper.converStringToDate(value[0])
                    value[1] = CommonHelper.converStringToDate(value[1])
                    answer.value1 = value[0]
                    answer.value2 = value[1]
                elif answer.question.type == 'time_range':
                    value = json.loads(answer.value)
                    value[0] = CommonHelper.converStringToTime(value[0])
                    value[1] = CommonHelper.converStringToTime(value[1])
                    answer.value1 = value[0]
                    answer.value2 = value[1]
                elif answer.question.type == 'country':
                    country_list = CommonHelper.get_country_list(request)
                    answer.value = country_list[answer.value]
            except Exception as e:
                ErrorR.efail(e)
                pass

        element = Elements.objects.filter(slug="questions")
        context = {
            'questionAnswer': questionAnswer,
            'question_rules': question_rules,
            "language": LanguageKey.get_lang_key(request, element[0].id)
        }
        if modal:
            context['firstname'] = attendee.firstname
            context['lastname'] = attendee.lastname
            return render_to_string('public/element/attendee_modal.html', context)
        return render_to_string('public/element/email_question.html', context)

    def get_answer_data_by_attendee(request, answer):
        try:
            if answer.question.type == 'checkbox':
                checkbox_answers = answer.value.split('<br>')
                checkbox_answer_list = []
                for checkbox_answer in checkbox_answers:
                    answer_lang = Option.objects.filter(option=checkbox_answer.strip(),
                                                        question_id=answer.question_id).first()
                    answer_data = LanguageKey.get_option_data_by_language(request, answer_lang)
                    checkbox_answer_list.append(answer_data.option)
                answer.value = '<br>'.join(checkbox_answer_list)
            elif answer.question.type == 'select' or answer.question.type == 'radio_button':
                answer_lang = Option.objects.filter(option=answer.value, question_id=answer.question_id).first()
                answer_data = LanguageKey.get_option_data_by_language(request, answer_lang)
                answer.value = answer_data.option
            elif answer.question.type == 'date_range' or answer.question.type == 'time_range':
                value = json.loads(answer.value)
                answer.value = ' - '.join(value)
            elif answer.question.type == 'country':
                country_list = CommonHelper.get_country_list(request)
                answer.value = country_list[answer.value]
        except Exception as e:
            ErrorR.efail(e)
            pass
        return answer