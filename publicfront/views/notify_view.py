from django.http import HttpResponse
from django.views.generic import TemplateView

from app.models import PresetEvent, ElementPresetLang, ElementDefaultLang


class NotifyView(TemplateView):
    def get(self,request, *args, **kwargs):

        msg =NotifyView.get_notification_text(request, "notify_session_full")
        return HttpResponse(msg)

    def get_notification_text(request, lang_key):
        event_id = request.session['event_id']
        language_id = request.session['language_id']
        # presetsEvents = PresetEvent.objects.filter(event_id=event_id)
        # if presetsEvents.exists():
        #     presetsEvent = presetsEvents[0]
        presetLang = ElementPresetLang.objects.filter(preset_id=language_id,
                                                      element_default_lang__lang_key=lang_key)
        if presetLang.exists():
            return presetLang[0].value

        defaultLang = ElementDefaultLang.objects.filter(lang_key=lang_key)
        if defaultLang.exists():
            return defaultLang[0].default_value
        else:
            return ""
