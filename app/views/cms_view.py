from django.views import generic

from app.views.language_view import LanguageView
from app.views.gbhelper.error_report_helper import ErrorR
import re
from app.models import ElementHtml


class CmsPageView(generic.DetailView):

    def replace_section(request,pageContent,page_id,add_page=False,duid=''):
        try:
            sections = re.findall("section:,box:\d+|section:[^,(?! )]+,box:\d+", pageContent)
            for section in sections:
                try:
                    section_data = section.split(",")
                    classes = section_data[0]
                    box = section_data[1]
                    temp_class = classes.split(":")[1]
                    box_id = box.split(":")[1]
                    if add_page:
                        content_id = "page-"+str(page_id)+"-box-"+box_id+duid
                    else:
                        content_id = "box-"+box_id
                    section_html = """<div class="section section-box """+temp_class+""" box" id=""" + content_id + """>"""
                    pageContent = pageContent.replace('{' + section + '}', section_html)
                except Exception as e:
                    ErrorR.efail(e)
                    section_html = """<div class="section section-box box">"""
                    pageContent = pageContent.replace('{' + section + '}', section_html)
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent

    def replace_row(request,pageContent,page_id,add_page=False,duid=''):
        try:
            rows = re.findall("row:,box:\d+", pageContent)
            for row in rows:
                try:
                    row_data = row.split(",")
                    box = row_data[1]
                    box_id = box.split(":")[1]
                    if add_page:
                        content_id = "page-"+str(page_id)+"-box-"+box_id+duid
                    else:
                        content_id = "box-"+box_id
                    row_html = """<div class="row box" id=""" + content_id + """>"""
                    pageContent = pageContent.replace('{' + row + '}', row_html)
                except Exception as e:
                    ErrorR.efail(e)
                    row_html = """<div class="row box">"""
                    pageContent = pageContent.replace('{' + row + '}', row_html)
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent

    def replace_col(request,pageContent,page_id,add_page=False,duid=''):
        try:
            cols = re.findall("col:[^,(?! )]+,box:\d+", pageContent)
            for col in cols:
                try:
                    col_data = col.split(",")
                    classes = col_data[0]
                    box = col_data[1]
                    span_class = classes.split(":")[1]
                    box_id = box.split(":")[1]
                    if add_page:
                        content_id = "page-"+str(page_id)+"-box-"+box_id+duid
                    else:
                        content_id = "box-"+box_id
                    col_html = """<div class="col box """+span_class+"""" id=""" + content_id + """>"""
                    pageContent = pageContent.replace('{' + col + '}', col_html)
                except Exception as e:
                    ErrorR.efail(e)
                    col_html = """<div class="col box">"""
                    pageContent = pageContent.replace('{' + col + '}', col_html)
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent

    def replace_editor_html(request,pageContent,page_id,language,add_page=False,duid=''):
        try:
            editor_htmls = re.findall("editor:html,box:\d+", pageContent)
            for html in editor_htmls:
                try:
                    html_data = html.split(",")
                    box = html_data[1]
                    box_id = box.split(":")[1]
                    if language == None:
                        editor_data = ElementHtml.objects.filter(page_id=page_id,box_id=box_id,language_id=6)
                    else:
                        editor_data = ElementHtml.objects.filter(page_id=page_id,box_id=box_id,language_id=language)
                        if not editor_data.exists():
                            if add_page:
                                current_language = LanguageView.get_current_public_preset(request)
                            else:
                                current_language = LanguageView.get_current_preset(request)
                            if current_language != None:
                                editor_data = ElementHtml.objects.filter(page_id=page_id, box_id=box_id,language_id=current_language.preset_id)
                            else:
                                editor_data = ElementHtml.objects.filter(page_id=page_id,box_id=box_id,language_id=6)
                    if editor_data.exists():
                        compiled_data = editor_data[0].compiled
                    else:
                        compiled_data = ""
                    if add_page:
                        content_id = "page-"+str(page_id)+"-box-"+box_id+duid
                    else:
                        content_id = "box-"+box_id
                    editor_html = """<div class="element box form-editor" id=""" + content_id + """>"""+compiled_data+"""</div>"""
                    pageContent = pageContent.replace('{' + html + '}', editor_html)
                except Exception as e:
                    ErrorR.efail(e)
                    pageContent = pageContent.replace('{' + html + '}', "")
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent

    def replace_enddiv(request,pageContent):
        try:
            end_divs = re.findall("end_div", pageContent)
            for end_div in end_divs:
                end_div_html = """</div>"""
                pageContent = pageContent.replace('{' + end_div + '}', end_div_html)
            return pageContent
        except Exception as e:
            ErrorR.efail(e)
            return pageContent
