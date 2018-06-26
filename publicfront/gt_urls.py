from django.conf.urls import url
from .gt_views import attendee, login, notification ,common,session, static_page
from django.conf import settings

urlpatterns = [
    url(r'^registration/$', attendee.AttendeeRegistration.as_view(), name='gt-registration'),
    url(r'^signin/$', attendee.login.as_view(), name='gt-registration'),
    url(r'^min-medverkan/$', attendee.AttendeeRegistration.optional_registration, name='gt-min-medverkan'),
    url(r'^min-medverkan-post/$', attendee.AttendeeRegistration.optional_registration_read, name='gt-min-medverkan-post'),
    url(r'^add-participation/$', attendee.AttendeeRegistration.add_participation, name='gt-add-participation'),
    url(r'^get-participation-info/$', attendee.AttendeeRegistration.get_participation, name='gt-get-participation-info'),
    url(r'^$', common.CommonMenu.start, name='gt-welcome'),
    url(r'^mina-kurser/$', common.CommonMenu.mina_kurser, name='gt-mina-kurser'),
    url(r'^mina-kurser-post/$', common.CommonMenu.mina_kurser_post, name='gt-mina-kurser-post'),
    url(r'^mina-semiarieval/$', common.CommonMenu.mina_semiarieval, name='gt-mina-semiarieval'),
    url(r'^training-aktiviteter/$', common.CommonMenu.mina_training_aktiviteter, name='gt-training-aktiviteter'),
    url(r'^aktiviteter/$', common.CommonMenu.aktiviteter, name='gt-aktiviteter'),
    url(r'^mina-seminarier/$', common.CommonMenu.mina_seminarier, name='gt-mina-seminarier'),
    url(r'^get-together/$', common.CommonMenu.get_together, name='gt-get-together'),
    url(r'^information/$', common.CommonMenu.information, name='gt-information'),
    url(r'^hitta-hit/$', common.CommonMenu.hitta_hit, name='gt-hitta-hit'),
    url(r'^ladda-ner-som-app/$', common.CommonMenu.ladda_ner, name='gt-ladda-ner-som-app'),
    url(r'^attendee/getattendees_alt/$', attendee.AttendeeRegistration.get_attendees_alt, name='get_attendees_alt'),
    url(r'^activation/$', login.UserLogin.as_view(), name='gt-activation'),
    url(r'^login/$', login.LoginView.as_view(), name='gt-user-login'),
    url(r'^logout/$', login.LogoutView.as_view(), name='gt-user-logout'),
    url(r'^sessions/(?P<pk>[0-9]+)/$', session.SessionDetail.as_view(), name='gt-session-detail'),
    url(r'^session-detail-post/(?P<pk>[0-9]+)/$', session.SessionDetail.session_detail_post, name='gt-session-detail-post'),
    url(r'^static-pages/$', static_page.StaticPage.as_view(), name='gt-static-pages'),
    url(r'^static-pages/(?P<staticPage>[\w-]+)/$', static_page.StaticPage.get_static_page, name='gt-static-page'),
    url(r'^sen-anmalan/$', attendee.SenRegistration.as_view(), name='gt-sen-anmalan'),
    url(r'^summering/$', common.CommonMenu.summering, name='gt-summering'),
    url(r'^gt-notifications/$', notification.NotificationClass.notifications, name='gt-notifications'),
    url(r'^gt-get-notifications/$', notification.NotificationClass.get_notifications, name='gt-get-notifications'),
    url(r'^gt-delete-notification/$', notification.NotificationClass.deletenotification, name='gt-delete-notification'),
    url(r'^gt-set-ratings/$', common.CommonMenu.set_session_ratings, name='gt-set-ratings'),
    url(r'^start-test/$', common.CommonMenu.start_test, name='start-test'),
    url(r'^app/$', common.CommonMenu.gt_app, name='app'),
    url(r'^ff/$', common.CommonMenu.gt_ff, name='ff'),
    url(r'^vfk/$', common.CommonMenu.gt_vfk, name='vfk'),

]

