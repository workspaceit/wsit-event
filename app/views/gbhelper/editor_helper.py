from django.views import generic
from app.models import Questions, Setting, StyleSheet, Presets, CustomClasses, PresetEvent
from app.views.common_views import GroupView
import json
from django.conf import settings


class EditorHelper(generic.DetailView):

    def get_editor_context(request, min_height=200, max_height=600 ,styles=True,fullpage=False,language_id=None,iframe_style='', toolbar_inline=0):
        context = {}
        question_group_list = []
        event_id = request.session['event_auth_user']['event_id']
        questionGroup = GroupView.get_questionGroup(request)
        for group in questionGroup:
            question_list = {}
            group.questions = Questions.objects.filter(group_id=group.id).order_by('question_order')
            for question in group.questions:
                # title = question.title.replace('"',"").replace("'","")
                title = question.title.replace('"',"&quot;").replace("'","&apos;")
                question_list[str(question.id)] = title + " (" + str(question.id) +")"
            question_group_list.append({group.name: question_list})
        context['editor_question_group_list'] = question_group_list
        default_date_format = 'm-d-Y'
        default_time_format = 'H:i'
        default_date_time_format = default_date_format + ' ' + default_time_format
        try:
            if language_id:
                date_time_language_format = Presets.objects.get(id=language_id)
                default_date_format = date_time_language_format.date_format
                default_time_format = date_time_language_format.time_format
                default_date_time_format = date_time_language_format.datetime_format
            else:
                setting_default_date_format = Setting.objects.filter(name='default_date_format', event_id=event_id)
                if setting_default_date_format:
                    default_date_format_all = json.loads(setting_default_date_format[0].value)
                    default_date_format = default_date_format_all['python']
                    default_date_time_format = default_date_format + ' ' + default_time_format
        except Exception as e:
            print(e)
            pass
        context['editor_default_date_format'] = default_date_format
        context['editor_default_time_format'] = default_time_format
        context['editor_default_date_time_format'] = default_date_time_format
        if styles:
            css_version_obj = StyleSheet.objects.get(event_id=event_id)
            css_version = css_version_obj.version
            event_stylesheet = str(settings.STATIC_URL_ALT)+"public/"+request.session['event_auth_user']['event_url']+"/compiled_css/main_style.css?v=" + str(css_version)
            context['editor_event_stylesheet'] = event_stylesheet
        editor_fullpage = 'false'
        if fullpage:
            editor_fullpage = 'true'
        # custom_classes = CustomClasses.objects.values('classname').filter(event_id=event_id)
        # class_data = {}
        # for custom_class in custom_classes:
        #     class_key = custom_class['classname'].replace('-',' ').replace('_',' ')
        #     class_data[custom_class['classname']] = class_key
        link_styles = {
            'button': 'Button'
        }
        font_familys = {
            'sans-serif': 'Sans-serif',
            'serif': 'Serif'
        }
        context['editor_link_styles'] = link_styles
        context['editor_font_familys'] = font_familys
        context['editor_fullpage'] = editor_fullpage
        context['editor_min_height'] = min_height
        context['editor_max_height'] = max_height
        iframe_style = 'html{margin: 0px;height: 200px;}body{height:200px;}'+iframe_style
        context['editor_iframe_style'] = iframe_style
        context['editor_toolbar_inline'] = toolbar_inline
        return context
