from django.conf.urls import url

from publicfront.views import document_list, page_replace, attendee_plugin_datatable
from publicfront.views import reset_password_view
from .views import attendee, common, login, profile, export_session, search, photo, location, \
    session_message, \
    offline_download, page2, notify_view, nextup_evaluation, registration, attendee_plugin, \
    hotel_reservation_plugin, \
    socket, plugin, payment

urlpatterns = [
    url(r'^attendee-registration/$', registration.Registration.save_or_update_data, name='attendee-registration'),
    url(r'^attendee-login/$', login.LoginView.as_view(), name='attendee-login'),
    url(r'^retrieve-uid/$', login.LoginView.retrieve_uid, name='retrieve-uid'),

    url(r'^$', common.AttendeeSession.welcome, name='welcome'),

    url(r'^get-session-group/$', common.AttendeeSession.getSessionGroup, name='get-session-group'),
    url(r'^get-session-event/$', common.AttendeeSession.getSessionEvent, name='get-session-event'),
    url(r'^get-session-group2/$', common.AttendeeSession.getSessionGroup2, name='get-session-group2'),
    url(r'^get-session-event2/$', common.AttendeeSession.getSessionEvent2, name='get-session-event2'),
    url(r'^webcal/$', common.AttendeeSession.webcal, name='webcal'),

    url(r'^set-ratings/$', common.AttendeeSession.set_session_ratings, name='set-ratings'),

    url(r'^notifications/$', socket.SocketView.notifications, name='notifications'),
    url(r'^get-notifications/$', profile.AttendeeProfile.getnotifications, name='get-notifications'),
    url(r'^delete-notification/$', profile.AttendeeProfile.deletenotification, name='delete-notification'),

    url(r'^public-locations/$', profile.AttendeeProfile.myLocations, name='public-locations'),
    url(r'^locations/$', location.LocationDetail.as_view(), name='publicLocations'),
    url(r'^locations-search/$', location.LocationDetail.search_location, name='locations-search'),
    url(r'^locations/(?P<pk>[0-9]+)/$', location.LocationDetail.as_view(), name='publicLocations-detail'),

    url(r'^notification-session/$', profile.AttendeeProfile.sessionNotification, name='notification-session'),
    url(r'^sessions-search/$', search.SessionFilter.search_sessions, name='sessions-search'),
    url(r'^sessions/$', profile.SessionDetail.as_view(), name='publicSessions'),
    url(r'^sessions/(?P<pk>[0-9]+)/$', profile.SessionDetail.as_view(), name='public-session-detail'),
    url(r'^attend-or-cancel-session/$', profile.SessionDetail.attend_or_cancel, name='attend_or_cancel_session'),
    url(r'^get-updated-session-info/$', page2.Plugins.get_updated_session_info, name='get-updated-session-info'),

    url(r'^attendee-bio/$', attendee.AttendeeInfo.as_view(), name='attendee-bio'),
    url(r'^attendee-bio/(?P<pk>[0-9]+)/$', attendee.AttendeeInfo.as_view(), name='attendee-bio'),

    url(r'^export-session/$', export_session.ExportSession.as_view(), name='export-session'),
    url(r'^getDesiredAttList/$', export_session.ExportSession.getDesiredAttList, name='getDesiredAttList'),
    url(r'^export-attendee-list/$', export_session.ExportSession.export_for_speaker, name='sessionExport'),

    url(r'^get-timezone/$', common.AttendeeSession.get_timezone, name='get-timezone'),
    url(r'^get-allowed-emails/$', common.AttendeeSession.getAllowedEmail, name='get-allowed-emails'),

    url(r'^page-locations-search/$', page2.Plugins.page_search_location, name='page-locations-search'),

    url(r'^archive-all-messages/$', session_message.SessionMessageView.archive_all_messages,
        name='archive-all-messages'),

    url(r'^offline/$', offline_download.OfflineExport.s3_offline_package, name='export-for-offline'),

    url(r'^notify/$', notify_view.NotifyView.as_view(), name='notifyview'),

    url(r'^reset-password/$', common.AttendeeSession.reset_password, name='reset-password-public'),
    url(r'^request-login/$', common.AttendeeSession.request_login, name='request-login'),
    url(r'^session-next-up/(?P<pk>[0-9]+)/$', nextup_evaluation.NextupEvaluation.nextup, name='session-next-up'),
    url(r'^session-evaluation/(?P<pk>[0-9]+)/$', nextup_evaluation.NextupEvaluation.evaluation,
        name='session-evaluation'),
    url(r'^message-notification/$', nextup_evaluation.NextupEvaluation.messages, name='message-notification'),
    url(r'^socket/$', socket.SocketView.as_view(), name='socket'),
    url(r'^document-list/$', document_list.DocumentDetail.as_view(), name='document-list'),

    # not for publicly usage start
    url(r'^resetpass/$', reset_password_view.ResetPasswordPublic.as_view(), name='resetpass'),
    url(r'^savepass/$', reset_password_view.ResetPasswordPublic.save_new_password, name='savepass'),
    url(r'^upload-files/$', photo.PhotoReel.upload_files_request, name='upload-files'),
    url(r'^get-push-notification-status/$', attendee.AttendeeInfo.get_push_notification_status,
        name='get-push-notification-status'),
    url(r'^change-push-notification-status/$', attendee.AttendeeInfo.change_push_notification_status,
        name='change-push-notification-status'),
    url(r'^get-eval-next-up-msg/$', page2.DynamicPage.get_eval_next_up_msg, name='get-eval-next-up-msg'),

    # not for publicly usage end
    url(r'^attendee-plugin-datatable/$', attendee_plugin.AttendeePluginList.attendee_datatable,
        name='attendee-plugin-datatable'),
    url(r'^export-plugin-attendee/$', attendee_plugin.AttendeePluginList.export_attendee,
        name='export-plugin-attendee'),
    url(r'^attendee-plugin-export-state/$', attendee_plugin.AttendeePluginList.attendee_plugin_export_state,
        name='attendee-plugin-export-state'),

    url(r'^hotel-reservation-plugin-buddy-list/$', hotel_reservation_plugin.HotelReservationPlugin.buddy_list,
        name='hotel-reservation-plugin-buddy-list'),
    url(r'^hotel-reservation-partial-alow-element/$',
        hotel_reservation_plugin.HotelReservationPlugin.get_partial_allow_element,
        name='hotel-reservation-partial-alow-element'),

    url(r'^check-session-availability/$', page2.Plugins.check_session_availability, name='check_session_availability'),
    url(r'^check-session-availability-act-radio/$', page2.Plugins.check_session_availability_act_radio,
        name='check_session_availability_act_radio'),
    url(r'^session-set-unset-availability/$', page2.Plugins.session_set_unset_availability,
        name='session-set-unset-availability'),
    url(r'^get-scheduler-session-details/$', page2.Plugins.get_scheduler_session_details,
        name='get-scheduler-session-details'),

    url(r'^get-location-details/(?P<pk>[0-9]+)/$', page2.Plugins.get_location_details, name='get-location-details'),
    url(r'^get-attendee-details/(?P<pk>[0-9]+)/$', page2.Plugins.get_attendee_details, name='get-attendee-details'),

    url(r'^get-photo-gallery-images/$', page2.Plugins.get_photo_gallery_image, name='get-photo-gallery-images'),
    url(r'^get-gallery-photo-details/$', page2.Plugins.get_gallery_photo_details, name='get-gallery-photo-details'),
    url(r'^change-language/$', page2.PageWithLanguage.change_language, name='change-language'),
    url(r'^session-schedule/$', common.AttendeeSession.sessionSchedule, name='session-schedule'),

    url(r'^check-min-max-registration-attendee/$', page2.MultipleRegistration.check_multiple_registration_attendee,
        name='check-min-max-registration-attendee'),
    url(r'^get-multiple-registration-attendee-form/$',
        page2.MultipleRegistration.get_multiple_registration_attendee_form,
        name='get-multiple-registration-attendee-form'),
    url(r'^get-attendee-next-page/$', page2.MultipleRegistration.get_attendee_next_page, name='get-attendee-next-page'),

    url(r'^multiple-attendee-save/$', registration.Registration.multiple_attendee_save_or_update,
        name='multiple-attendee-save'),
    url(r'^multiple-attendee-save-inline/$', registration.Registration.multiple_attendee_save_or_update_inline,
        name='multiple-attendee-save-inline'),
    url(r'^add-new-pages/$', registration.AutoLoginView.add_new_pages, name='add-new-pages'),
    url(r'^delete-temporary-attendee/$', plugin.Plugins.delete_temporary_attendee, name='delete-temporary-attendee'),
    url(r'^delete-temporary-attendee-session/$', plugin.Plugins.delete_temporary_attendee_session,
        name='delete-temporary-attendee-session'),

    url(r'^economy-change-order-status/$', page2.Plugins.economy_change_order_status,
        name='economy-change-order-status'),
    url(r'^economy-pdf-request/$', page2.Plugins.economy_pdf_request, name='economy-pdf-request'),
    url(r'^convert-html-to-pdf/$', page2.Plugins.convert_html_to_pdf, name='convert-html-to-pdf'),

    url(r'^get-order-info-for-payment/$', payment.Payment.get_order_info_for_payment,
        name='get-order-info-for-payment'),
    url(r'^payment-callback-success/$', payment.Payment.payment_callback_success, name='payment-callback-success'),
    url(r'^payment-callback-cancel/$', payment.Payment.payment_callback_cancel, name='payment-callback-cancel'),

    # session agenda
    url(r'^get-session-agenda-filtered-data/$', page2.Plugins.get_filtered_session_agenda,
        name='get-session-agenda-filtered-data'),
    url(r'^get-date-with-language/$', page2.PageWithLanguage.get_date_with_language, name='get-date-with-language'),

    # attendee list plugin
    url(r'^get-attendee-plugin-data/$', page2.Plugins.get_attendee_plugin_data,
        name='get-attendee-plugin-pagination-data'),
    url(r'^get-attendee-plugin-data-2/$', page2.Plugins.get_attendee_plugin_data_2,
        name='get-attendee-plugin-pagination-data-2'),
    url(r'^get-attendee-plugin-dt/$', attendee_plugin_datatable.AttendeePluginDatatable.as_view(),
        name='get-attendee-plugin-dt'),
    url(r'^get-logout-plugin/$', page2.Plugins.get_logout_plugin, name='get-logout-plugin'),

    url(r'^get-session-expire-lang/$', page_replace.PageReplace.get_session_expire_lang,
        name='get-session-expire-lang'),
    url(r'^qr-to-png$', page2.QRResponse.as_view(), name='qr-to-png'),
    url(r'^admin-attendee-logged-in/$', registration.AutoLoginView.logged_in_using_admin_email, name='admin-attendee-logged-in'),
    # No url should be written after the upper url "static-pages"
    url(r'^api/(?P<staticPage>[\w-]+)/$', page2.DynamicPage.get_dynamic_page_filtered, name='dynamic-pages'),
    url(r'^(?P<staticPage>[\w-]+)/$', page2.DynamicPage.get_static_page, name='static-pages'),
]
