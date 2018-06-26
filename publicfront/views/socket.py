from django.shortcuts import render
from django.views import generic
from publicfront.views.page2 import DynamicPage
from django.shortcuts import render, redirect

class SocketView(generic.DetailView):
    def get(self, request, *args, **kwargs):
        content = {
            'uid': request.session['event_user']['secret_key']
        }
        return render(request, 'public/socket/index.html', content)

    def notifications(request, *args, **kwargs):
        if 'is_user_login' in request.session and request.session['is_user_login']:
            return DynamicPage.get_static_page(request,'messages',True,*args, **kwargs)
        else:
            return redirect('welcome', event_url=request.session['event_url'])
