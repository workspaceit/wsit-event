from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
import json
from app.models import Photo, Setting, ActivityHistory, PhotoGroup
from django.db import transaction
from django.conf import settings
from boto.s3.connection import S3Connection, Bucket, Key
import os
import zipfile
import io
import boto
from PIL import Image
from .common_views import EventView


class PhotoReelView(generic.DetailView):

    def download_photo_reel(request):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        event_id = request.session['event_auth_user']['event_id']
        approved_photos = Photo.objects.filter(is_approved=1, attendee__event_id=event_id)
        s = io.BytesIO()
        zf = zipfile.ZipFile(s, "w")
        for photo in approved_photos:
            k = bucket.get_key(photo.photo)
            file = io.BytesIO()
            k.get_contents_to_file(file)
            zip_path = photo.photo.split('/')[-1]
            zf.writestr(zip_path, file.getvalue())
        zf.close()
        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % 'photo-reel.zip'
        return resp

    def photo_admin_requested(request):
        if EventView.check_read_permissions(request, 'photo_reel_permission'):
            photo_groups = PhotoReelView.get_photo_groups(request)
            for group in photo_groups:
                group.photos = Photo.objects.filter(is_approved=0, group_id=group)
            context = {
                "photo_groups": photo_groups,
                'allow_btn': True,
                'deny_btn':True,
                'page' : 'request',
                'title':'New photos',
                'icon':'fa fa-picture-o',
                'img_src_origin' : settings.STATIC_URL_ALT
            }
            return render(request, 'photo-reel/photo_reel.html', context)

    def photo_admin_allowed(request):
        if EventView.check_read_permissions(request, 'photo_reel_permission'):
            photo_groups = PhotoReelView.get_photo_groups(request)
            for group in photo_groups:
                group.photos = Photo.objects.filter(is_approved=1, group_id=group)
            context = {
                "photo_groups": photo_groups,
                'deny_btn': True,
                'page' : 'allow',
                'title':'Visible photos',
                 'icon':'fa fa-eye',
                'img_src_origin' : settings.STATIC_URL_ALT
            }
            return render(request, 'photo-reel/photo_reel.html', context)

    def photo_admin_denied(request):
        if EventView.check_read_permissions(request, 'photo_reel_permission'):
            photo_groups = PhotoReelView.get_photo_groups(request)
            for group in photo_groups:
                group.photos = Photo.objects.filter(is_approved=2, group_id=group)
            context = {
                "photo_groups": photo_groups,
                'allow_btn': True,
                'page' : 'deny',
                'title':'Denied photos',
                'icon':'fa fa-eye-slash',
                'img_src_origin' : settings.STATIC_URL_ALT
            }
            return render(request, 'photo-reel/photo_reel.html', context)

    def photo_admin_all(request):
        if EventView.check_read_permissions(request, 'photo_reel_permission'):
            photo_groups = PhotoReelView.get_photo_groups(request)
            print(photo_groups)
            for group in photo_groups:
                group.photos = Photo.objects.filter(group_id=group)
                for photo in group.photos:
                    if photo.is_approved==1:
                        photo.deny_btn=True
                    elif photo.is_approved==2:
                        photo.allow_btn=True
                    else:
                        photo.allow_btn=True
                        photo.deny_btn=True

            context = {
                "photo_groups": photo_groups,
                'page' : 'all',
                'title':'All photos',
                'icon':'fa fa-picture-o',
                'img_src_origin' : settings.STATIC_URL_ALT
            }
            return render(request, 'photo-reel/photo_reel.html', context)

    def change_photo_status(request):
        if request.is_ajax():
            try:
                id = request.POST.get('id')
                Photo.objects.filter(pk=id).update(is_approved=request.POST.get('changestatus'))
                photo = Photo.objects.get(id=id)
                event_id = request.session['event_auth_user']['event_id']
                admin_id = request.session['event_auth_user']['id']
                activity = ActivityHistory(attendee_id=photo.attendee_id,admin_id=admin_id, activity_type="update", category="photo", photo_id=photo.id, event_id=event_id)
                activity.save()
                message={'success':'Successfully Updated'}
            except Exception as w:
                message ={'error':'Failed to updated!!!'+str(w)}

        else:
            message = {'error':'Permission Denied!!!'}
        return HttpResponse(json.dumps(message), content_type="application/json")


    def delete_photo(request):
        if request.is_ajax():
            try:

                # print(os.path('/publicfront'+photo[0].photo))
                # import os
                # myfile= photo[0].photo
                # if os.path.isfile(myfile):
                #     os.remove(myfile)
                # else:
                #     print("asd")
                # os.unlink(os.path('/publicfront'+photo[0].photo))
                # os.unlink(os.path('/publicfront'+photo[0].thumb_image))
                with transaction.atomic():
                    photo=Photo.objects.get(pk=request.POST.get('id'))
                    photoName=photo.photo
                    thumbName=photo.thumb_image
                    Photo.objects.get(pk=request.POST.get('id')).delete()
                    conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
                    b = Bucket(conn, settings.AWS_STORAGE_BUCKET_NAME)
                    k = Key(b)
                    k.key = photoName
                    b.delete_key(k)
                    k.key = thumbName
                    b.delete_key(k)

                    message={'success':'Successfully Deleted'}
            except Exception as w:
                message ={'error':'Failed to updated!!!'+str(w)}

        else:
            message = {'error':'Permission Denied!!!'}
        return HttpResponse(json.dumps(message), content_type="application/json")

    def get_photo_groups(request):
        event_id = request.session['event_auth_user']['event_id']
        photo_groups = PhotoGroup.objects.filter(page__event_id=event_id)
        return photo_groups



class PhotoSliderDuration(generic.DetailView):
    def get(self, request):
        event_id = request.session['event_auth_user']['event_id']
        duration = Setting.objects.filter(name='photo_slider_duration', event_id=event_id)
        context = {
            'duration': duration
        }
        return render(request, 'photo-reel/photo_slider_duration.html', context)

    def post(self,request):
        response_data = {}
        duration = request.POST.get('duration')
        event_id = request.session['event_auth_user']['event_id']
        slider_duration = Setting.objects.filter(name='photo_slider_duration', event_id=event_id)
        if slider_duration.exists():
            Setting.objects.filter(name='photo_slider_duration', event_id=event_id).update(value=duration)
        else:
            new_slider_duration = Setting(name='photo_slider_duration', value=duration, event_id=event_id)
            new_slider_duration.save()

        response_data['success'] = "Photo Slider Duration Updated Successfully"
        return HttpResponse(json.dumps(response_data), content_type="application/json")