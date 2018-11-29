from django.views import generic
from app.models import Elements, PresetEvent, ElementPresetLang, ElementDefaultLang, Presets
from app.views.gbhelper.error_report_helper import ErrorR
import json


class LanguageKey(generic.TemplateView):
    def get_lang_key(request, element_id, preset=0):
        language_id = request.session['language_id']
        response_data = {}
        try:
            elementObj = Elements.objects.get(id=element_id)
            if elementObj:
                lang_data = ElementPresetLang.objects.select_related('element_default_lang').filter(preset_id=language_id,
                                                             element_default_lang__element_id=element_id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.element_default_lang.lang_key] = lang.value

                response_data['langkey'] = lang_key
                response_data['lang_preset'] = Presets.objects.get(id=language_id)
                return response_data
        except Exception as e:
            ErrorR.efail(e)
        response_data = {
            'error': True,
            'message': 'Something went wrong with language setting. Please try again.'
        }
        return response_data

    # catch_lang_key(2,"element-key","lang-key")
    # Return a string
    def catch_lang_key(request, element_name, lang_key):
        try:
            element = Elements.objects.get(slug=element_name)
            lang = LanguageKey.get_lang_key(request, element.id)
            return lang['langkey'][lang_key]
        except Exception as e:
            ErrorR.efail(e)

     # catch_lang_key_multiple(2,"element-key","lang-keys[]")
    # Return a array
    def catch_lang_key_multiple(request, element_name, lang_keys):
        response = {}
        try:
            element = Elements.objects.get(slug=element_name)
            language_id = request.session['language_id']
            elementObj = Elements.objects.filter(id=element.id)
            if elementObj.exists():
                lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                             element_default_lang__element_id=elementObj[0].id,element_default_lang__lang_key__in=lang_keys)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.element_default_lang.lang_key] = lang.value
                response['langkey'] = lang_key
                return response
        except Exception as e:
            ErrorR.efail(e)

    # Return object
    def catch_lang_key_obj(request, element_name):
        try:
            element = Elements.objects.filter(slug=element_name)
            lang = LanguageKey.get_lang_key(request, element[0].id)
            return lang
        except Exception as e:
            ErrorR.efail(e)

    def get_session_details_lang(request):
        response_data = {}
        event_id = request.session['event_id']
        language_id = request.session['language_id']
        try:
            elementObj = Elements.objects.filter(slug='session-details')
            if elementObj.exists():
                lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                             element_default_lang__element_id=elementObj[0].id).select_related('element_default_lang')
                if lang_data.exists():
                    lang_key = {}
                    for lang in lang_data:
                        lang_key[lang.element_default_lang.lang_key] = lang.value

                    response_data['langkey'] = lang_key
                else:
                    default_lang_data = ElementDefaultLang.objects.filter(element_id=elementObj[0].id)
                    lang_key = {}
                    for lang in default_lang_data:
                        lang_key[lang.lang_key] = lang.default_value
                    response_data['langkey'] = lang_key
            else:
                response_data = {
                    'error': True,
                    'langkey': "",
                    'message': 'Something went wrong with language setting. Please try again.'
                }
        except Exception as e:
            ErrorR.efail(e)
            response_data = {
                'error': True,
                'langkey': "",
                'message': 'Something went wrong with language setting. Please try again.'
            }
        response_data['lang_preset'] = Presets.objects.get(id=language_id)
        return response_data

    def get_question_data_by_language(request, question):
        language_id = request.session['language_id']
        if question.title_lang != '' and question.title_lang != None:
            try:
                question_title_lang = json.loads(question.title_lang, strict=False)
                if question_title_lang[str(language_id)]:
                    question.title = LanguageKey.html_decode(question_title_lang[str(language_id)])
            except:
                pass
        if question.description_lang != '' and question.description_lang != None:
            try:
                question_description_lang = json.loads(question.description_lang, strict=False)
                if question_description_lang[str(language_id)]:
                    question.description = LanguageKey.html_decode(question_description_lang[str(language_id)])
            except:
                pass
        return question

    def get_session_data_by_language(request, session):
        language_id = request.session['language_id']
        if session.name_lang != '' and session.name_lang != None:
            try:
                session_name_lang = json.loads(session.name_lang, strict=False)
                if session_name_lang[str(language_id)]:
                    session.name = LanguageKey.html_decode(session_name_lang[str(language_id)])
            except:
                pass
        if session.description_lang != '' and session.description_lang != None:
            try:
                session_description_lang = json.loads(session.description_lang, strict=False)
                if session_description_lang[str(language_id)]:
                    session.description = LanguageKey.html_decode(session_description_lang[str(language_id)])
            except:
                pass
        session.location = LanguageKey.get_location_data_by_language(request, session.location)
        session.group = LanguageKey.get_group_data_by_language(request, session.group)
        return session

    def get_travel_data_by_language(request, travel):
        language_id = request.session['language_id']
        if travel.name_lang != '' and travel.name_lang != None:
            try:
                travel_name_lang = json.loads(travel.name_lang, strict=False)
                if travel_name_lang[str(language_id)]:
                    travel.name = LanguageKey.html_decode(travel_name_lang[str(language_id)])
            except:
                pass
        if travel.description_lang != '' and travel.description_lang != None:
            try:
                travel_description_lang = json.loads(travel.description_lang, strict=False)
                if travel_description_lang[str(language_id)]:
                    travel.description = LanguageKey.html_decode(travel_description_lang[str(language_id)])
            except:
                pass
        travel.location = LanguageKey.get_location_data_by_language(request, travel.location)
        travel.group = LanguageKey.get_group_data_by_language(request, travel.group)
        return travel

    def get_location_data_by_language(request, location):
        language_id = request.session['language_id']
        if location.name_lang != '' and location.name_lang != None:
            try:
                location_name_lang = json.loads(location.name_lang, strict=False)
                if location_name_lang[str(language_id)]:
                    location.name = LanguageKey.html_decode(location_name_lang[str(language_id)])
            except:
                pass
        if location.description_lang != '' and location.description_lang != None:
            try:
                location_description_lang = json.loads(location.description_lang, strict=False)
                if location_description_lang[str(language_id)]:
                    location.description = LanguageKey.html_decode(location_description_lang[str(language_id)])
            except:
                pass
        if location.address_lang != '' and location.address_lang != None:
            try:
                location_address_lang = json.loads(location.address_lang, strict=False)
                if location_address_lang[str(language_id)]:
                    location.address = LanguageKey.html_decode(location_address_lang[str(language_id)])
            except:
                pass
        if location.contact_name_lang != '' and location.contact_name_lang != None:
            try:
                location_contact_name_lang = json.loads(location.contact_name_lang, strict=False)
                if location_contact_name_lang[str(language_id)]:
                    location.contact_name = LanguageKey.html_decode(location_contact_name_lang[str(language_id)])
            except:
                pass
        return location

    def get_option_data_by_language(request, option):
        language_id = request.session['language_id']
        if option.option_lang != '' and option.option_lang != None:
            try:
                option_lang = json.loads(option.option_lang, strict=False)
                # print(option_lang)
                if option_lang[str(language_id)]:
                    option.option = LanguageKey.html_decode(option_lang[str(language_id)])
            except:
                pass
        return option

    def get_hotel_data_by_language(request, hotel):
        language_id = request.session['language_id']
        if hotel.name_lang != '' and hotel.name_lang != None:
            try:
                hotel_name_lang = json.loads(hotel.name_lang, strict=False)
                if hotel_name_lang[str(language_id)]:
                    hotel.name = LanguageKey.html_decode(hotel_name_lang[str(language_id)])
            except:
                pass
        hotel.group = LanguageKey.get_group_data_by_language(request, hotel.group)
        hotel.location = LanguageKey.get_location_data_by_language(request, hotel.location)
        return hotel

    def get_room_data_by_language(request, room):
        language_id = request.session['language_id']
        if room.description_lang != '' and room.description_lang != None:
            try:
                room_description_lang = json.loads(room.description_lang, strict=False)
                if room_description_lang[str(language_id)]:
                    room.description = LanguageKey.html_decode(room_description_lang[str(language_id)])

            except:
                pass
        room.hotel = LanguageKey.get_hotel_data_by_language(request, room.hotel)
        return room

    def get_group_data_by_language(request, group):
        language_id = request.session['language_id']
        if group.name_lang != '' and group.name_lang != None:
            try:
                group_name_lang = json.loads(group.name_lang, strict=False)
                if group_name_lang[str(language_id)]:
                    group.name = LanguageKey.html_decode(group_name_lang[str(language_id)])
            except:
                pass
        return group

    def get_plugin_description_by_language(request, description):
        if description != "":
            try:
                msg = json.loads(description, strict=False)
                if msg[str(request.session["language_id"])]:
                    description = msg[str(request.session["language_id"])]
            except Exception as e:
                ErrorR.efail(e)
                try:
                    current_language = LanguageKey.get_current_language(request)
                    msg = json.loads(description, strict=False)
                    if msg[str(current_language.preset_id)]:
                        description = msg[str(current_language.preset_id)]
                except:
                    description = ""
        description = LanguageKey.html_decode(description)
        return description

    def get_current_language(request):
        event_id = request.session['event_id']
        presetsEvent = PresetEvent.objects.filter(event_id=event_id)
        if presetsEvent.exists():
            presetsEvent = presetsEvent[0]
        else:
            presetsEvent = None
        return presetsEvent

    def html_decode(s):
        """
        Returns the ASCII decoded version of the given HTML string. This does
        NOT remove normal HTML tags like <p>.
        """
        htmlCodes = (
                # ("'", '&#39;'),
                ('"', '&quot;'),
                # ('>', '&gt;'),
                # ('<', '&lt;'),
                ('&', '&amp;')
            )
        for code in htmlCodes:
            s = s.replace(code[1], code[0])
        return s
