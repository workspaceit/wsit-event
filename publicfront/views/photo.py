from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from app.models import Photo, Setting, ElementsAnswers, ActivityHistory
import json
import boto
from boto.s3.key import Key
from django.conf import settings
import time
from PIL import Image, ExifTags
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import io
from django.contrib import messages
from django.conf import settings
from boto3.session import Session as boto_session
from app.views.gbhelper.error_report_helper import ErrorR
from publicfront.views.lang_key import LanguageKey


class PhotoReel(TemplateView):

    def get(self, request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            if request.session['event_user']['attending'] == "Yes":
                event_id = request.session['event_user']['event_id']
                all_photos = Photo.objects.filter(is_approved=1, attendee__event_id=event_id).order_by('-uploaded_at')
                context = {
                    'photos': all_photos
                }
                return render(request, 'public/photo/photo-reel.html', context)
            else:
                return redirect('welcome', event_url=request.session['event_url'])
        else:
            return redirect('welcome', event_url=request.session['event_url'])

    def upload_files_request(request,*args, **kwargs):
        event_id = request.session['event_id']
        language = LanguageKey.catch_lang_key_obj(request, "photo-upload")
        if 'is_user_login' in request.session and request.session['is_user_login']:
            try:
                image_file =request.FILES.get('pic')
                page_id =request.POST.get('page_id')
                box_id =request.POST.get('box_id')
                group_id =request.POST.get('photo_group_id')
                attendee_id = request.session['event_user']['id']
                uploaded_image = io.BytesIO(image_file.read())
                upload_file = PhotoReel.upload_image(request,uploaded_image, attendee_id, page_id, box_id, language['langkey'])
                if upload_file['success']:
                    if upload_file['photo_overwrite'] == "True":
                        Photo.objects.filter(group_id=group_id, attendee_id=attendee_id).delete()
                        # existing_photos = Photo.objects.filter(group_id=group_id, attendee_id=attendee_id)
                        # for photo in existing_photos:
                        #     bucket.delete_key(key)
                    photo_form = {
                        'photo': upload_file['file_name'],
                        'thumb_image': upload_file['file_thumb'],
                        'attendee_id': attendee_id,
                        'group_id': group_id
                    }
                    if 'comment' in request.POST:
                        photo_form['comment'] = request.POST.get('comment')
                    if upload_file['auto_publish'] == "True":
                        photo_form['is_approved'] = 1
                    photo = Photo(**photo_form)
                    photo.save()
                    activity = ActivityHistory(attendee_id=attendee_id, activity_type="update", category="photo", photo_id=photo.id, event_id=event_id)
                    activity.save()
                context = {
                    'status': 200,
                    'success':upload_file['success'],
                    'message': upload_file['message']
                }
                return HttpResponse(json.dumps(context), content_type="application/json")

            except Exception as e:
                ErrorR.efail(e)
                context = {
                    'status': 304,
                    'success': False,
                    'message': language['langkey']['photo_upload_notification_error_general']
                }
                return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            context = {
                'status': 304,
                'success': False,
                'message': language['langkey']['photo_upload_notification_error_general']
            }
            return HttpResponse(json.dumps(context), content_type="application/json")

    def upload_image(request, uploaded_image, attendee_id, page_id, box_id,language):
        response = {}
        try:
            photo_settings = ElementsAnswers.objects.filter(page_id=page_id, box_id=box_id)
            max_height = ''
            max_width = ''
            min_height = ''
            min_width = ''
            thumbnail_height = '256'
            thumbnail_width = '256'
            rescal_height = ''
            rescal_width = ''
            auto_publish = 'False'
            photo_overwrite = 'False'
            for setting in photo_settings:
                if setting.element_question.question_key == 'photo_upload_max_height':
                        max_height = setting.answer
                if setting.element_question.question_key == 'photo_upload_max_width':
                        max_width = setting.answer
                if setting.element_question.question_key == 'photo_upload_min_height':
                        min_height = setting.answer
                if setting.element_question.question_key == 'photo_upload_min_width':
                        min_width = setting.answer
                if setting.element_question.question_key == 'photo_upload_thumbnail_height':
                        thumbnail_height = setting.answer
                if setting.element_question.question_key == 'photo_upload_thumbnail_width':
                        thumbnail_width = setting.answer
                if setting.element_question.question_key == 'photo_upload_rescal_height':
                        rescal_height = setting.answer
                if setting.element_question.question_key == 'photo_upload_rescal_width':
                        rescal_width = setting.answer
                if setting.element_question.question_key == 'photo_upload_auto_publish':
                        auto_publish = setting.answer
                if setting.element_question.question_key == 'photo_upload_overwrite':
                        photo_overwrite = setting.answer
            max_height = int(max_height) if max_height != '' else int(0)
            max_width = int(max_width) if max_width != '' else int(0)
            min_height = int(min_height) if min_height != '' else int(0)
            min_width = int(min_width) if min_width != '' else int(0)
            thumbnail_height = int(thumbnail_height) if thumbnail_height != '' else int('256')
            thumbnail_width = int(thumbnail_width) if thumbnail_width != '' else int('256')
            rescal_height = int(rescal_height) if rescal_height != '' else int(0)
            rescal_width = int(rescal_width) if rescal_width != '' else int(0)

            image = Image.open(uploaded_image)
            uploaded_image_height = image.height
            uploaded_image_width = image.width
            if (max_height != 0 and uploaded_image_height > max_height) or (max_width != 0 and uploaded_image_width > max_width):
                response['success'] = False
                response['message'] = language['photo_upload_notification_error_large']
                return response
            if (min_height != 0 and uploaded_image_height < min_height) or (min_width != 0 and uploaded_image_width < min_width):
                response['success'] = False
                response['message'] = language['photo_upload_notification_error_small']
                return response
            size = uploaded_image_width, uploaded_image_height
            old_image = image
            ErrorR.okblue("height "+str(rescal_height))
            ErrorR.okblue("width "+str(rescal_width))
            ErrorR.okblue("img height " + str(uploaded_image_height))
            ErrorR.okblue("img width " + str(uploaded_image_width))
            ErrorR.ilog("img height " + str(uploaded_image_height))
            ErrorR.ilog("img width " + str(uploaded_image_width))
            try:
                for orientation in ExifTags.TAGS.keys():
                    if ExifTags.TAGS[orientation] == 'Orientation':
                        break
                exif = dict(image._getexif().items())
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
                ErrorR.ilog("rescal img height " + str(uploaded_image_height))
                ErrorR.ilog("rescal img width " + str(uploaded_image_width))
                if (rescal_height != 0 and image.height > rescal_height) or (rescal_width != 0 and image.width > rescal_width):
                    response['success'] = False
                    response['message'] = language['photo_upload_notification_error_large']
                    return response
                else:
                    size = image.width, image.height
            except (AttributeError, KeyError, IndexError):
                pass
            image = image.resize((size))
            image.thumbnail(size)
            output_image = io.BytesIO()
            image.save(output_image, old_image.format)
            filename = str(int(time.time())) + str(attendee_id) + '.' + old_image.format
            filename_with_path = 'public/' + request.session['event_url'] + '/photo-reel/' + filename
            save_to_s3 = PhotoReel.upload_image_to_s3(request, filename_with_path, output_image, old_image, language)

            thumbnail_size = thumbnail_width, thumbnail_height
            img = image.resize((thumbnail_width, thumbnail_height))
            img.thumbnail(thumbnail_size)
            output_image = io.BytesIO()
            img.save(output_image, old_image.format)
            thumbnail_filename = str(int(time.time())) + str(attendee_id) + '_thumb.' + old_image.format
            thumbnail_filename_with_path = 'public/' + request.session['event_url'] + '/photo-reel/' + thumbnail_filename
            PhotoReel.upload_image_to_s3(request, thumbnail_filename_with_path, output_image, old_image, language)
            response['success'] = save_to_s3['success']
            response['message'] = save_to_s3['message']
            response['file_name'] = filename_with_path
            response['file_thumb'] = thumbnail_filename_with_path
            response['auto_publish'] = auto_publish
            response['photo_overwrite'] = photo_overwrite
            return response
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
            response['message'] = language['photo_upload_notification_error_general']
            return response

    def upload_image_to_s3(request, filename_with_path, output_image, image, language):
        response = {}
        try:
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            key_name = filename_with_path
            k = Key(bucket)
            k.key = key_name
            if not k.exists():
                key = bucket.new_key(key_name)
                key.set_metadata('Content-Type', 'image/' + image.format)
                key.set_contents_from_string(output_image.getvalue())
                key.set_acl('public-read')
                key.make_public()
            else:
                k.set_metadata('Content-Type', 'image/' + image.format)
                k.set_contents_from_string(output_image.getvalue())
                k.set_acl('public-read')
                k.make_public()
            response['success'] = True
            response['message'] = language['photo_upload_notification_success']
            return response
        except Exception as e:
            ErrorR.efail(e)
            response['success'] = False
            response['message'] = language['photo_upload_notification_error_general']
            return response

from django_datatables_view.base_datatable_view import BaseDatatableView

class PhotoListJson(BaseDatatableView):
    # The model we're going to show
    model = Photo
    columns = ['photo','thumb_image']
    order_columns = ['photo']
    max_display_length = 50

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(attendee__event_id=self.get_event_id(),is_approved=1)

    def get_event_id(self):
        return self.request.session['event_user']['event_id']


    def prepare_results(self, qs):

        session = boto_session(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
          region_name='eu-west-1')
        s3_client = session.client('s3')
        json_data = []
        for q in qs:
            print(q.photo)
            main_photo_key = q.photo
            thumb_photo_key = q.thumb_image
            main_photo = '{}/{}/{}'.format(s3_client.meta.endpoint_url, settings.AWS_STORAGE_BUCKET_NAME, main_photo_key)
            thumb_photo = '{}/{}/{}'.format(s3_client.meta.endpoint_url, settings.AWS_STORAGE_BUCKET_NAME, thumb_photo_key)
            #url = "<a class='fancybox-thumbs' data-fancybox-group='thumb' href='"+main_photo+"'><img src='"+thumb_photo+"' /></a>"
            json_data.append([{
                'photo': main_photo,
                'thumb': thumb_photo
            }])
        return json_data