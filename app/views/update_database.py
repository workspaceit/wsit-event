import json

from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.template.loader import render_to_string

from app.models import Elements, ElementDefaultLang, ElementsQuestions, Presets, ElementPresetLang
from app.views.gbhelper.error_report_helper import ErrorR
import logging


class UpdateDatabaseView(generic.TemplateView):
    def get(self, request):
        return render(request, 'update_database/index.html', UpdateDatabaseView().getContent())

    def update_database(request):
        response_data = []
        logger = logging.getLogger(__name__)
        try:
            logger.debug("============Update Database Start Details===============")
            if request.POST.get('confirm') == "CONFIRM":
                c = connection.cursor()
                try:
                    element_sql = render_to_string('update_database/elements.sql')
                    c.execute(element_sql.strip(' \n\r\t'))
                    element_sql = render_to_string('update_database/element_default_lang.sql')
                    c.execute(element_sql.strip(' \n\r\t'))
                    element_sql = render_to_string('update_database/elements_questions.sql')
                    c.execute(element_sql.strip(' \n\r\t'))
                finally:
                    c.close()

                try:
                    logger.debug("=============New Preset Language Add START==============")
                    presets = Presets.objects.all()
                    for preset in presets:
                        preset_lang_ids = ElementPresetLang.objects.filter(preset=preset.id).values_list('element_default_lang_id',
                                                                                                         flat=True)
                        logger.debug(preset_lang_ids)
                        new_preset_langs = ElementDefaultLang.objects.all().exclude(id__in=preset_lang_ids)
                        if(len(new_preset_langs)):
                            for new_preset_lang in new_preset_langs:
                                new_lang = ElementPresetLang(value=new_preset_lang.default_value,
                                                         element_default_lang_id=new_preset_lang.id,
                                                         preset_id=preset.id)
                                new_lang.save()
                    logger.debug("=============New Preset Language Add END==============")
                except Exception as e:
                    ErrorR.efail(e)
                    # Elements.objects.raw('"'+render_to_string('update_database/elements.html')+'"')

            response_data = {'message': 'Database updated Successfully','content':UpdateDatabaseView().getContent()}
            logger.debug("=============Update Database Start END==============")
        except Exception as e:
            logger.debug("============Update Database Start ERROR Details===============")
            ErrorR.efail(e)
            logger.debug("=============Update Database Start ERROR END==============")
            response_data = {
                'error': True,
                'message': 'Something went wrong with update database. Please try again.'
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def clean_database(request):
        response_data = []
        logger = logging.getLogger(__name__)
        try:
            logger.debug("============Clean Database Start Details===============")
            if request.POST.get('confirm') == "CONFIRM":
                import re
                regex = r"\(\d*,"

                # Elements
                element_sql = render_to_string('update_database/elements.sql')
                matches = re.finditer(regex, element_sql)
                element_sql_row = []
                for match in matches:
                    temp_str = match.group()
                    element_sql_row.append(int(temp_str.replace("(", "").replace(",", "")))
                logger.debug(element_sql_row)
                Elements.objects.exclude(id__in=element_sql_row).delete()

                # Element Default Language
                element_sql = render_to_string('update_database/element_default_lang.sql')
                matches = re.finditer(regex, element_sql)
                element_default_lang_sql_row = []
                for match in matches:
                    temp_str = match.group()
                    element_default_lang_sql_row.append(int(temp_str.replace("(", "").replace(",", "")))
                ElementDefaultLang.objects.exclude(id__in=element_default_lang_sql_row).delete()

                # Elements Question
                element_sql = render_to_string('update_database/elements_questions.sql')
                matches = re.finditer(regex, element_sql)
                elements_questions_sql_row = []
                for match in matches:
                    temp_str = match.group()
                    elements_questions_sql_row.append(int(temp_str.replace("(", "").replace(",", "")))
                ElementsQuestions.objects.exclude(id__in=elements_questions_sql_row).delete()
            response_data = {'message': 'Database cleaned Successfully','content':UpdateDatabaseView().getContent()}
            logger.debug("=============Clean Database Start END==============")
        except Exception as e:
            logger.debug("============Clean Database Start ERROR Details===============")
            ErrorR.efail(e)
            logger.debug("=============Clean Database Start ERROR END==============")
            response_data = {
                'error': True,
                'message': 'Something went wrong with clean database. Please try again.'
            }
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    def getContent(self):
        import re
        regex = r"\(\d*,"
        logger = logging.getLogger(__name__)
        # Elements
        element_sql = render_to_string('update_database/elements.sql')
        matches = re.finditer(regex, element_sql)
        element_sql_row = 0
        for match in matches:
            element_sql_row += 1
        element_row = Elements.objects.count()

        # Element Default Language
        element_sql = render_to_string('update_database/element_default_lang.sql')
        matches = re.finditer(regex, element_sql)
        element_default_lang_sql_row = 0
        for match in matches:
            element_default_lang_sql_row += 1
        element_default_lang_row = ElementDefaultLang.objects.count()

        # Elements Question
        element_sql = render_to_string('update_database/elements_questions.sql')
        matches = re.finditer(regex, element_sql)
        elements_questions_sql_row = 0
        for match in matches:
            elements_questions_sql_row += 1
        elements_questions_row = ElementsQuestions.objects.count()

        logger.debug("===========REG=============")
        logger.debug(element_sql_row)
        content = {
            'element_row': element_row,
            'element_sql_row': element_sql_row,
            'element_default_lang_row': element_default_lang_row,
            'element_default_lang_sql_row': element_default_lang_sql_row,
            'elements_questions_row': elements_questions_row,
            'elements_questions_sql_row': elements_questions_sql_row,
        }
        return content