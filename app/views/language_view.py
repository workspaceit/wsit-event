from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import Elements, Presets, ElementDefaultLang, ElementPresetLang, PresetEvent, MenuItem, Questions, \
    Option, Session, Travel, Locations, Hotel, Room, Group, \
    Attendee, EmailContents, ElementsAnswers
from django.db.models import Q
import json
from django.db import connection
import time
from django.template.loader import render_to_string

from app.views.common_views import EventView
from app.views.gbhelper.error_report_helper import ErrorR
from app.views.gbhelper.language_helper import LanguageH


class LanguageView(TemplateView):
    def get(self, request):
        if EventView.check_read_permissions(request, 'language_permission'):
            event_id = request.session['event_auth_user']['event_id']
            [presets, presetsEvent] = LanguageH.get_preset_list(event_id, request.session['event_auth_user']['type'])
            elements = Elements.objects.all()
            elementDefault = ElementDefaultLang.objects.all()
            header_lang_render = render_to_string('language/header_lang_render.html',
                                                  {
                                                      "presets": presets,
                                                      "presetsEvent": presetsEvent,
                                                      "request": request
                                                  })
            context = {
                "elements": elements,
                "elementDefault": elementDefault,
                "presets": presets,
                "presetsEvent": presetsEvent,
                "header_lang_render": header_lang_render,
                "event_id": event_id
            }
            # lang = LanguageView.all_key(request,27)

            return render(request, 'language/index.html', context)

    def get_general_language(request):
        if EventView.check_read_permissions(request, 'language_permission'):
            event_id = request.session['event_auth_user']['event_id']
            [presets, presetsEvent] = LanguageH.get_preset_list(event_id, request.session['event_auth_user']['type'])
            menus = MenuItem.objects.values('id', 'title').filter(event_id=event_id)
            questions = Questions.objects.values('id', 'title').filter(group__event_id=event_id)
            sessions = Session.objects.values('id', 'name').filter(group__event_id=event_id)
            travels = Travel.objects.values('id', 'name').filter(group__event_id=event_id)
            locations = Locations.objects.values('id', 'name').filter(group__event_id=event_id)
            hotels = Hotel.objects.values('id', 'name').filter(group__event_id=event_id)
            rooms = Room.objects.values('id', 'description').filter(hotel__group__event_id=event_id)
            groups = Group.objects.values('id', 'name').filter(event_id=event_id, is_show=1).exclude(type='email')
            emails = EmailContents.objects.values('id','name').filter(template__event_id=event_id)
            submit_btns = ElementsAnswers.objects.values('id','answer','box_id','page_id').filter(page__event_id=event_id, element_question_id=69)
            submit_button_names = ElementsAnswers.objects.values('id','answer','box_id','page_id').filter(page__event_id=event_id, element_question_id=70)
            pdf_btns = ElementsAnswers.objects.values('id', 'answer', 'box_id', 'page_id').filter(
                page__event_id=event_id, element_question_id=343)
            pdf_button_names = ElementsAnswers.objects.values('id', 'answer', 'box_id', 'page_id').filter(
                page__event_id=event_id, element_question_id=344)
            header_lang_render = render_to_string('language/header_lang_render.html',
                                                  {
                                                      "presets": presets,
                                                      "presetsEvent": presetsEvent,
                                                      "request": request
                                                  })
            submit_buttons = []
            for submit_button in submit_btns:
                button_pdf = {
                    "id": submit_button['id'],
                    "box_id": submit_button['box_id'],
                    "answer":submit_button['answer'],
                    "page_id":submit_button['page_id']
                }
                submit_buttons.append(button_pdf)
            for s_btn in submit_buttons:
                for s_btn_n in submit_button_names:
                    if s_btn_n['box_id'] == s_btn['box_id'] and s_btn_n['page_id'] == s_btn['page_id']:
                        print(s_btn_n['box_id'])
                        print(s_btn_n['answer'])
                        s_btn['button_name'] = s_btn_n['answer']

            pdf_buttons = []
            for pdf_button in pdf_btns:
                button_pdf = {
                    "id": pdf_button['id'],
                    "box_id": pdf_button['box_id'],
                    "answer": pdf_button['answer'],
                    "page_id": pdf_button['page_id']
                }
                pdf_buttons.append(button_pdf)
            for p_btn in pdf_buttons:
                for p_btn_n in pdf_button_names:
                    if p_btn_n['box_id'] == p_btn['box_id'] and p_btn_n['page_id'] == p_btn['page_id']:
                        print(p_btn_n['box_id'])
                        print(p_btn_n['answer'])
                        p_btn['button_name'] = p_btn_n['answer']

            context = {
                "menus": menus,
                "questions": questions,
                "sessions": sessions,
                "travels": travels,
                "locations": locations,
                "hotels": hotels,
                "rooms": rooms,
                "groups": groups,
                "emails": emails,
                "presets": presets,
                "presetsEvent": presetsEvent,
                "header_lang_render": header_lang_render,
                "submit_buttons": submit_buttons,
                "pdf_buttons": pdf_buttons,
                "event_id": event_id
            }
            return render(request, 'language/general_language.html', context)

    def get_date_time_language(request):
        if EventView.check_read_permissions(request, 'language_permission'):
            event_id = request.session['event_auth_user']['event_id']
            [presets, presetsEvent] = LanguageH.get_preset_list(event_id, request.session['event_auth_user']['type'])
            header_lang_render = render_to_string('language/header_lang_render.html',
                                                  {
                                                      "presets": presets,
                                                      "presetsEvent": presetsEvent,
                                                      "request": request
                                                  })
            context = {
                "presets": presets,
                "presetsEvent": presetsEvent,
                "header_lang_render": header_lang_render,
                "event_id": event_id
            }
            return render(request, 'language/date_time_language.html', context)

    def get_preset(request):
        presetId = 0
        if request.GET.get('id') == "":
            presetId = 0
        else:
            presetId = request.GET.get('id')

        elements = Elements.objects.all()
        if presetId != "0":

            for element in elements:
                element.name = element.name.replace(" ", "-")
                element.lang = ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                                preset_id=presetId)
                element.hasNotification = False
                element.hasButton = False
                element.hasText = False
                element.hasValidation = False
                if (ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                     preset_id=presetId,
                                                     element_default_lang__type='notification').exists()):
                    element.hasNotification = True
                if (ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                     preset_id=presetId,
                                                     element_default_lang__type='text').exists()):
                    element.hasText = True
                if (ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                         preset_id=presetId,
                                                         element_default_lang__type='button').exists()):
                    element.hasButton = True
                if (ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                     preset_id=presetId,
                                                     element_default_lang__type='validation_text').exists()):
                    element.hasValidation = True
            context = {
                "elements": elements
            }

            return render(request, 'language/preset_lang_render.html', context)

        else:
            for element in elements:
                element.name = element.name.replace(" ", "-")
                element.lang = ElementDefaultLang.objects.filter(element_id=element.id)
                element.hasNotification = False
                element.hasButton = False
                element.hasText = False
                element.hasValidation = False
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='notification').exists()):
                    element.hasNotification = True
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='text').exists()):
                    element.hasText = True
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='button').exists()):
                    element.hasButton = True
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='validation_text').exists()):
                    element.hasValidation = True

            context = {
                "elements": elements
            }

            return render(request, 'language/default_lang_render.html', context)

    def get_general_preset(request):
        try:
            presetId = 0
            if request.GET.get('id') == "":
                presetId = 0
            else:
                presetId = request.GET.get('id')
            general_langs = []
            event_id = request.session['event_auth_user']['event_id']
            menus = MenuItem.objects.values('id', 'title', 'title_lang').filter(event_id=event_id)
            questions = Questions.objects.values('id', 'title', 'description', 'title_lang', 'description_lang').filter(
                group__event_id=event_id)
            sessions = Session.objects.values('id', 'name', 'name_lang', 'description', 'description_lang').filter(
                group__event_id=event_id)
            travels = Travel.objects.values('id', 'name', 'name_lang', 'description', 'description_lang').filter(
                group__event_id=event_id)
            locations = Locations.objects.values('id', 'name', 'name_lang', 'description', 'description_lang',
                                                 'address', 'address_lang', 'contact_name', 'contact_name_lang').filter(
                group__event_id=event_id)
            hotels = Hotel.objects.values('id', 'name', 'name_lang').filter(group__event_id=event_id)
            rooms = Room.objects.values('id', 'description', 'description_lang').filter(hotel__group__event_id=event_id)
            groups = Group.objects.values('id', 'name', 'name_lang').filter(event_id=event_id).exclude(type='email')
            emails = EmailContents.objects.values('id', 'subject', 'subject_lang').filter(template__event_id=event_id)
            submit_buttons = ElementsAnswers.objects.values('id', 'answer').filter(page__event_id=event_id, element_question_id=69)
            pdf_buttons = ElementsAnswers.objects.values('id', 'answer').filter(page__event_id=event_id, element_question_id=343)
            menu_array = []
            question_array = []
            session_array = []
            travel_array = []
            location_array = []
            hotel_array = []
            room_array = []
            group_array = []
            emails_array = []
            submit_button_array = []
            pdf_button_array = []

            if presetId != "0":
                for menu in menus:
                    if menu['title_lang'] != '' and menu['title_lang'] != None:
                        try:
                            menu_title_lang = json.loads(menu['title_lang'], strict=False)
                            if menu_title_lang[str(presetId)]:
                                menu['title'] = menu_title_lang[str(presetId)]
                        except:
                            pass
                    menu_dict = {
                        'id': menu['id'],
                        'title': menu['title']
                    }
                    menu_array.append(menu_dict)
                general_langs.append({"menus": menu_array})

                for question in questions:
                    if question['title_lang'] != '' and question['title_lang'] != None:
                        try:
                            question_title_lang = json.loads(question['title_lang'], strict=False)
                            if question_title_lang[str(presetId)]:
                                question['title'] = question_title_lang[str(presetId)]
                        except:
                            pass
                    if question['description_lang'] != '' and question['description_lang'] != None:
                        try:
                            question_description_lang = json.loads(question['description_lang'], strict=False)
                            if question_description_lang[str(presetId)]:
                                question['description'] = question_description_lang[str(presetId)]
                        except:
                            pass
                    options = Option.objects.filter(question_id=question['id'])
                    option_array = []
                    for option in options:
                        if option.option_lang != '' and option.option_lang != None:
                            try:
                                option_lang = json.loads(option.option_lang, strict=False)
                                if option_lang[str(presetId)]:
                                    option.option = option_lang[str(presetId)]
                            except:
                                pass
                        option_dict = {
                            'option_id': option.id,
                            'option': option.option
                        }
                        option_array.append(option_dict)
                    question_dict = {
                        'id': question['id'],
                        'title': question['title'],
                        'description': question['description'] if question['description'] else '',
                        'options': option_array
                    }
                    question_array.append(question_dict)
                general_langs.append({"questions": question_array})

                for session in sessions:
                    if session['name_lang'] != '' and session['name_lang'] != None:
                        try:
                            session_name_lang = json.loads(session['name_lang'], strict=False)
                            if session_name_lang[str(presetId)]:
                                session['name'] = session_name_lang[str(presetId)]
                        except:
                            pass
                    if session['description_lang'] != '' and session['description_lang'] != None:
                        try:
                            session_description_lang = json.loads(session['description_lang'], strict=False)
                            if session_description_lang[str(presetId)]:
                                session['description'] = session_description_lang[str(presetId)]
                        except:
                            pass
                    session_dict = {
                        'id': session['id'],
                        'name': session['name'],
                        'description': session['description'] if session['description'] else '',
                    }
                    session_array.append(session_dict)
                general_langs.append({"sessions": session_array})

                for travel in travels:
                    if travel['name_lang'] != '' and travel['name_lang'] != None:
                        try:
                            travel_name_lang = json.loads(travel['name_lang'], strict=False)
                            if travel_name_lang[str(presetId)]:
                                travel['name'] = travel_name_lang[str(presetId)]
                        except:
                            pass
                    if travel['description_lang'] != '' and travel['description_lang'] != None:
                        try:
                            travel_description_lang = json.loads(travel['description_lang'], strict=False)
                            if travel_description_lang[str(presetId)]:
                                travel['description'] = travel_description_lang[str(presetId)]
                        except:
                            pass
                    travel_dict = {
                        'id': travel['id'],
                        'name': travel['name'],
                        'description': travel['description'] if travel['description'] else '',
                    }
                    travel_array.append(travel_dict)
                general_langs.append({"travels": travel_array})

                for location in locations:
                    if location['name_lang'] != '' and location['name_lang'] != None:
                        try:
                            location_name_lang = json.loads(location['name_lang'], strict=False)
                            if location_name_lang[str(presetId)]:
                                location['name'] = location_name_lang[str(presetId)]
                        except:
                            pass
                    if location['description_lang'] != '' and location['description_lang'] != None:
                        try:
                            location_description_lang = json.loads(location['description_lang'], strict=False)
                            if location_description_lang[str(presetId)]:
                                location['description'] = location_description_lang[str(presetId)]
                        except:
                            pass
                    if location['address_lang'] != '' and location['address_lang'] != None:
                        try:
                            location_address_lang = json.loads(location['address_lang'], strict=False)
                            if location_address_lang[str(presetId)]:
                                location['address'] = location_address_lang[str(presetId)]
                        except:
                            pass
                    if location['contact_name_lang'] != '' and location['contact_name_lang'] != None:
                        try:
                            location_contact_name_lang = json.loads(location['contact_name_lang'], strict=False)
                            if location_contact_name_lang[str(presetId)]:
                                location['contact_name'] = location_contact_name_lang[str(presetId)]
                        except:
                            pass
                    location_dict = {
                        'id': location['id'],
                        'name': location['name'],
                        'description': location['description'] if location['description'] else '',
                        'address': location['address'] if location['address'] else '',
                        'contact_name': location['contact_name'] if location['contact_name'] else '',
                    }
                    location_array.append(location_dict)
                general_langs.append({"locations": location_array})

                for hotel in hotels:
                    if hotel['name_lang'] != '' and hotel['name_lang'] != None:
                        try:
                            hotel_name_lang = json.loads(hotel['name_lang'], strict=False)
                            if hotel_name_lang[str(presetId)]:
                                hotel['name'] = hotel_name_lang[str(presetId)]
                        except:
                            pass
                    hotel_dict = {
                        'id': hotel['id'],
                        'name': hotel['name'],
                    }
                    hotel_array.append(hotel_dict)
                general_langs.append({"hotels": hotel_array})

                for room in rooms:
                    if room['description_lang'] != '' and room['description_lang'] != None:
                        try:
                            room_description_lang = json.loads(room['description_lang'], strict=False)
                            if room_description_lang[str(presetId)]:
                                room['description'] = room_description_lang[str(presetId)]
                        except:
                            pass
                    room_dict = {
                        'id': room['id'],
                        'description': room['description'] if room['description'] else '',
                    }
                    room_array.append(room_dict)
                general_langs.append({"rooms": room_array})

                for group in groups:
                    if group['name_lang'] != '' and group['name_lang'] != None:
                        try:
                            group_name_lang = json.loads(group['name_lang'], strict=False)
                            if group_name_lang[str(presetId)]:
                                group['name'] = group_name_lang[str(presetId)]
                        except:
                            pass
                    group_dict = {
                        'id': group['id'],
                        'name': group['name']
                    }
                    group_array.append(group_dict)
                general_langs.append({"groups": group_array})

                for email in emails:
                    if email['subject_lang'] != '' and email['subject_lang'] != None:
                        try:
                            email_subject_lang = json.loads(email['subject_lang'], strict=False)
                            if email_subject_lang[str(presetId)]:
                                email['subject'] = email_subject_lang[str(presetId)]
                        except:
                            pass
                    email_dict = {
                        'id': email['id'],
                        'subject': email['subject']
                    }
                    emails_array.append(email_dict)
                general_langs.append({"emails": emails_array})

                for submit_button in submit_buttons:
                    if submit_button['answer'] != '' and submit_button['answer'] != None:
                        try:
                            submit_button_lang = json.loads(submit_button['answer'], strict=False)
                            if submit_button_lang[str(presetId)]:
                                submit_button['answer'] = submit_button_lang[str(presetId)]
                        except Exception as e:
                            if e.__class__.__name__ == "KeyError":
                                submit_button['answer'] = ''
                            pass
                    submit_button_dict = {
                        'id': submit_button['id'],
                        'answer': submit_button['answer']
                    }
                    submit_button_array.append(submit_button_dict)
                general_langs.append({"submit_buttons": submit_button_array})

                for pdf_button in pdf_buttons:
                    if pdf_button['answer'] != '' and pdf_button['answer'] != None:
                        try:
                            pdf_button_lang = json.loads(pdf_button['answer'], strict=False)
                            if pdf_button_lang[str(presetId)]:
                                pdf_button['answer'] = pdf_button_lang[str(presetId)]
                        except Exception as e:
                            if e.__class__.__name__ == "KeyError":
                                pdf_button['answer'] = ''
                            pass
                    pdf_button_dict = {
                        'id': pdf_button['id'],
                        'answer': pdf_button['answer']
                    }
                    pdf_button_array.append(pdf_button_dict)
                general_langs.append({"pdf_buttons": pdf_button_array})

                context = {
                    "general_langs": general_langs
                }
                return render(request, 'language/general_lang_render.html', context)

            else:
                for menu in menus:
                    menu_dict = {
                        'id': menu['id'],
                        'title': menu['title']
                    }
                    menu_array.append(menu_dict)
                general_langs.append({"menus": menu_array})
                for question in questions:
                    options = Option.objects.filter(question_id=question['id'])
                    option_array = []
                    for option in options:
                        option_dict = {
                            'option_id': option.id,
                            'option': option.option
                        }
                        option_array.append(option_dict)
                    question_dict = {
                        'id': question['id'],
                        'title': question['title'],
                        'description': question['description'] if question['description'] else '',
                        'options': option_array
                    }
                    question_array.append(question_dict)
                general_langs.append({"questions": menu_array})
                for session in sessions:
                    session_dict = {
                        'id': session['id'],
                        'name': session['name'],
                        'description': session['description'] if session['description'] else '',
                    }
                    session_array.append(session_dict)
                general_langs.append({"sessions": session_array})

                for travel in travels:
                    travel_dict = {
                        'id': travel['id'],
                        'name': travel['name'],
                        'description': travel['description'] if travel['description'] else '',
                    }
                    travel_array.append(travel_dict)
                general_langs.append({"travels": travel_array})

                for location in locations:
                    location_dict = {
                        'id': location['id'],
                        'name': location['name'],
                        'description': location['description'] if location['description'] else '',
                        'address': location['address'] if location['address'] else '',
                        'contact_name': location['contact_name'] if location['contact_name'] else '',
                    }
                    location_array.append(location_dict)
                general_langs.append({"locations": location_array})

                for hotel in hotels:
                    hotel_dict = {
                        'id': hotel['id'],
                        'name': hotel['name'],
                    }
                    hotel_array.append(hotel_dict)
                general_langs.append({"hotels": hotel_array})

                for room in rooms:
                    room_dict = {
                        'id': room['id'],
                        'description': room['description'] if room['description'] else '',
                    }
                    room_array.append(room_dict)
                general_langs.append({"rooms": room_array})

                for group in groups:
                    group_dict = {
                        'id': group['id'],
                        'name': group['name']
                    }
                    group_array.append(group_dict)
                general_langs.append({"groups": group_array})
                context = {
                    "general_langs": general_langs
                }
                return render(request, 'language/general_lang_render.html', context)
        except Exception as e:
            import traceback
            traceback.print_exc()
            # print(traceback.print_exc())
            # import sys, os
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # print(exc_type, fname, exc_tb.tb_lineno)
            context = {
                "general_langs": []
            }
            return render(request, 'language/general_lang_render.html', context)

    def get_date_time_preset(request):
        try:
            presetId = 0
            if request.GET.get('id') == "":
                presetId = 0
            else:
                presetId = request.GET.get('id')
            if presetId != "0":
                preset_data = Presets.objects.get(id=presetId)
                days = ['sunday','monday','tuesday','wednesday','thursday','friday','saturday']
                months = ['january','february','march','april','may','june','july','august','september','october','november','december']
                monthsFull=[]
                monthsShort=[]
                weekdaysShort=[]
                weekdaysFull=[]
                today = ''
                close = ''
                clear = ''
                firstDay = ''
                yesterday = ''
                tomorrow = ''
                if preset_data.datetime_language:
                    try:
                        preset_datetime_language_json =json.loads(preset_data.datetime_language)

                        weekdaysShort = preset_datetime_language_json['weekdaysShort']
                        weekdaysFull = preset_datetime_language_json['weekdaysFull']

                        monthsFull = preset_datetime_language_json['monthsFull']
                        monthsShort = preset_datetime_language_json['monthsShort']

                        today = preset_datetime_language_json['today']
                        close = preset_datetime_language_json['close']
                        clear = preset_datetime_language_json['clear']
                        firstDay = preset_datetime_language_json['firstDay']
                        yesterday = preset_datetime_language_json['yesterday']
                        tomorrow = preset_datetime_language_json['tomorrow']
                    except Exception as e:
                        ErrorR.efail(e)
                        pass


                context = {
                    "preset_date": preset_data,
                    "days":days,
                    "months":months,
                    "weekdaysFull":weekdaysFull,
                    "weekdaysShort":weekdaysShort,
                    "monthsFull":monthsFull,
                    "monthsShort":monthsShort,
                    "today":today,
                    "clear":clear,
                    "close":close,
                    "firstDay":firstDay,
                    "yesterday": yesterday,
                    "tomorrow": tomorrow
                }
                return render(request, 'language/date_time_lang_render.html', context)
            else:
                return "Preset Not found"
        except Exception as e:
            ErrorR.efail(e)
            return "Something went wrong"



    def all_key(request, element_id, preset=0):
        response_data = {}
        try:
            elementObj = Elements.objects.filter(id=element_id)
            if elementObj.exists():
                event_id = request.session['event_auth_user']['event_id']
                presets = Presets.objects.all()
                presetsEvent = PresetEvent.objects.filter(event_id=event_id)
                if presetsEvent.exists():
                    lang_data = ElementPresetLang.objects.filter(preset_id=presetsEvent[0].preset_id,
                                                                 element_default_lang__element_id=elementObj[0].id)
                    lang_key = {}
                    for lang in lang_data:
                        lang_key[lang.element_default_lang.lang_key] = lang.value

                    response_data['lang-key'] = lang_key
                else:
                    lang_data = ElementDefaultLang.objects.filter(element_id=elementObj[0].id)
                    lang_key = {}
                    for lang in lang_data:
                        lang_key[lang.lang_key] = lang.default_value
                    response_data['lang-key'] = lang_key
                return response_data
        except Exception as e:
            ErrorR.efail(e)
        response_data = {
            'error': True,
            'message': 'Something went wrong. Please try again.'
        }
        return response_data

    def add_preset(request):
        response_data = {}
        if EventView.check_permissions(request, 'language_permission'):
            try:
                preset = request.POST.get('preset')
                admin_id = request.session['event_auth_user']['id']
                event_id = request.session['event_auth_user']['event_id']
                try:
                    objPreset = Presets.objects.get(preset_name=preset, event_id=event_id)
                    response_data = {
                        'success': False,
                        'message': 'Preset Exist'
                    }
                except Presets.DoesNotExist:
                    objPreset = Presets(preset_name=preset, created_by_id=admin_id, event_id=event_id)
                    objPreset.save()
                    objPresetLang = ElementPresetLang()
                    objDefaultLang = ElementDefaultLang.objects.all()
                    insert_list = []
                    for defaultLang in objDefaultLang:
                        insert_list.append(
                            ElementPresetLang(value=defaultLang.default_value, element_default_lang_id=defaultLang.id,
                                              preset_id=objPreset.id))
                    ElementPresetLang.objects.bulk_create(insert_list)
                    response_data = {
                        'preset_id': objPreset.id,
                        'success': True,
                        'message': "Preset Added Successfully"
                    }
            except Exception as e:
                ErrorR.efail(e)
                response_data = {
                    'success': False,
                    'message': 'Something went wrong. Please try again.'
                }
        else:
            response_data = {
                'success': False,
                'message': 'You do not have Permission to do this'
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def rename_preset_name(request):
        if EventView.check_permissions(request, 'language_permission'):
            try:
                preset = request.POST.get('preset')
                preset_id = request.POST.get('preset_id')
                event_id = request.session['event_auth_user']['event_id']
                if not Presets.objects.filter(preset_name=preset, event_id=event_id).exclude(id=preset_id).exists():
                    Presets.objects.filter(id=preset_id).update(preset_name=preset)
                    response_data = {
                        'preset_id': preset_id,
                        'success': True,
                        'message': "Preset Renamed Successfully",
                    }
                else:
                    response_data = {
                        'success': False,
                        'message': 'Preset Exist'
                    }
            except Exception as e:
                ErrorR.efail(e)
                response_data = {
                    'success': False,
                    'message': 'Something went wrong. Please try again.'
                }
        else:
            response_data = {
                'success': False,
                'message': 'You do not have Permission to do this'
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_preset(request):
        response_data = {}
        if EventView.check_permissions(request, 'language_permission'):
            postData = request.POST
            token = set(["csrfmiddlewaretoken"])
            postData = [data for data in postData if data not in token]
            sql_lang_case = ""
            lang_ids = []
            for data in postData:
                # value = str(request.POST.get(data)).replace('"', "'")
                value = str(request.POST.get(data)).replace('"','\\"')
                sql_lang_case += 'WHEN id = ' + str(data) + ' THEN "' + value + '" '
                lang_ids.append(str(data))
                # ElementPresetLang.objects.filter(id=int(data)).update(value=request.POST.get(data))
            sql_case = "value = CASE " + sql_lang_case + "END"
            sql = 'update element_preset_lang set ' + sql_case + ' WHERE id IN (' + str(lang_ids).replace("[",
                                                                                                          "").replace(
                "]", "") + ')'
            cursor = connection.cursor()
            cursor.execute(sql)
            response_data['message'] = "Language Update Successfully"
            response_data['success'] = True
        else:
            response_data['message'] = "You do not have Permission to do this"
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_date_time_preset(request):
        response_data = {}
        if EventView.check_permissions(request, 'language_permission'):
            try:
                preset_id = request.POST.get('preset_id')
                datetime_language = request.POST.get('datetime_language')


                preset_form = {
                    "date_format": request.POST.get('preset_date_format'),
                    "time_format": request.POST.get('preset_time_format'),
                    "datetime_format": request.POST.get('preset_date_time_format'),
                    "language_code": request.POST.get('preset_date_time_language'),
                    "datetime_language":datetime_language
                }
                Presets.objects.filter(id=preset_id).update(**preset_form)
                response_data['message'] = "language Update Successfully"
                response_data['success'] = True
            except Exception as e:
                ErrorR.efail(e)
                response_data['message'] = "Something went wrong. Please try again"
                response_data['success'] = False
        else:
            response_data['message'] = "You do not have Permission to do this"
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_preset(request):
        response_data = {}
        if EventView.check_permissions(request, 'language_permission'):
            try:
                postDataId = request.POST.get('id')
                default_presets = [6, 7]
                non_deleted_preset_ids = []
                non_deleted_presets = Presets.objects.filter(id__in=default_presets)
                for preset in non_deleted_presets:
                    non_deleted_preset_ids.append(preset.id)
                event_id = request.session['event_auth_user']['event_id']
                presetsEvent = PresetEvent.objects.filter(event_id=event_id).first()
                non_deleted_preset_ids.append(presetsEvent.preset_id)
                if int(postDataId) in non_deleted_preset_ids:
                    response_data['message'] = "You can't delete the Default Presets"
                    response_data['success'] = False
                else:
                    preset_attendees = Attendee.objects.filter(language_id=postDataId, status="registered")
                    preset_attendees.update(language_id=presetsEvent.preset_id)
                    Presets.objects.filter(id=postDataId).delete()
                    response_data['success'] = True
                    response_data['id'] = postDataId
            except Exception as e:
                ErrorR.efail(e)
                response_data['message'] = "Something went wrong"
                response_data['success'] = False
        else:
            response_data['message'] = "You do not have Permission to do this"
            response_data['success'] = False
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def save_general_language(request):
        response = {}
        if EventView.check_permissions(request, 'language_permission'):
            try:
                event_id = request.session['event_auth_user']['event_id']
                preset_id = request.POST.get('preset_id')
                menus_lang = json.loads(request.POST.get('menus'))
                questions_lang = json.loads(request.POST.get('questions'))
                options_lang = json.loads(request.POST.get('options'))
                sessions_lang = json.loads(request.POST.get('sessions'))
                travels_lang = json.loads(request.POST.get('travels'))
                locations_lang = json.loads(request.POST.get('locations'))
                hotels_lang = json.loads(request.POST.get('hotels'))
                rooms_lang = json.loads(request.POST.get('rooms'))
                groups_lang = json.loads(request.POST.get('groups'))
                emails_lang = json.loads(request.POST.get('emails'))
                submit_buttons_lang = json.loads(request.POST.get('submit_buttons'))
                pdf_buttons_lang = json.loads(request.POST.get('pdf_buttons'))

                menus = MenuItem.objects.values('id', 'title', 'title_lang').filter(event_id=event_id)
                questions = Questions.objects.values('id', 'title', 'description', 'title_lang',
                                                     'description_lang').filter(
                    group__event_id=event_id)
                options = Option.objects.values('id', 'option', 'option_lang').filter(
                    question__group__event_id=event_id)
                sessions = Session.objects.values('id', 'name', 'name_lang', 'description', 'description_lang').filter(
                    group__event_id=event_id)
                travels = Travel.objects.values('id', 'name', 'name_lang', 'description', 'description_lang').filter(
                    group__event_id=event_id)
                locations = Locations.objects.values('id', 'name', 'name_lang', 'description', 'description_lang',
                                                     'address', 'address_lang', 'contact_name',
                                                     'contact_name_lang').filter(
                    group__event_id=event_id)
                hotels = Hotel.objects.values('id', 'name', 'name_lang').filter(group__event_id=event_id)
                rooms = Room.objects.values('id', 'description', 'description_lang').filter(
                    hotel__group__event_id=event_id)
                groups = Group.objects.values('id', 'name', 'name_lang').filter(event_id=event_id).exclude(type='email')
                emails = EmailContents.objects.values('id', 'subject', 'subject_lang').filter(template__event_id=event_id)
                submit_buttons = ElementsAnswers.objects.values('id', 'answer').filter(page__event_id=event_id,element_question_id=69)
                pdf_buttons = ElementsAnswers.objects.values('id', 'answer').filter(page__event_id=event_id,element_question_id=343)

                cursor = connection.cursor()

                # update Menu Language
                save_menus = LanguageView.save_menu_lang(request, menus, menus_lang, preset_id)
                if save_menus['success']:
                    cursor.execute(save_menus['sql'])
                # update Questions Language
                save_questions = LanguageView.save_question_lang(request, questions, questions_lang, preset_id)
                if save_questions['success']:
                    cursor.execute(save_questions['sql'])
                # update Options Language
                save_options = LanguageView.save_option_lang(request, options, options_lang, preset_id)
                if save_options['success']:
                    cursor.execute(save_options['sql'])
                # update Sessions Language
                save_sessions = LanguageView.save_session_lang(request, sessions, sessions_lang, preset_id)
                if save_sessions['success']:
                    cursor.execute(save_sessions['sql'])
                # update Travels Language
                save_travels = LanguageView.save_travel_lang(request, travels, travels_lang, preset_id)
                if save_travels['success']:
                    cursor.execute(save_travels['sql'])
                # update Locations Language
                save_locations = LanguageView.save_location_lang(request, locations, locations_lang, preset_id)
                if save_locations['success']:
                    cursor.execute(save_locations['sql'])
                # update Hotels Language
                save_hotels = LanguageView.save_hotel_lang(request, hotels, hotels_lang, preset_id)
                if save_hotels['success']:
                    cursor.execute(save_hotels['sql'])
                # update Rooms Language
                save_rooms = LanguageView.save_room_lang(request, rooms, rooms_lang, preset_id)
                if save_rooms['success']:
                    cursor.execute(save_rooms['sql'])
                # update Groups Language
                save_groups = LanguageView.save_group_lang(request, groups, groups_lang, preset_id)
                if save_groups['success']:
                    cursor.execute(save_groups['sql'])
                # update Emails Language
                save_emails = LanguageView.save_email_lang(request, emails, emails_lang, preset_id)
                if save_emails['success']:
                    cursor.execute(save_emails['sql'])
                # update Submit Buttons Language
                save_submit_buttons = LanguageView.save_submit_buttons_lang(request, submit_buttons, submit_buttons_lang, preset_id)
                if save_submit_buttons['success']:
                    cursor.execute(save_submit_buttons['sql'])
                # update PDF Buttons Language
                save_pdf_buttons = LanguageView.save_pdf_buttons_lang(request, pdf_buttons,
                                                                            pdf_buttons_lang, preset_id)
                if save_pdf_buttons['success']:
                    cursor.execute(save_pdf_buttons['sql'])
                response['success'] = True
                response['message'] = "Language Update Successfully"
            except Exception as e:
                ErrorR.efail(e)
                response['success'] = False
                response['message'] = "Something Went wrong. Please try again"
        else:
            response['success'] = False
            response['message'] = "You do not have Permission to do this"
        return HttpResponse(json.dumps(response), content_type="application/json")

    def get_current_preset(request):
        event_id = request.session['event_auth_user']['event_id']
        presetsEvent = PresetEvent.objects.filter(event_id=event_id)
        if presetsEvent.exists():
            presetsEvent = presetsEvent[0]
        else:
            presetsEvent = None
        return presetsEvent

    def get_current_public_preset(request):
        event_id = request.session['event_id']
        presetsEvent = PresetEvent.objects.filter(event_id=event_id)
        if presetsEvent.exists():
            presetsEvent = presetsEvent[0]
        else:
            presetsEvent = None
        return presetsEvent

    def save_menu_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'title_' + str(data['id']) in datas_lang:
                    if data['title_lang'] != '' and data['title_lang'] != None:
                        menu_title_lang = json.loads(data['title_lang'], strict=False)
                        menu_title_lang[str(preset_id)] = datas_lang['title_' + str(data['id'])]
                    else:
                        menu_title_lang = {str(preset_id): datas_lang['title_' + str(data['id'])]}
                    data['title_lang'] = str(menu_title_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'title_lang': data['title_lang']})
                    data_ids.append(data['id'])
            sql_title_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_title = d_data["title_lang"]
                sql_title_case += "WHEN id = " + d_id + " THEN '" + str(d_title) + "' "
            if sql_title_case != "":
                sql_case = 'title_lang = CASE ' + sql_title_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('menu_items', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_option_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'option_' + str(data['id']) in datas_lang:
                    if data['option_lang'] != '' and data['option_lang'] != None:
                        option_lang = json.loads(data['option_lang'], strict=False)
                        option_lang[str(preset_id)] = datas_lang['option_' + str(data['id'])]
                    else:
                        option_lang = {str(preset_id): datas_lang['option_' + str(data['id'])]}
                    data['option_lang'] = str(option_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'option_lang': data['option_lang']})
                    data_ids.append(data['id'])
            sql_option_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_option = d_data["option_lang"]
                sql_option_case += "WHEN id = " + d_id + " THEN '" + str(d_option) + "' "
            if sql_option_case != "":
                sql_case = 'option_lang = CASE ' + sql_option_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('options', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_question_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                data_dict = {
                    'id': str(data['id'])
                }
                ErrorR.okblue(str(data['id']))
                if 'title_' + str(data['id']) in datas_lang:
                    if data['title_lang'] != '' and data['title_lang'] != None:
                        question_title_lang = json.loads(data['title_lang'], strict=False)
                        question_title_lang[str(preset_id)] = datas_lang['title_' + str(data['id'])]
                    else:
                        question_title_lang = {str(preset_id): datas_lang['title_' + str(data['id'])]}
                    data_dict['title_lang'] = str(question_title_lang).replace("'", '"')
                if 'description_' + str(data['id']) in datas_lang:
                    if data['description_lang'] != '' and data['description_lang'] != None:
                        question_description_lang = json.loads(data['description_lang'], strict=False)
                        question_description_lang[str(preset_id)] = datas_lang['description_' + str(data['id'])]
                    else:
                        question_description_lang = {str(preset_id): datas_lang['description_' + str(data['id'])]}
                    data_dict['description_lang'] = str(question_description_lang).replace("'", '"')
                data_array.append(data_dict)
                data_ids.append(data['id'])
            sql_title_case = ''
            sql_description_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                if 'title_lang' in d_data:
                    d_title = d_data["title_lang"]
                    sql_title_case += "WHEN id = " + d_id + " THEN '" + str(d_title) + "' "
                if 'description_lang' in d_data:
                    d_description = d_data["description_lang"]
                    sql_description_case += "WHEN id = " + d_id + " THEN '" + str(d_description) + "' "
            if sql_title_case != "" or sql_description_case != "":
                sql_case_array = []
                if sql_title_case != "":
                    sql_case_array.append('title_lang = CASE ' + sql_title_case + 'END')
                if sql_description_case != "":
                    sql_case_array.append('description_lang = CASE ' + sql_description_case + 'END')
                sql_case = ','.join(sql_case_array)
                response['success'] = True
                sql = LanguageView.create_language_sql('questions', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_session_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                data_dict = {
                    'id': str(data['id'])
                }
                if 'name_' + str(data['id']) in datas_lang:
                    if data['name_lang'] != '' and data['name_lang'] != None:
                        name_lang = json.loads(data['name_lang'], strict=False)
                        name_lang[str(preset_id)] = datas_lang['name_' + str(data['id'])]
                    else:
                        name_lang = {str(preset_id): datas_lang['name_' + str(data['id'])]}
                    data_dict['name_lang'] = str(name_lang).replace("'", '"')
                if 'description_' + str(data['id']) in datas_lang:
                    if data['description_lang'] != '' and data['description_lang'] != None:
                        description_lang = json.loads(data['description_lang'], strict=False)
                        description_lang[str(preset_id)] = datas_lang['description_' + str(data['id'])]
                    else:
                        description_lang = {str(preset_id): datas_lang['description_' + str(data['id'])]}
                    data_dict['description_lang'] = str(description_lang).replace("'", '"')
                data_array.append(data_dict)
                data_ids.append(data['id'])
            sql_name_case = ''
            sql_description_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                if 'name_lang' in d_data:
                    d_name = d_data["name_lang"]
                    sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
                if 'description_lang' in d_data:
                    d_description = d_data["description_lang"]
                    sql_description_case += "WHEN id = " + d_id + " THEN '" + str(d_description) + "' "
            if sql_name_case != "" or sql_description_case != "":
                sql_case_array = []
                if sql_name_case != "":
                    sql_case_array.append('name_lang = CASE ' + sql_name_case + 'END')
                if sql_description_case != "":
                    sql_case_array.append('description_lang = CASE ' + sql_description_case + 'END')
                sql_case = ','.join(sql_case_array)
                response['success'] = True
                sql = LanguageView.create_language_sql('sessions', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_travel_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                data_dict = {
                    'id': str(data['id'])
                }
                if 'name_' + str(data['id']) in datas_lang:
                    if data['name_lang'] != '' and data['name_lang'] != None:
                        name_lang = json.loads(data['name_lang'], strict=False)
                        name_lang[str(preset_id)] = datas_lang['name_' + str(data['id'])]
                    else:
                        name_lang = {str(preset_id): datas_lang['name_' + str(data['id'])]}
                    data_dict['name_lang'] = str(name_lang).replace("'", '"')
                if 'description_' + str(data['id']) in datas_lang:
                    if data['description_lang'] != '' and data['description_lang'] != None:
                        description_lang = json.loads(data['description_lang'], strict=False)
                        description_lang[str(preset_id)] = datas_lang['description_' + str(data['id'])]
                    else:
                        description_lang = {str(preset_id): datas_lang['description_' + str(data['id'])]}
                    data_dict['description_lang'] = str(description_lang).replace("'", '"')
                data_array.append(data_dict)
                data_ids.append(data['id'])
            sql_name_case = ''
            sql_description_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                if 'name_lang' in d_data:
                    d_name = d_data["name_lang"]
                    sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
                if 'description_lang' in d_data:
                    d_description = d_data["description_lang"]
                    sql_description_case += "WHEN id = " + d_id + " THEN '" + str(d_description) + "' "
            if sql_name_case != "" or sql_description_case != "":
                sql_case_array = []
                if sql_name_case != "":
                    sql_case_array.append('name_lang = CASE ' + sql_name_case + 'END')
                if sql_description_case != "":
                    sql_case_array.append('description_lang = CASE ' + sql_description_case + 'END')
                sql_case = ','.join(sql_case_array)
                response['success'] = True
                sql = LanguageView.create_language_sql('travels', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_location_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                data_dict = {
                    'id': str(data['id'])
                }
                if 'name_' + str(data['id']) in datas_lang:
                    if data['name_lang'] != '' and data['name_lang'] != None:
                        name_lang = json.loads(data['name_lang'], strict=False)
                        name_lang[str(preset_id)] = datas_lang['name_' + str(data['id'])]
                    else:
                        name_lang = {str(preset_id): datas_lang['name_' + str(data['id'])]}
                    data_dict['name_lang'] = str(name_lang).replace("'", '"')
                if 'description_' + str(data['id']) in datas_lang:
                    if data['description_lang'] != '' and data['description_lang'] != None:
                        description_lang = json.loads(data['description_lang'], strict=False)
                        description_lang[str(preset_id)] = datas_lang['description_' + str(data['id'])]
                    else:
                        description_lang = {str(preset_id): datas_lang['description_' + str(data['id'])]}
                    data_dict['description_lang'] = str(description_lang).replace("'", '"')
                if 'address_' + str(data['id']) in datas_lang:
                    if data['address_lang'] != '' and data['address_lang'] != None:
                        address_lang = json.loads(data['address_lang'], strict=False)
                        address_lang[str(preset_id)] = datas_lang['address_' + str(data['id'])]
                    else:
                        address_lang = {str(preset_id): datas_lang['address_' + str(data['id'])]}
                    data_dict['address_lang'] = str(address_lang).replace("'", '"')
                if 'contact_name_' + str(data['id']) in datas_lang:
                    if data['contact_name_lang'] != '' and data['contact_name_lang'] != None:
                        contact_name_lang = json.loads(data['contact_name_lang'], strict=False)
                        contact_name_lang[str(preset_id)] = datas_lang['contact_name_' + str(data['id'])]
                    else:
                        contact_name_lang = {str(preset_id): datas_lang['contact_name_' + str(data['id'])]}
                    data_dict['contact_name_lang'] = str(contact_name_lang).replace("'", '"')
                data_array.append(data_dict)
                data_ids.append(data['id'])
            sql_name_case = ''
            sql_description_case = ''
            sql_address_case = ''
            sql_contact_name_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                if 'name_lang' in d_data:
                    d_name = d_data["name_lang"]
                    sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
                if 'description_lang' in d_data:
                    d_description = d_data["description_lang"]
                    sql_description_case += "WHEN id = " + d_id + " THEN '" + str(d_description) + "' "
                if 'address_lang' in d_data:
                    d_address = d_data["address_lang"]
                    sql_address_case += "WHEN id = " + d_id + " THEN '" + str(d_address) + "' "
                if 'contact_name_lang' in d_data:
                    d_contact_name = d_data["address_lang"]
                    sql_contact_name_case += "WHEN contact_name_lang = " + d_id + " THEN '" + str(d_contact_name) + "' "
            if sql_name_case != "" or sql_description_case != "" or sql_address_case != "" or sql_contact_name_case != "":
                sql_case_array = []
                if sql_name_case != "":
                    sql_case_array.append('name_lang = CASE ' + sql_name_case + 'END')
                if sql_description_case != "":
                    sql_case_array.append('description_lang = CASE ' + sql_description_case + 'END')
                if sql_address_case != "":
                    sql_case_array.append('address_lang = CASE ' + sql_address_case + 'END')
                if sql_contact_name_case != "":
                    sql_case_array.append('contact_name_lang = CASE ' + sql_contact_name_case + 'END')
                sql_case = ','.join(sql_case_array)
                response['success'] = True
                sql = LanguageView.create_language_sql('locations', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_hotel_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'name_' + str(data['id']) in datas_lang:
                    if data['name_lang'] != '' and data['name_lang'] != None:
                        name_lang = json.loads(data['name_lang'], strict=False)
                        name_lang[str(preset_id)] = datas_lang['name_' + str(data['id'])]
                    else:
                        name_lang = {str(preset_id): datas_lang['name_' + str(data['id'])]}
                    data['name_lang'] = str(name_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'name_lang': data['name_lang']})
                    data_ids.append(data['id'])
            sql_name_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_name = d_data["name_lang"]
                sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
            if sql_name_case != "":
                sql_case = 'name_lang = CASE ' + sql_name_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('hotels', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_room_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'description_' + str(data['id']) in datas_lang:
                    if data['description_lang'] != '' and data['description_lang'] != None:
                        description_lang = json.loads(data['description_lang'], strict=False)
                        description_lang[str(preset_id)] = datas_lang['description_' + str(data['id'])]
                    else:
                        description_lang = {str(preset_id): datas_lang['description_' + str(data['id'])]}
                    data['description_lang'] = str(description_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'description_lang': data['description_lang']})
                    data_ids.append(data['id'])
            sql_description_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_description = d_data["description_lang"]
                sql_description_case += "WHEN id = " + d_id + " THEN '" + str(d_description) + "' "
            if sql_description_case != "":
                sql_case = 'description_lang = CASE ' + sql_description_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('rooms', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_group_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'name_' + str(data['id']) in datas_lang:
                    if data['name_lang'] != '' and data['name_lang'] != None:
                        name_lang = json.loads(data['name_lang'], strict=False)
                        name_lang[str(preset_id)] = datas_lang['name_' + str(data['id'])]
                    else:
                        name_lang = {str(preset_id): datas_lang['name_' + str(data['id'])]}
                    data['name_lang'] = str(name_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'name_lang': data['name_lang']})
                    data_ids.append(data['id'])
            sql_name_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_name = d_data["name_lang"]
                sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
            if sql_name_case != "":
                sql_case = 'name_lang = CASE ' + sql_name_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('groups', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_email_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'subject_' + str(data['id']) in datas_lang:
                    if data['subject_lang'] != '' and data['subject_lang'] != None:
                        name_lang = json.loads(data['subject_lang'], strict=False)
                        name_lang[str(preset_id)] = datas_lang['subject_' + str(data['id'])]
                    else:
                        name_lang = {str(preset_id): datas_lang['subject_' + str(data['id'])]}
                    data['subject_lang'] = str(name_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'subject_lang': data['subject_lang']})
                    data_ids.append(data['id'])
            sql_name_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_name = d_data["subject_lang"]
                sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
            if sql_name_case != "":
                sql_case = 'subject_lang = CASE ' + sql_name_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('email_contents', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_submit_buttons_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'answer_' + str(data['id']) in datas_lang:
                    if data['answer'] != '' and data['answer'] != None:
                        try:
                            name_lang = json.loads(data['answer'], strict=False)
                            name_lang[str(preset_id)] = datas_lang['answer_' + str(data['id'])]
                        except:
                            name_lang = {str(preset_id): datas_lang['answer_' + str(data['id'])]}
                            pass
                    else:
                        name_lang = {str(preset_id): datas_lang['answer_' + str(data['id'])]}
                    data['answer'] = str(name_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'answer': data['answer']})
                    data_ids.append(data['id'])
            sql_name_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_name = d_data["answer"]
                sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
            if sql_name_case != "":
                sql_case = 'answer = CASE ' + sql_name_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('elements_answers', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def save_pdf_buttons_lang(request, datas, datas_lang, preset_id):
        response = {}
        try:
            data_array = []
            data_ids = []
            for data in datas:
                if 'answer_' + str(data['id']) in datas_lang:
                    if data['answer'] != '' and data['answer'] != None:
                        try:
                            name_lang = json.loads(data['answer'], strict=False)
                            name_lang[str(preset_id)] = datas_lang['answer_' + str(data['id'])]
                        except:
                            name_lang = {str(preset_id): datas_lang['answer_' + str(data['id'])]}
                            pass
                    else:
                        name_lang = {str(preset_id): datas_lang['answer_' + str(data['id'])]}
                    data['answer'] = str(name_lang).replace("'", '"')
                    data_array.append({'id': str(data['id']), 'answer': data['answer']})
                    data_ids.append(data['id'])
            sql_name_case = ''
            for d_data in data_array:
                d_id = d_data["id"]
                d_name = d_data["answer"]
                sql_name_case += "WHEN id = " + d_id + " THEN '" + str(d_name) + "' "
            if sql_name_case != "":
                sql_case = 'answer = CASE ' + sql_name_case + 'END'
                response['success'] = True
                sql = LanguageView.create_language_sql('elements_answers', sql_case, data_ids)
                response['sql'] = sql
            else:
                response['success'] = False
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
        return response

    def create_language_sql(table_name, sql_case, data_ids):
        sql = 'update ' + table_name + ' set ' + sql_case + ' WHERE id IN (' + str(data_ids).replace("[", "").replace(
            "]", "") + ')'
        return sql
