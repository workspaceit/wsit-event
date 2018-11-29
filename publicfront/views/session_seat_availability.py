from app.models import SeminarsUsers
from publicfront.views.helper import HelperData


class SessionSeatAvailability:
    def get_seats_availability(request, session, session_option, event_id, all_langs={}):
        try:
            session_attendees = SeminarsUsers.objects.filter(session_id=session.id, status='attending').count()
            seats_remain = session.max_attendees - session_attendees
            if 'is_user_login' in request.session and request.session['is_user_login']:
                check_radio = SeminarsUsers.objects.filter(session_id=session.id,
                                                           attendee_id=request.session['event_user']['id'])
                if check_radio.exists():
                    session.status = check_radio[0].status
                    # if check_radio[0].status == "attending" or check_radio[0].status == "in-queue":
                    if check_radio[0].status == "attending":
                        # preselected_session_history = True
                        session.check_radio = True
                        session.check_checkbox = True
                    elif check_radio[0].status == "in-queue":
                        session.check_radio = False
                        session.check_checkbox = True
                    else:
                        session.check_radio = False
                        session.check_checkbox = False
                else:
                    session.check_radio = False
                    session.check_checkbox = False
            if seats_remain < 0:
                seats_remain = 0
            if seats_remain == 0 and not session.allow_attendees_queue and not int(session.max_attendees) == 0:
                session.disable = True
            else:
                session.disable = False
            if session_option == 'x':
                session.availability = str(seats_remain)
            elif session_option == 'x-of-y':
                x_of_y_availability_message = all_langs['langkey']['sessiondetails_txt_seat_availability_x_of_y']
                availability_message = x_of_y_availability_message.replace('{X}', str(seats_remain)).replace('{Y}', str(
                    session.max_attendees))
                session.availability = availability_message
            elif session_option == 'estimate':
                remain_attending_percent = (seats_remain * 100) / session.max_attendees
                if remain_attending_percent == 0:
                    if session.allow_attendees_queue == 1:
                        no_seats_available = all_langs['langkey']['sessiondetails_txt_no_seats_available']
                        queue_is_open = all_langs['langkey']['sessiondetails_txt_seats_available_queue_is_open']
                        availability_message = no_seats_available + ', ' + queue_is_open
                        availability = availability_message
                    else:
                        no_seats_available = all_langs['langkey']['sessiondetails_txt_no_seats_available']
                        availability = no_seats_available
                elif remain_attending_percent >= 10:
                    seats_available = all_langs['langkey']['sessiondetails_txt_seats_available']
                    availability = seats_available
                elif remain_attending_percent < 10:
                    few_seats_available = all_langs['langkey']['sessiondetails_txt_few_seats_available']
                    availability = few_seats_available
                session.availability = availability
            else:
                session.availability = ''
        except Exception as e:
            print(e)
        return session

    def get_vat_lang(request, session, session_option, event_id,economy_lang,all_langs={}):
        lang_vat_included = economy_lang['economy_cost']['langkey']['economy_txt_cost_incl_vat']
        lang_vat_excluded = economy_lang['economy_cost']['langkey']['economy_txt_cost_excl_vat']
        economy_currency_txt = economy_lang['economy_currency_txt']
        amount = session.get_vat_amount()
        if not HelperData.isint(amount):
            amount = '{:0,.2f}'.format(amount).replace(",", " ")
        else:
            amount = '{0:,}'.format(int(amount)).replace(",", " ")
        if session.vat != None:
            lang_vat_included = lang_vat_included.replace("{X}", '%s %s'%(amount,economy_currency_txt))
            session.lang_vat_included = lang_vat_included

            lang_vat_excluded = lang_vat_excluded.replace("{X}", '%s %s'%(amount,economy_currency_txt))
            session.lang_vat_excluded = lang_vat_excluded
        else:
            lang_vat_included = lang_vat_included.replace("{X}", '%s %s'%(str(0),economy_currency_txt))
            session.lang_vat_included = lang_vat_included

            lang_vat_excluded = lang_vat_excluded.replace("{X}", '%s %s'%(str(0),economy_currency_txt))
            session.lang_vat_excluded = lang_vat_excluded
        return session