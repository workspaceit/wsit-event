from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from app.models import Scan, Attendee, DeviceToken
import json
import re
from datetime import datetime
import boto
from boto.s3.key import Key
from django.conf import settings

from app.views.common_views import EventView


class FileView(TemplateView):
    def buildTree(list, parent_id='root'):
        branch = []
        for li in list:
            if li['parent_id'] == parent_id:
                items = FileView.buildTree(list, li['text'])
                if items:
                    li['items'] = items
                branch.append(li)
        return branch

    def newfolder(request):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        key = request.POST.get('key') + request.POST.get('name') + '/'
        key = key.replace('//', '/')
        k = bucket.new_key(key)
        k.set_contents_from_string('', policy='public-read')
        res = {
            'result': True,
            'folderName':request.POST.get('name'),
            'key':key,
            'message': 'New folder created successfully'
        }
        return HttpResponse(json.dumps(res), content_type="application/json")

    def deletefolder(request):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        event_url = request.session['event_auth_user']['event_url']
        checker = "public/" + event_url + "/files/offline_package"

        delete_files = json.loads(request.POST.get("delete_files"))
        for file in delete_files:
            key = file['key'].replace('//', '/')
            if checker in key:
                FileView.update_offline_status(request)
            type = file['type']
            if type == 'folder':
                for key in bucket.list(prefix=key):
                    key.delete()
            else:
                k = bucket.delete_key(key)

        # print(key)
        res = {
            'result': True,
            'message': 'Deleted successfully'
        }
        return HttpResponse(json.dumps(res), content_type="application/json")

    def getlink(request):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        key = request.POST.get('key').replace('//', '/')
        key_detail = bucket.get_key(key)
        key_url = key_detail.generate_url(0, query_auth=False)
        # print(key_url)
        res = {
            'result': True,
            'key_url':key_url
        }
        return HttpResponse(json.dumps(res), content_type="application/json")

    def rename(request):
        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
        oldKey = request.POST.get('key').replace('//', '/')
        name = request.POST.get('name')
        newKey = ''

        event_url = request.session['event_auth_user']['event_url']
        checker = "public/" + event_url + "/files/offline_package"
        if checker in oldKey:
            FileView.update_offline_status(request)

        arr = oldKey.split('/')
        index = len(arr) - 1

        for num in range(0, len(arr) - 1):
            newKey += arr[num] + '/'

        newKey += name + '/'
        # print (newKey)

        fileList = []

        if request.POST.get('type') == 'folder':
            files = bucket.list(prefix=oldKey)
            for file in files:
                fileList.append(file.name)
                # print(file.name)

            newFileList = []

            for file in fileList:
                newArr = file.split('/')
                newArr[index] = name
                result = ''
                for num in range(0, len(newArr)):
                    result += newArr[num] + '/'
                result = result[:-1]
                newFileList.append(result)

            for num in range(0, len(newFileList)):
                bucket.copy_key(newFileList[num], settings.AWS_STORAGE_BUCKET_NAME, fileList[num])
                newKey_bucket_file = Key(bucket)
                newKey_bucket_file.key = newFileList[num]
                newKey_bucket_file.make_public()
                bucket.delete_key(fileList[num])

        else:
            newKey = newKey[:-1]
            bucket.copy_key(newKey, settings.AWS_STORAGE_BUCKET_NAME, oldKey)
            newKey_bucket_file = Key(bucket)
            newKey_bucket_file.key = newKey
            newKey_bucket_file.make_public()
            bucket.delete_key(oldKey)

        res = {
            'result': True,
            'newKey': newKey,
            'message': 'Rename successfully'
        }
        return HttpResponse(json.dumps(res), content_type="application/json")

    def urlify(s):
        s = re.sub(r"[^\w\s]", '_', s)
        s = re.sub(r"\s+", '_', s)
        return s

    def fileupload(request):

        file = request.FILES['files']
        key = request.POST.get('key').replace('//', '/')

        event_url = request.session['event_auth_user']['event_url']
        checker = "public/" + event_url + "/files/offline_package"
        if checker in key:
            FileView.update_offline_status(request)

        response = {}
        filename = FileView.urlify(file.name.split('.')[0])

        conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

        contentType = file.content_type
        if not key.endswith('/'):
            key_name = key + '/' + file.name
        else:
            key_name = key + file.name

        k = Key(bucket)
        k.key = key_name

        # print(key_name)

        if not k.exists():
            key = bucket.new_key(key_name)
            key.set_metadata('Content-Type', contentType)
            key.set_contents_from_string(file.read())
            key.set_acl('public-read')
            key.make_public()
            response['success'] = True
            response['msg'] = "Successfully Uploaded"
        else:
            key = bucket.new_key(key_name)
            key.set_metadata('Content-Type', contentType)
            key.set_contents_from_string(file.read())
            key.set_acl('public-read')
            key.make_public()
            response['success'] = True
            response['msg'] = "Successfully Uploaded"

        response['key'] = key_name
        response['file_name'] = file.name

        filetypeAarry = file.name.split(".")
        file_type = filetypeAarry[len(filetypeAarry)-1]

        if file_type.lower() == "png" or file_type.lower() == "jpeg" or file_type.lower() == "jpg"  or file_type.lower() == "svg":
            response['spriteCssClass'] = 'image'
        elif file_type.lower() == "css" or file_type.lower() == "html":
            response['spriteCssClass'] = 'html'
        elif file_type.lower() == "pdf":
            response['spriteCssClass'] = 'pdf'
        elif file_type.lower() == "txt":
            response['spriteCssClass'] = 'html'
        else:
            response['spriteCssClass'] = 'html'


        return HttpResponse(json.dumps(response), content_type="application/json")

    def filecut(request):
        response = {}
        if request.POST.get('type') != 'rootfolder':
            sourceKey = request.POST.get('sourceKey').replace('//', '/')
            destKey = request.POST.get('destKey').replace('//', '/')
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

            event_url = request.session['event_auth_user']['event_url']
            checker = "public/" + event_url + "/files/offline_package"
            if checker in sourceKey or checker in destKey:
                FileView.update_offline_status(request)

            # print(sourceKey)
            arrSourceKey = sourceKey.split('/')
            destKey += '/' + arrSourceKey[len(arrSourceKey) - 1]
            # print(destKey)

            fileList = []

            if request.POST.get('type') == 'folder':
                files = bucket.list(prefix=sourceKey)
                for file in files:
                    fileList.append(file.name)

                newFileList = []

                for file in fileList:
                    newArr = file.split('/')
                    result = destKey + '/' + newArr[len(newArr) - 1]
                    # print(result)
                    newFileList.append(result)

                for num in range(0, len(newFileList)):
                    bucket.copy_key(newFileList[num], settings.AWS_STORAGE_BUCKET_NAME, fileList[num])
                    newKey_bucket_file = Key(bucket)
                    newKey_bucket_file.key = newFileList[num]
                    newKey_bucket_file.make_public()
                    bucket.delete_key(fileList[num])

            else:
                bucket.copy_key(destKey, settings.AWS_STORAGE_BUCKET_NAME, sourceKey)
                newKey_bucket_file = Key(bucket)
                newKey_bucket_file.key = destKey
                newKey_bucket_file.make_public()
                bucket.delete_key(sourceKey)

            response['result'] = True
            response['message'] = "Successfully Moved"
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps(response), content_type="application/json")

    def filecopy(request):
        response = {}
        if request.POST.get('type') != 'rootfolder':
            sourceKey = request.POST.get('sourceKey').replace('//', '/')
            destKey = request.POST.get('destKey').replace('//', '/')
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)

            event_url = request.session['event_auth_user']['event_url']
            checker = "public/" + event_url + "/files/offline_package"
            if checker in sourceKey or checker in destKey:
                FileView.update_offline_status(request)

            # print(sourceKey)
            arrSourceKey = sourceKey.split('/')
            destKey += '/' + arrSourceKey[len(arrSourceKey) - 1]
            # print(destKey)

            fileList = []

            if request.POST.get('type') == 'folder':
                files = bucket.list(prefix=sourceKey)
                for file in files:
                    fileList.append(file.name)

                newFileList = []

                for file in fileList:
                    newArr = file.split('/')
                    result = destKey + '/' + newArr[len(newArr) - 1]
                    # print(result)
                    newFileList.append(result)

                for num in range(0, len(newFileList)):
                    bucket.copy_key(newFileList[num], settings.AWS_STORAGE_BUCKET_NAME, fileList[num])
                    newKey_bucket_file = Key(bucket)
                    newKey_bucket_file.key = newFileList[num]
                    newKey_bucket_file.make_public()

            else:
                bucket.copy_key(destKey, settings.AWS_STORAGE_BUCKET_NAME, sourceKey)
                newKey_bucket_file = Key(bucket)
                newKey_bucket_file.key = destKey
                newKey_bucket_file.make_public()

            response['result'] = True
            response['message'] = "Successfully Copied"
            return HttpResponse(json.dumps(response), content_type="application/json")
        else:
            return HttpResponse(json.dumps(response), content_type="application/json")

    def files(request):
        if EventView.check_read_permissions(request, 'file_browser_permission'):
            context = FileView.get_all_files(request)
            return render(request, 'file/file.html', context)

    def get_all_files(request):
        context = {}
        try:
            conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
            bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
            event_url=request.session['event_auth_user']['event_url']
            #
            fileList = []
            # url = "public/"+event_url
            url = "public/" + event_url + "/files"
            files = bucket.list(prefix=url)
            for file in files:
                fileList.append(file.name)

            # here only 'if' condition is for getting all files name, used for file upload when check same name exist or not
            if request.method == 'POST':
                return HttpResponse(json.dumps(fileList), content_type="application/json")

            objList = []
            # print (fileList)
            # rootdict = {
            #     'text': 'public',
            #     'parent_id': 'root',
            #     'expanded': True,
            #     'spriteCssClass': 'rootfolder',
            #     'path': "public/"
            # }
            rootdict = {
                'text': 'files',
                'parent_id': 'root',
                'expanded': True,
                'spriteCssClass': 'rootfolder',
                'path': url + "/"
            }
            objList.append(rootdict)
            for obj in fileList:
                str = obj.split("/")
                depth_level = len(str)
                path = url
                for index in range(2, depth_level):
                    if index + 1 < depth_level:
                        if str[index + 1] != '':
                            dict = {}
                            dict['text'] = str[index + 1]
                            path = path + "/" + str[index + 1]
                            dict['parent_id'] = str[index]
                            dict['path'] = path

                            dict['expanded']=True
                            file = str[index + 1].split(".")
                            if len(file) == 1:
                                dict['spriteCssClass'] = 'folder'
                            else:
                                if file[1].lower() == "png" or file[1].lower() == "jpeg" or file[1].lower() == "jpg" or file[1].lower() == "svg":
                                    dict['spriteCssClass'] = 'image'
                                elif file[1].lower() == "css" or file[1].lower() == "html":
                                    # dict['spriteCssClass'] = 'file'
                                    dict['spriteCssClass'] = 'html'
                                elif file[1].lower() == "pdf":
                                    # dict['spriteCssClass'] = 'file'
                                    dict['spriteCssClass'] = 'pdf'
                                elif file[1].lower() == "txt":
                                    # dict['spriteCssClass'] = 'file'
                                    dict['spriteCssClass'] = 'html'
                                else:
                                    # dict['spriteCssClass'] = 'file'
                                    dict['spriteCssClass'] = 'html'

                            found = False
                            for object in objList:
                                if object['text'] == dict['text'] and object['parent_id'] == dict['parent_id']:
                                    found = True
                                    break
                            if not found:
                                objList.append(dict)


            ph = FileView.buildTree(objList)

            context = {
                'filelist': json.dumps(ph)
            }
        except Exception as e:
            print(e)
            context = {
                'filelist': []
            }
        return context

    def update_offline_status(request):
        event_id = request.session['event_auth_user']['event_id']
        DeviceToken.objects.filter(attendee__event_id=event_id).update(offline_pakage_status=1)