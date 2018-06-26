import json

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView
from app.models import Elements, Presets, ElementDefaultLang, ElementPresetLang, PresetEvent


class LanguageDefaultView(TemplateView):
    def get(self, request):
        event_id = request.session['event_auth_user']['event_id']
        presets = Presets.objects.all()
        presetsEvent = PresetEvent.objects.filter(event_id=event_id)
        if presetsEvent.exists():
            presetsEvent = presetsEvent[0]
        else:
            presetsEvent = None
        elements = Elements.objects.all()

        for element in elements:
            element.name = element.name.replace(" ", "-")
            element.lang = ElementDefaultLang.objects.filter(element_id=element.id)

        context = {
            "elements": elements,
            "presets": presets,
            "presetsEvent": presetsEvent,
            "event_id": event_id
        }

        return render(request, 'language_default/index.html', context)

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
                if (ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                     preset_id=presetId,
                                                     element_default_lang__type='notification').exists()):
                    element.hasNotification = True
                if (ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                     preset_id=presetId,
                                                     element_default_lang__type='text').exists()):
                    element.hasText = True
                if (
                        ElementPresetLang.objects.filter(element_default_lang__element_id=element.id,
                                                         preset_id=presetId,
                                                         element_default_lang__type='button').exists()):
                    element.hasButton = True

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
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='notification').exists()):
                    element.hasNotification = True
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='text').exists()):
                    element.hasText = True
                if (ElementDefaultLang.objects.filter(element_id=element.id, type='button').exists()):
                    element.hasButton = True

            context = {
                "elements": elements
            }

            return render(request, 'language/default_lang_render.html', context)

    def add_preset(request):
        preset = request.POST.get('preset')
        try:
            objPreset = Presets.objects.get(preset_name=preset)
        except Presets.DoesNotExist:
            objPreset = Presets(preset_name=preset)
            objPreset.save()
            objPresetLang = ElementPresetLang()
            objDefaultLang = ElementDefaultLang.objects.all()
            insert_list = []
            for defaultLang in objDefaultLang:
                insert_list.append(
                    ElementPresetLang(value=defaultLang.default_value, element_default_lang_id=defaultLang.id,
                                      preset_id=objPreset.id))
            ElementPresetLang.objects.bulk_create(insert_list)

        return HttpResponse(objPreset.id)

    def save_preset(request):

        postData = request.POST
        token = set(["csrfmiddlewaretoken"])
        responseData = []
        postData = [data for data in postData if data not in token]
        for data in postData:
            ElementPresetLang.objects.filter(id=int(data)).update(value=request.POST.get(data))
        return HttpResponse("true")

    def delete_preset(request):
        postDataId = request.POST.get('id')
        Presets.objects.filter(id=postDataId).delete()
        return HttpResponse(postDataId)

    def get_lang_key_source(request, element_id):
        response_data = {}
        string = "<table><tbody>"
        elementObj = Elements.objects.filter(id=element_id)
        if elementObj.exists():
            lang_data = ElementDefaultLang.objects.filter(element_id=elementObj[0].id)
            lang_key = {}
            for lang in lang_data:
                lang_key[lang.lang_key] = lang.default_value
                string += "<tr><td>"+lang.default_value+"</td><td>{{language.langkey."+lang.lang_key+"}}</td></tr>"
            response_data['langkey'] = lang_key
            return HttpResponse(string)
        response_data = {
            'error': True,
            'message': 'Something went wrong. Please try again.'
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class DLanguageDetailView(generic.DetailView):
    def get_object(self, pk):
        try:
            return ElementDefaultLang.objects.get(id=pk)
        except ElementDefaultLang.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        def_lang = self.get_object(pk)
        data = {
            'def_lang': def_lang.as_dict()
        }
        return HttpResponse(json.dumps(data), content_type='application/json')

    def save_dlanguage(request):
        response_data = {}
        id = request.POST.get('id')
        name = request.POST.get('name')
        default_value = request.POST.get('default_value')
        lang_key = request.POST.get('lang_key')
        element = request.POST.get('element')
        type = request.POST.get('type')
        if name and default_value and lang_key and element and type:
            dlang = ElementDefaultLang.objects.filter(id=id)
            if dlang.exists():
                ElementDefaultLang.objects.filter(id=int(id)).update(name=name,
                                                                     default_value=default_value,
                                                                     lang_key=lang_key,
                                                                     element_id=element,
                                                                     type=type)
                response_data['add'] = False
                response_data['success'] = 'Language Saved Successfully'
            else:
                new_dlang = ElementDefaultLang(name=name,
                                               default_value=default_value,
                                               lang_key=lang_key,
                                               element_id=element,
                                               type=type
                                               )
                new_dlang.save()
                response_data['id'] = str(new_dlang.id)
                response_data['name'] = str(new_dlang.name)
                response_data['default_value'] = str(new_dlang.default_value)
                response_data['lang_key'] = str(new_dlang.lang_key)
                response_data['element'] = str(new_dlang.element)
                response_data['type'] = str(new_dlang.type)
                response_data['add'] = True
                presets = Presets.objects.all()
                for preset in presets:
                    new_preset = ElementPresetLang(value=default_value, element_default_lang_id=new_dlang.id,
                                                   preset_id=preset.id)
                    new_preset.save()
                response_data['success'] = 'Language Created Successfully'
        else:
            response_data['success'] = 'Language Creataion Failed.Fill all field'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def delete_dlanguage(request):
        response_data = {}
        id = request.POST.get('id')
        dlang = ElementDefaultLang.objects.get(id=id)
        dlang.delete()
        response_data['success'] = 'Option Deleted Successfully'
        return HttpResponse(json.dumps(response_data), content_type="application/json")
