from django.views import generic
from app.models import Elements, Presets, PresetEvent, ElementPresetLang, ElementDefaultLang, Attendee
from app.views.gbhelper.error_report_helper import ErrorR
import json
from django.db.models import Q


class LanguageH(generic.TemplateView):
    def get_lang_key(event_id, language_id, element_id, preset=0):
        response_data = {}
        try:
            elementObj = Elements.objects.filter(id=element_id)
            if elementObj.exists():
                # presets = Presets.objects.all()
                # presetsEvent = PresetEvent.objects.filter(event_id=event_id)
                # if presetsEvent.exists():
                lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                             element_default_lang__element_id=elementObj[0].id)
                lang_key = {}
                for lang in lang_data:
                    lang_key[lang.element_default_lang.lang_key] = lang.value

                response_data['langkey'] = lang_key
                response_data['lang_preset'] = Presets.objects.get(id=language_id)
                # else:
                #     lang_data = ElementDefaultLang.objects.filter(element_id=elementObj[0].id)
                #     lang_key = {}
                #     for lang in lang_data:
                #         lang_key[lang.lang_key] = lang.default_value
                #     response_data['langkey'] = lang_key
                return response_data
        except Exception as e:
            ErrorR.efail(e)
        response_data = {
            'error': True,
            'message': 'Something went wrong with language setting. Please try again.'
        }
        return response_data

    def get_question_data_by_language(language_id, question):
        if question.title_lang != '' and question.title_lang != None:
            try:
                question_title_lang = json.loads(question.title_lang, strict=False)
                if question_title_lang[str(language_id)]:
                    question.title = question_title_lang[str(language_id)]
            except:
                pass
        if question.description_lang != '' and question.description_lang != None:
            try:
                question_description_lang = json.loads(question.description_lang, strict=False)
                if question_description_lang[str(language_id)]:
                    question.description = question_description_lang[str(language_id)]
            except:
                pass
        return question

    def get_session_data_by_language(language_id, session):
        if session.name_lang != '' and session.name_lang != None:
            try:
                session_name_lang = json.loads(session.name_lang, strict=False)
                if session_name_lang[str(language_id)]:
                    session.name = session_name_lang[str(language_id)]
            except:
                pass
        if session.description_lang != '' and session.description_lang != None:
            try:
                session_description_lang = json.loads(session.description_lang, strict=False)
                if session_description_lang[str(language_id)]:
                    session.description = session_description_lang[str(language_id)]
            except:
                pass
        session.location = LanguageH.get_location_data_by_language(language_id, session.location)
        session.group = LanguageH.get_group_data_by_language(language_id, session.group)
        return session

    def get_travel_data_by_language(language_id, travel):
        if travel.name_lang != '' and travel.name_lang != None:
            try:
                travel_name_lang = json.loads(travel.name_lang, strict=False)
                if travel_name_lang[str(language_id)]:
                    travel.name = travel_name_lang[str(language_id)]
            except:
                pass
        if travel.description_lang != '' and travel.description_lang != None:
            try:
                travel_description_lang = json.loads(travel.description_lang, strict=False)
                if travel_description_lang[str(language_id)]:
                    travel.description = travel_description_lang[str(language_id)]
            except:
                pass
        travel.location = LanguageH.get_location_data_by_language(language_id, travel.location)
        travel.group = LanguageH.get_group_data_by_language(language_id, travel.group)
        return travel

    def get_location_data_by_language(language_id, location):
        if location.name_lang != '' and location.name_lang != None:
            try:
                location_name_lang = json.loads(location.name_lang, strict=False)
                if location_name_lang[str(language_id)]:
                    location.name = location_name_lang[str(language_id)]
            except:
                pass
        if location.description_lang != '' and location.description_lang != None:
            try:
                location_description_lang = json.loads(location.description_lang, strict=False)
                if location_description_lang[str(language_id)]:
                    location.description = location_description_lang[str(language_id)]
            except:
                pass
        if location.address_lang != '' and location.address_lang != None:
            try:
                location_address_lang = json.loads(location.address_lang, strict=False)
                if location_address_lang[str(language_id)]:
                    location.address = location_address_lang[str(language_id)]
            except:
                pass
        if location.contact_name_lang != '' and location.contact_name_lang != None:
            try:
                location_contact_name_lang = json.loads(location.contact_name_lang, strict=False)
                if location_contact_name_lang[str(language_id)]:
                    location.contact_name = location_contact_name_lang[str(language_id)]
            except:
                pass
        return location

    def get_option_data_by_language(language_id, option):
        if option.option_lang != '' and option.option_lang != None:
            try:
                option_lang = json.loads(option.option_lang, strict=False)
                # print(option_lang)
                if option_lang[str(language_id)]:
                    option.option = option_lang[str(language_id)]
            except:
                pass
        return option

    def get_hotel_data_by_language(language_id, hotel):
        if hotel.name_lang != '' and hotel.name_lang != None:
            try:
                hotel_name_lang = json.loads(hotel.name_lang, strict=False)
                if hotel_name_lang[str(language_id)]:
                    hotel.name = hotel_name_lang[str(language_id)]
            except:
                pass
        hotel.group = LanguageH.get_group_data_by_language(language_id, hotel.group)
        hotel.location = LanguageH.get_location_data_by_language(language_id, hotel.location)
        return hotel

    def get_room_data_by_language(language_id, room):
        if room.description_lang != '' and room.description_lang != None:
            try:
                room_description_lang = json.loads(room.description_lang, strict=False)
                if room_description_lang[str(language_id)]:
                    room.description = room_description_lang[str(language_id)]
            except:
                pass
        room.hotel = LanguageH.get_hotel_data_by_language(language_id, room.hotel)
        return room

    def get_group_data_by_language(language_id, group):
        if group.name_lang != '' and group.name_lang != None:
            try:
                group_name_lang = json.loads(group.name_lang, strict=False)
                if group_name_lang[str(language_id)]:
                    group.name = group_name_lang[str(language_id)]
            except:
                pass
        return group

    def get_preset_list(event_id, event_user_type):
        if event_user_type == 'super_admin':
            presets = Presets.objects.filter(Q(event_id=event_id) | Q(event_id=None))
        else:
            presets = Presets.objects.filter(event_id=event_id)
        presetsEvent = PresetEvent.objects.filter(event_id=event_id)
        if presetsEvent.exists():
            presetsEvent = presetsEvent[0]
        else:
            presetsEvent = None
        return [presets, presetsEvent]

    def get_current_and_all_presets(request):
        [presets, presetsEvent] = LanguageH.get_preset_list(request.session['event_auth_user']['event_id'],
                                                            request.session['event_auth_user']['type'])
        context = {
            'all_presets': presets,
            'presetsEvent': presetsEvent
        }
        return context

    # Return object
    def catch_lang_key_obj(event_id, language_id, element_name):
        try:
            element = Elements.objects.filter(slug=element_name)
            lang = LanguageH.get_lang_key(event_id, language_id, element[0].id)
            return lang
        except Exception as e:
            ErrorR.efail(e)

    def get_current_language_id(event_id):
        current_language = PresetEvent.objects.filter(event_id=event_id).first()
        return str(current_language.preset_id)

    def insert_lang(language_id,form_data,lang_key,lang_value):
        lang_data = {language_id: lang_value}
        form_data[lang_key] = str(lang_data).replace("'", '"')
        return form_data

    def update_lang(language_id,form_data,lang_key,lang_value,json_lang):
        if json_lang != '' and json_lang != None:
            new_lang = json.loads(json_lang, strict=False)
            new_lang[str(language_id)] = lang_value
            form_data[lang_key] = str(new_lang).replace("'", '"')
        else:
            lang_data = {language_id: lang_value}
            form_data[lang_key] = str(lang_data).replace("'", '"')
        return form_data

    def catch_lang_key_multiple(language_id, element_name, lang_keys):
        response = {}
        try:
            element = Elements.objects.get(slug=element_name)
            # elementObj = Elements.objects.filter(id=element.id)
            # if elementObj.exists():
            lang_data = ElementPresetLang.objects.filter(preset_id=language_id,
                                                         element_default_lang__element_id=element.id,
                                                         element_default_lang__lang_key__in=lang_keys).select_related('element_default_lang')
            lang_key = {}
            for lang in lang_data:
                lang_key[lang.element_default_lang.lang_key] = lang.value
            response['langkey'] = lang_key
            return response
        except Exception as e:
            ErrorR.efail(e)

    def get_email_subject_by_language(language_id,email):
        subject_lang = email.subject
        if email.subject_lang != '' and email.subject_lang != None:
            try:
                email_subject_lang = json.loads(email.subject_lang, strict=False)
                if email_subject_lang[str(language_id)]:
                    subject_lang = email_subject_lang[str(language_id)]
            except:
                pass
        return subject_lang



