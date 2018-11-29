import json, os, math, time
from datetime import datetime, timedelta
from django.db.models import Max, Min, Sum, F
from django.db import transaction
from app.models import Orders, OrderItems, CreditOrders, Session, Setting, Rebates, ActivityHistory, \
    RegistrationGroupOwner, Attendee, CreditUsages, Payments, Room, RoomAllotment, Booking

from app.views.gbhelper.language_helper import LanguageH
from app.views.gbhelper.error_report_helper import ErrorR


class EconomyLibrary:
    """This class is for economy common functionalities."""

    def get_order_tables(user_id, event_id, public=False, order_number=None):
        """ order_number is for invoice, here need only one order(attendee/multiple),
            otherwise order_number must be ignored
        """
        try:
            order_list = []
            orders = []
            user_id = int(user_id)
            group_reg_info = EconomyLibrary.get_group_registration_info(user_id)
            if group_reg_info['group-attendee']:
                order_type = 'group-order'
            else:
                order_type = 'attendee-order'

            if order_number:
                if user_id not in group_reg_info['grp-atts']:
                    raise ValueError('Wrong information provided. Given Attendee: {}, group atts: {}'.format(user_id, group_reg_info['grp-atts']))
                orders = Orders.objects.filter(order_number=order_number, cost__gt=0, attendee__event_id=event_id)
            else:
                if order_type == 'attendee-order':
                    if not group_reg_info['group-attendee']:
                        orders = Orders.objects.filter(attendee_id=user_id, cost__gt=0,).order_by('status')
                else:
                    if group_reg_info['group-attendee']:
                        group_attendees = group_reg_info['grp-atts']
                        orders = Orders.objects.filter(attendee_id__in=group_attendees, cost__gt=0,).order_by('status', 'order_number')

            order_number_checker = None
            order_id = None
            order_status = None
            order_due_date = None
            order_ref_id = None
            invoice_date = None
            language_id = None
            group_total_cost_exl_vat = 0
            group_total_cost_incl_vat = 0
            group_total_vat_amount = 0
            group_total_rebate_amount = 0
            group_order_detail = []
            for order in orders:
                if public and order.status == 'cancelled':
                    continue
                order_list_item = EconomyLibrary.get_individual_order_table(order, order_type, public)
                if order_list_item:
                    if order_type == 'attendee-order':
                        credit_usage_info = EconomyLibrary.get_credit_usage_payment(order.order_number)
                        order_list_item['credit_usages'] = credit_usage_info['credit_usage']
                        order_list_item['total_cost_incl_vat'] -= credit_usage_info['total_amount']
                        order_list_item['order_amount_due'] -= credit_usage_info['total_amount'] if order.status == 'pending' else 0
                        order_list_item['show_balance_table'] = True
                        order_list.append(order_list_item)
                    else:
                        show_balance_table = False
                        if order_number_checker == None:
                            order_number_checker = order.order_number
                            show_balance_table = True

                        if order_number_checker != order.order_number:
                            show_balance_table = True
                            credit_usage_info = EconomyLibrary.get_credit_usage_payment(order_number_checker)
                            group_order_detail.append({
                                'is_group_total': True,
                                'is_group_detail': True,
                                'is_owner': group_reg_info['is_owner'],
                                'order_id': order_id,
                                'order_number': order_number_checker,
                                'order_status': order_status,
                                'order_status_lang': EconomyLibrary.get_status_from_lang(language_id, order_status),
                                'due_date': str(order_due_date),
                                'due_date_datetype': order_due_date,
                                'invoice_ref': order_ref_id,
                                'invoice_date': invoice_date,
                                'order_amount_due': group_total_cost_incl_vat - credit_usage_info['total_amount'] if order_status == 'pending' else 0
                            })
                            order_list.append({
                                'is_group_total': True,
                                'is_owner': group_reg_info['is_owner'],
                                'order_id': order_id,
                                'order_number': order_number_checker,
                                'order_status': order_status,
                                'order_status_lang': EconomyLibrary.get_status_from_lang(language_id, order_status),
                                'due_date': str(order_due_date),
                                'due_date_datetype': order_due_date,
                                'invoice_ref': order_ref_id,
                                'invoice_date': invoice_date,
                                'credit_usages': credit_usage_info['credit_usage'],
                                'group_total_cost_exl_vat': group_total_cost_exl_vat,
                                'group_total_cost_incl_vat': group_total_cost_incl_vat - credit_usage_info['total_amount'],
                                'group_total_rebate_amount': group_total_rebate_amount,
                                'keep_rebate_column': False if group_total_rebate_amount == 0 else True,
                                'group_total_vat_amount': group_total_vat_amount,
                                'order_amount_due': group_total_cost_incl_vat - credit_usage_info['total_amount'] if order_status == 'pending' else 0
                            })
                            order_number_checker = order.order_number
                            group_total_cost_exl_vat = 0
                            group_total_cost_incl_vat = 0
                            group_total_vat_amount = 0
                            group_total_rebate_amount = 0

                        order_list_item['show_balance_table'] = show_balance_table
                        order_list.append(order_list_item)
                        group_total_cost_exl_vat += order_list_item['total_cost_exl_vat']
                        group_total_cost_incl_vat += order_list_item['total_cost_incl_vat']
                        group_total_vat_amount += order_list_item['total_vat_amount']
                        group_total_rebate_amount += order_list_item['total_rebate_amount']
                        order_id = order.id
                        order_status = order.status
                        order_due_date = order.due_date
                        order_ref_id = order.invoice_ref
                        invoice_date = order.invoice_date
                        language_id = order.attendee.language_id

            if order_number_checker:
                credit_usage_info = EconomyLibrary.get_credit_usage_payment(order_number_checker)
                group_order_detail.append({
                    'is_group_total': True,
                    'is_group_detail': True,
                    'is_owner': group_reg_info['is_owner'],
                    'order_id': order_id,
                    'order_number': order_number_checker,
                    'order_status': order_status,
                    'order_status_lang': EconomyLibrary.get_status_from_lang(language_id, order_status),
                    'due_date': str(order_due_date),
                    'due_date_datetype': order_due_date,
                    'invoice_ref': order_ref_id,
                    'invoice_date': invoice_date,
                    'order_amount_due': group_total_cost_incl_vat - credit_usage_info['total_amount'] if order_status == 'pending' else 0
                })
                order_list.append({
                    'is_group_total': True,
                    'is_owner': group_reg_info['is_owner'],
                    'order_id': order_id,
                    'order_number': order_number_checker,
                    'order_status': order_status,
                    'order_status_lang': EconomyLibrary.get_status_from_lang(language_id, order_status),
                    'due_date': str(order_due_date),
                    'due_date_datetype': order_due_date,
                    'invoice_ref': order_ref_id,
                    'invoice_date': invoice_date,
                    'credit_usages': credit_usage_info['credit_usage'],
                    'group_total_cost_exl_vat': group_total_cost_exl_vat,
                    'group_total_cost_incl_vat': group_total_cost_incl_vat - credit_usage_info['total_amount'],
                    'group_total_rebate_amount': group_total_rebate_amount,
                    'keep_rebate_column': False if group_total_rebate_amount == 0 else True,
                    'group_total_vat_amount': group_total_vat_amount,
                    'order_amount_due': group_total_cost_incl_vat - credit_usage_info['total_amount'] if order_status == 'pending' else 0
                })

            for grp_item in group_order_detail:
                index_to_insert = 0
                order_number_grp = grp_item['order_number']
                for ol_item in order_list:
                    if not ol_item.get('is_group_total') and ol_item['order']['order_number'] == order_number_grp:
                        order_list.insert(index_to_insert, grp_item)
                        break
                    index_to_insert += 1

            return {'order_list': order_list, 'order_type': order_type}
        except Exception as ex:
            ErrorR.efail(ex)
            return {'order_list': [], 'order_type': ''}

    def get_individual_order_table(order, order_type=False, public=False):
        event_id = order.attendee.event_id
        if public:
            order_item_items = OrderItems.objects.filter(order_id=order.id).exclude(item_type='rebate')
            order_item_rebates = OrderItems.objects.filter(order_id=order.id, item_type='rebate', applied_on_open_order=True).exclude(rebate_amount=0)
        else:
            order_item_items = OrderItems.objects.filter(order_id=order.id).exclude(item_type='rebate')
            order_item_rebates = OrderItems.objects.filter(order_id=order.id, item_type='rebate')
        session_sort = Session.objects.filter(group__event_id=event_id).values_list('id',flat=True).order_by('group__group_order','session_order')

        if len(session_sort) > 0:
            try:
                s_clauses = ' '.join(['WHEN item_id=%s THEN %s' % (pk, i) for i, pk in enumerate(session_sort)])
                s_ordering = 'CASE %s END' % s_clauses
                all_sessions = order_item_items.filter(item_type='session').extra(select={'ordering': s_ordering},
                                                                                  order_by=('ordering',))
            except Exception as e:
                ErrorR.efail(e)
                all_sessions = []
                pass
        else:
            all_sessions = []
        hotel_sort = Room.objects.filter(hotel__group__event_id=event_id).values_list('id',flat=True).order_by('hotel__group__group_order','room_order')
        if len(hotel_sort) > 0:
            try:
                h_clauses = ' '.join(['WHEN item_id=%s THEN %s' % (pk, i) for i, pk in enumerate(hotel_sort)])
                h_ordering = 'CASE %s END' % h_clauses
                all_hotels = order_item_items.filter(item_type='hotel').extra(select={'ordering': h_ordering}, order_by=('ordering',))
            except Exception as e:
                ErrorR.efail(e)
                all_hotels = []
                pass
        else:
            all_hotels = []
        order_item_sessions = [obj for obj in all_sessions]
        order_item_hotels = [obj for obj in all_hotels]
        adjustments = [obj for obj in order_item_items.filter(item_type='adjustment')]
        order_items = order_item_sessions + order_item_hotels + adjustments
        for rebate_object in order_item_rebates:
            item_index = 0
            for item_object in order_items:
                item_index += 1
                if rebate_object.rebate_for_item_type == item_object.item_type and rebate_object.rebate_for_item_id == item_object.rebate_for_item_id:
                    order_items.insert(item_index, rebate_object)

        order_item_list = []
        vats = []
        total_cost_exl_vat = 0
        total_cost_incl_vat = 0
        total_vat_amount = 0
        total_rebate_amount = 0
        for order_item in order_items:
            new_vat_rate = True
            order_item_as_dict = order_item.as_dict()
            order_item_as_dict['cost'] = order_item.cost + order_item.rebate_amount
            if order_item.vat_rate:
                total_vat_amount += order_item.get_vat_amount()
            if order_item.item_type != 'rebate':
                total_cost_exl_vat += order_item.cost
                total_cost_incl_vat += order_item.get_total_cost()
            else:
                if order_item.rebate_amount:
                    total_rebate_amount += order_item.rebate_amount

                tem_obj = order_item_items.filter(item_type=order_item.rebate_for_item_type, item_id=order_item.rebate_for_item_id,
                                        order_id=order_item.order_id)
                if tem_obj.exists():
                    order_item_as_dict['cost'] = tem_obj[0].cost
                    order_item_as_dict['vat_rate'] = tem_obj[0].vat_rate
                    order_item_as_dict['vat_amount'] = tem_obj[0].get_vat_amount()
                    order_item_as_dict['total_cost'] = tem_obj[0].get_total_cost()

            for vat in vats:
                if order_item.vat_rate == vat['vat_rate']:
                    vat['amount'] += order_item.get_vat_amount()
                    new_vat_rate = False
                    break
            if new_vat_rate and order_item.item_type not in ['rebate', 'adjustment']:
                vats.append({'vat_rate': order_item.vat_rate, 'amount': order_item.get_vat_amount()})

            order_item_list.append(order_item_as_dict)
        if public and len(order_item_list) == 0:
            return False

        order_as_dict = order.as_dict()
        order_as_dict['status_lang'] = EconomyLibrary.get_status_from_lang(order.attendee.language_id, order.status)
        return {
            'order': order_as_dict,
            'order_items': order_item_list,
            'total_cost_exl_vat': total_cost_exl_vat,
            'total_cost_incl_vat': total_cost_incl_vat,
            'total_vat_amount': total_vat_amount,
            'total_rebate_amount': total_rebate_amount * (-1),
            'keep_rebate_column': False if total_rebate_amount == 0 else True,
            'vats': vats,
            'balance_table': EconomyLibrary.get_balance_tables(order.attendee_id, order.attendee.event_id, order.id),
            'order_amount_due': total_cost_incl_vat if order.status == 'pending' else 0
        }

    def get_group_order_single_table(order_list):
        combined_group_orders = []
        order_item_list = []
        vat_list = []
        balance_table = None
        try:
            for order in order_list:
                if order.get('is_group_total') and order.get('is_group_detail'):
                    order_item_list = []
                    vat_list = []
                elif order.get('is_group_total') and not order.get('is_group_detail'):
                    combined_group_orders.append({
                        'order': order,
                        'order_items': order_item_list,
                        'balance_table': balance_table,
                        'vats': vat_list
                    })
                else:
                    balance_table = order.get('balance_table')
                    for order_item in order['order_items']:
                        order_item['attendee_name'] = order['order']['attendee']['full_name']
                        order_item_list.append(order_item)

                    if len(vat_list) > 0:
                        for vat in order['vats']:
                            new_vat_rate = True
                            for vl_item in vat_list:
                                if vl_item['vat_rate'] == vat['vat_rate']:
                                    vl_item['amount'] += vat['amount']
                                    new_vat_rate = False
                                    break
                            if new_vat_rate:
                                vat_list.append({'vat_rate': vat['vat_rate'], 'amount': vat['amount']})
                    else:
                        vat_list = order['vats']

        except Exception as ex:
            ErrorR.efail(ex)
        return combined_group_orders

    def get_balance_tables(user_id, event_id, order_id=None):
        try:
            balance_table_list = []
            skip_duplicate_order_number = []
            if order_id:
                orders = Orders.objects.filter(id=order_id, status__in=['pending', 'paid'])
            else:
                group_info = EconomyLibrary.get_group_registration_info(user_id)
                orders = Orders.objects.filter(attendee_id__in=group_info['grp-atts'], cost__gt=0, status__in=['pending', 'paid']).order_by('status')
            for order in orders:
                if order.order_number in skip_duplicate_order_number:
                    continue
                skip_duplicate_order_number.append(order.order_number)
                order_costs = Orders.objects.filter(order_number=order.order_number, attendee__event_id=event_id).aggregate(
                    total_excl=Sum(F('cost')), total_incl=Sum(F('cost') + F('vat_amount')))
                invoice_created_settle_detail = {
                    'order_id': order.id,
                    'cost_excl_vat': order_costs['total_excl'],
                    'cost_incl_vat': order_costs['total_incl'],
                    'date': order.created_at
                }
                balance_table = {
                    'order_number': order.order_number,
                    'invoice_created': invoice_created_settle_detail
                }
                if order.status == 'paid':
                    obj = Payments.objects.filter(order_number=order.order_number)
                    invoice_created_settle_detail2 = {
                        'order_id': order.id,
                        'cost_excl_vat': order_costs['total_excl'],
                        'cost_incl_vat': order_costs['total_incl'],
                        'date': obj[0].created_at
                    }
                    balance_table['invoice_settled'] = invoice_created_settle_detail2

                credit_orders = CreditOrders.objects.filter(order_number=order.order_number,
                                                            order__attendee__event_id=event_id, status='open')
                total_cr_amount_excluding_vat = 0
                total_cr_amount_including_vat = 0
                credit_order_list = []
                for credit_order in credit_orders:
                    total_cr_amount_excluding_vat += credit_order.cost_excluding_vat
                    total_cr_amount_including_vat += credit_order.cost_including_vat
                    credit_order_list.append({
                        'credit_order_id': credit_order.id,
                        'cost_excl_vat': credit_order.cost_excluding_vat * (-1),
                        'cost_incl_vat': credit_order.cost_including_vat * (
                            -1) if credit_order.cost_including_vat else credit_order.cost_excluding_vat,
                        'date': credit_order.created_at
                    })

                order_balance_cost_excl_vat = order_costs['total_excl'] - total_cr_amount_excluding_vat
                order_balance_cost_incl_vat = order_costs['total_incl'] - total_cr_amount_including_vat
                balance_table['credit_invoices'] = credit_order_list
                balance_table['total_amount_excluding_vat'] = order_balance_cost_excl_vat * -1 if order.status == 'pending' else 0
                balance_table['total_amount_including_vat'] = (order_balance_cost_incl_vat * -1) if order.status == 'pending' else 0
                balance_table_list.append(balance_table)
            return balance_table_list
        except Exception as ex:
            ErrorR.efail(ex)

    def get_order_value(user_id, status, type='attendee-order', order_type='order'):
        try:
            if order_type == 'order':
                if type == 'attendee-order':
                    if status != 'all':
                        order = Orders.objects.filter(attendee_id=user_id, status=status).aggregate(
                            total=Sum(F('cost') + F('vat_amount')))
                    else:
                        order = Orders.objects.filter(attendee_id=user_id).exclude(status='cancelled').aggregate(
                            total=Sum(F('cost') + F('vat_amount')))

                    return order['total']
                else:
                    result = EconomyLibrary.get_group_registration_info(user_id)
                    if result['group-attendee']:
                        all_attendee = result['grp-atts']
                        if status != 'all':
                            order = Orders.objects.filter(attendee_id__in=all_attendee, status=status).aggregate(
                                total=Sum(F('cost') + F('vat_amount')))
                        else:
                            order = Orders.objects.filter(attendee_id__in=all_attendee).exclude(
                                status='cancelled').aggregate(
                                total=Sum(F('cost') + F('vat_amount')))

                        return order['total']
                    else:
                        return
            elif order_type == 'credit-order':
                if type == 'attendee-order':
                    order = CreditOrders.objects.filter(order__attendee_id=user_id, status=status).aggregate(
                        total=Sum(F('cost_including_vat')))
                    return order['total']
                else:
                    result = EconomyLibrary.get_group_registration_info(user_id)
                    if result['group-attendee']:
                        all_attendee = result['grp-atts']
                        order = CreditOrders.objects.filter(order__attendee_id__in=all_attendee, status=status).aggregate(
                            total=Sum(F('cost_including_vat')))
                        return order['total']
                    else:
                        return
        except Exception as ex:
            ErrorR.efail(ex)

    def place_order(event_id, user_id, item_type, item_id, admin_id=None, order_number=None, preselected=False, booking_day_count=1, booking_id=None, new_extra_booking_dates=None):
        item_cost_exists = EconomyLibrary.check_item_cost(item_type, item_id)
        if not item_cost_exists:
            print('Item has no cost')
            return False
        try:
            with transaction.atomic():
                existing_open_order = Orders.objects.filter(attendee_id=user_id, status='open')
                if existing_open_order:
                    order = existing_open_order[0]
                else:
                    if not order_number:
                        order_number = EconomyLibrary.get_next_order_number(event_id, user_id)

                    order = Orders(attendee_id=user_id, order_number=order_number, created_by_id=admin_id, is_preselected=preselected)
                    order.save()
                    activity_msg = 'New order created with order id: {0} and order number: {1}'.format(order.id, order_number)
                    EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, user_id, admin_id)

                item_name = None
                item_cost = 0
                item_vat = 0
                if item_type == 'session':
                    item_object = Session.objects.get(id=item_id)
                    item_name = item_object.name
                    item_cost = item_object.cost
                    item_vat = item_object.vat
                elif item_type == 'hotel':
                    item_object = Room.objects.get(id=item_id)
                    item_name = '{} {}'.format(item_object.hotel.name, item_object.description)
                    item_cost = 0
                    item_vat = 0
                    allotments = RoomAllotment.objects.filter(room_id=item_id, cost__gt=0)
                    if allotments.exists():
                        booking_days = new_extra_booking_dates
                        if not booking_days:
                            booking = Booking.objects.get(id=booking_id)
                            booking_days = [booking.check_in + timedelta(days=n) for n in
                                            range(0, (booking.check_out - booking.check_in).days)]
                        for allotment in allotments:
                            if allotment.available_date in booking_days:
                                item_cost += allotment.get_allotment_cost()
                                if not item_vat:
                                    item_vat = allotment.vat
                    else:
                        item_vat = item_object.vat
                        item_cost = item_object.cost_excluded_vat()
                        if booking_day_count > 1:
                            item_cost *= booking_day_count
                            item_cost = float('{:.2f}'.format(item_cost))

                order_item = OrderItems(order_id=order.id, item_type=item_type, item_id=item_id, cost=item_cost,
                                        rebate_for_item_id=item_id, vat_rate=item_vat, item_booking_id=booking_id, effected_day_count=booking_day_count)
                # rebates_on_item = OrderItems.objects.filter(order_id=order.id, item_type='rebate',
                #                                             rebate_for_item_type=item_type, rebate_for_item_id=item_id)
                rebates_on_item = OrderItems.objects.filter(order__attendee_id=user_id, item_type='rebate', rebate_is_deleted=False, rebate_amount=0,
                                                            rebate_for_item_type=item_type, rebate_for_item_id=item_id)
                if rebates_on_item:
                    rebate_costs = 0
                    rebate_id = None
                    for rebate in rebates_on_item:
                        rebate_value = rebate.get_rebate_amount(item_cost)
                        rebate_costs += rebate_value
                        rebate_id = rebate.item_id
                        # this two fields need to update because
                        # this open order could be turn from pending to open, where rebate_item
                        # could have previous different status in applied_on_open_order, rebate_is_deleted
                        rebate.applied_on_open_order = True
                        rebate.rebate_is_deleted = False
                        rebate.rebate_amount = rebate_value
                        if rebate.order_id != order.id:
                            rebate.order_id = order.id
                        rebate.save()

                    order_item.cost -= rebate_costs
                    order_item.rebate_amount = rebate_costs
                    order_item.rebate_id = rebate_id
                    order.rebate_amount += rebate_costs

                order_item.save()
                order.cost += order_item.cost
                order.vat_amount += order_item.get_vat_amount()
                order.save()
                activity_message = 'New order item {0} added to order number: {1}'.format(item_name, order.order_number)
                EconomyLibrary.add_economy_log('register', 'order_item', event_id, activity_message, user_id, admin_id)
                return {'order_id': order.id, 'order_number': order.order_number}

        except Exception as ex:
            ErrorR.efail(ex)

    def check_item_cost(item_type, item_id):
        try:
            if item_type == 'session':
                session = Session.objects.get(id=item_id)
                if session.cost and session.cost > 0:
                    return True
                else:
                    print('{} has no cost'.format(session.name))
                    return False
            elif item_type == 'hotel':
                allotments = RoomAllotment.objects.filter(room_id=item_id, cost__gt=0)
                if allotments.exists():
                    return True
                room_object = Room.objects.filter(id=item_id, cost__gt=0)
                if room_object.exists():
                    return True
                return False
            elif item_type == 'travel':
                return False

        except Exception as ex:
            ErrorR.efail(ex)

    def update_order_number_for_group_reg(owner_id):
        """In group registration, group is created after making hotel reservation, which cause different order_number
        for open orders. This method will sync them into a same order_number"""
        try:
            group_info = EconomyLibrary.get_group_registration_info(owner_id)
            if group_info['group-attendee']:
                group_open_orders = Orders.objects.filter(attendee_id__in=group_info['grp-atts'], status='open')
                if group_open_orders:
                    min_order_number = group_open_orders.aggregate(min_order_number=Min('order_number'))['min_order_number']
                    group_open_orders.update(order_number=min_order_number)
        except Exception as ex:
            ErrorR.efail(ex)

    def update_hotel_cost(event_id, user_id, room_id, booking_day_count, day_count_difference, item_booking_id, new_booking_id=None, new_extra_booking_dates=None, admin_id=None):
        order_items = OrderItems.objects.filter(order__attendee_id=user_id, item_type='hotel', item_id=room_id,
                                                item_booking_id=item_booking_id, rebate_is_deleted=False).order_by('order__status')
        if order_items.exists():
            place_order = False
            order_item = order_items.first()
            if order_item.order.status == 'open':
                # print('phase 1')
                delete_open_order_item_flag = False
                if order_items.count() == 1:
                    # print('phase 2')
                    # only an open order exist for this booking
                    delete_open_order_item_flag = True
                    place_order = True
                else:
                    # print('phase 3')
                    # multiple order exists [open and pending/paid]
                    open_order_day_count = order_items.get(order__status='open').effected_day_count
                    pending_paid_day_filter = order_items.filter(order__status__in=['pending', 'paid']).aggregate(Sum('effected_day_count'))
                    pending_paid_day_count = pending_paid_day_filter['effected_day_count__sum'] if pending_paid_day_filter['effected_day_count__sum'] else 0
                    old_stay_day_count = open_order_day_count + pending_paid_day_count
                    new_extra_day_count = booking_day_count - old_stay_day_count

                    if new_extra_day_count == 0:
                        # print('phase pass')
                        pass
                    elif new_extra_day_count > 0:
                        # print('phase 4')
                        # here booking_day_count is > than total existing day_count
                        # so need to delete existing open_order_item to update by placing new order for new day count
                        booking_day_count = new_extra_day_count + open_order_day_count
                        delete_open_order_item_flag = True
                        place_order = True
                    elif new_extra_day_count < 0:
                        # print('phase 5')
                        # < than 0, which led the system to delete the open order_item and two following possibilities
                        delete_open_order_item_flag = True
                        booking_day_count = new_extra_day_count + open_order_day_count
                        # here new_extra_day_count is negative and open_order_day_count is positive
                        # and if booking_day_count is negative then booking_day_count is the amount of day which will be credited
                        if booking_day_count > 0:
                            # print('phase 6')
                            # if booking_d_count is > than 0, which means still need an open order_item and eff_day_count is booking_day_count
                            place_order = True
                        elif booking_day_count < 0:
                            # print('phase 7')
                            # booking_day_count is < than 0, which means delete open order_item and also make credit order
                            # because less than 0 specifies that the current stay_day_count is less than pending/paid order_item's stay_day_count
                            for oi_item in order_items:
                                # we may have multiple pending/paid order for same booking
                                if booking_day_count == 0:
                                    # when booking_day_count == 0, we shouldn't break the loop because there could have more order and new_booking_id != None
                                    if new_booking_id:
                                        oi_item.item_booking_id = new_booking_id
                                        oi_item.save()
                                        continue

                                if oi_item.order.status in ['pending', 'paid'] and oi_item.effected_day_count > 0:
                                    if oi_item.effected_day_count > abs(booking_day_count):
                                        # print('phase 8')
                                        # here pending/paid order_item has more day_count than reducing_day_count(booking_day_count)
                                        # so, need to reduce create credit order depend on booking_day_count and reduce order_item's eff_day_count
                                        room_object = Room.objects.get(id=oi_item.item_id)
                                        new_cost = 0
                                        allotments = RoomAllotment.objects.filter(room_id=oi_item.item_id, cost__gt=0)
                                        if allotments.exists():
                                            a_booking = Booking.objects.get(id=oi_item.item_booking_id)
                                            a_booking_days = [a_booking.check_in + timedelta(days=n) for n in range(0, (a_booking.check_out - a_booking.check_in).days)]
                                            for allotment in allotments:
                                                if allotment.available_date in a_booking_days:
                                                    new_cost += allotment.get_allotment_cost()
                                        else:
                                            new_cost = room_object.cost_excluded_vat()
                                            if abs(booking_day_count) > 1:
                                                new_cost *= abs(booking_day_count)
                                                new_cost = float('{:.2f}'.format(new_cost))

                                        rebates_on_item = OrderItems.objects.filter(order_id=oi_item.order_id, item_type='rebate', applied_on_open_order=True, rebate_is_deleted=False, rebate_for_item_type='hotel', rebate_for_item_id=oi_item.item_id)
                                        if rebates_on_item:
                                            rebate_cost = 0
                                            for rebate in rebates_on_item:
                                                rebate_cost += rebate.get_rebate_amount(new_cost)
                                            new_cost -= rebate_cost
                                        open_credit_order = CreditOrders.objects.filter(order_id=oi_item.order_id, status='open')
                                        if open_credit_order.exists():
                                            open_credit_order = open_credit_order.first()
                                            old_cost_incl_vat = open_credit_order.cost_including_vat
                                            open_credit_order.cost_excluding_vat += new_cost
                                            open_credit_order.cost_including_vat += new_cost + oi_item.get_rebate_vat_amount(new_cost)
                                            open_credit_order.save()
                                            activity_message = 'Updated the credit order {}'.format(open_credit_order.order_number)
                                            EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                                           admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                                        else:
                                            current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                                            item_name = '{} {}'.format(room_object.hotel.name, room_object.description)
                                            CreditOrders(order_id=oi_item.order_id, order_number=oi_item.order.order_number, cost_excluding_vat=new_cost,
                                                         cost_including_vat=(new_cost + oi_item.get_rebate_vat_amount(new_cost)), type='hotel',
                                                         item_name=item_name, created_by_id=admin_id, invoice_ref=current_invoice_ref).save()
                                            activity_message = 'New credit order created to order: {}'.format(oi_item.order.order_number)
                                            EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id, admin_id)

                                        oi_item.effected_day_count = oi_item.effected_day_count - abs(booking_day_count)
                                        if new_booking_id:
                                            oi_item.item_booking_id = new_booking_id
                                        oi_item.save()
                                        booking_day_count = 0
                                    else:
                                        # print('phase 9')
                                        # here pending/paid order_item's eff_day_count is either equal/less than booking_day_count
                                        # so, need to make order_item cost as credit order
                                        open_credit_order = CreditOrders.objects.filter(order_id=oi_item.order_id, status='open')
                                        if open_credit_order.exists():
                                            open_credit_order = open_credit_order.first()
                                            old_cost_incl_vat = open_credit_order.cost_including_vat
                                            open_credit_order.cost_excluding_vat += oi_item.cost
                                            open_credit_order.cost_including_vat += oi_item.get_total_cost()
                                            open_credit_order.save()
                                            activity_message = 'Updated the credit order {}'.format(open_credit_order.order_number)
                                            EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                                           admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                                        else:
                                            current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                                            CreditOrders(order_id=oi_item.order_id, order_number=oi_item.order.order_number, cost_excluding_vat=oi_item.cost,
                                                         cost_including_vat=oi_item.get_total_cost(), type='hotel',
                                                         item_name=oi_item.get_item_name(), created_by_id=admin_id, invoice_ref=current_invoice_ref).save()
                                            activity_message = 'New credit order created to order: {}'.format(oi_item.order.order_number)
                                            EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id, admin_id)

                                        booking_day_count += oi_item.effected_day_count
                                        oi_item.effected_day_count = 0
                                        oi_item.rebate_is_deleted = True
                                        if new_booking_id:
                                            oi_item.item_booking_id = new_booking_id
                                        oi_item.save()

                if delete_open_order_item_flag:
                    # print('phase delete_order_item')
                    order_item.order.cost -= order_item.cost
                    order_item.order.rebate_amount -= order_item.rebate_amount
                    order_item.order.vat_amount -= order_item.get_vat_amount()
                    order_item.order.save()
                    order_item.delete()

            elif order_item.order.status in ['pending', 'paid']:
                # print('phase 10')
                room_object = Room.objects.get(id=room_id)
                item_name = '{} {}'.format(room_object.hotel.name, room_object.description)
                new_cost = 0
                allotments = RoomAllotment.objects.filter(room_id=room_id, cost__gt=0)
                if allotments.exists():
                    a_booking = Booking.objects.get(id=order_item.item_booking_id)
                    a_booking_days = [a_booking.check_in + timedelta(days=n) for n in
                                      range(0, (a_booking.check_out - a_booking.check_in).days)]
                    for allotment in allotments:
                        if allotment.available_date in a_booking_days:
                            new_cost += allotment.get_allotment_cost()
                else:
                    new_cost = room_object.cost_excluded_vat()
                    if booking_day_count > 1:
                        new_cost *= booking_day_count
                        new_cost = float('{:.2f}'.format(new_cost))

                rebates_on_item = OrderItems.objects.filter(order_id=order_item.order_id, item_type='rebate', applied_on_open_order=True,
                                                            rebate_is_deleted=False, rebate_for_item_type='hotel', rebate_for_item_id=room_id)
                if rebates_on_item:
                    rebate_cost = 0
                    for rebate in rebates_on_item:
                        rebate_cost += rebate.get_rebate_amount(new_cost)
                    new_cost -= rebate_cost
                if day_count_difference > 0:
                    # print('phase 11')
                    # when increase hotel stays, kept day_count_difference =  diff of new and old day_count
                    # couldn't check (new_cost < order_item.cost) because, Ex: 3 day stay initial then keep 2 day, then again keep 3 day
                    # in this example we will find new_cost and order_item.cost equal, because they are pending or paid, to avoid this we use day_count_difference
                    booking_day_count = day_count_difference
                    place_order = True
                if new_cost < order_item.cost and day_count_difference < 1:
                    # print('phase 12')
                    # when reduce hotel stays, kept day_count_difference=0
                    new_cost = order_item.cost - new_cost
                    b = Booking.objects.get(id=order_item.item_booking_id)
                    order_item.effected_day_count = (b.check_out - b.check_in).days
                    if new_booking_id:
                        order_item.item_booking_id = new_booking_id
                    order_item.save()
                    open_credit_order = CreditOrders.objects.filter(order_id=order_item.order_id, status='open')
                    if open_credit_order.exists():
                        open_credit_order = open_credit_order.first()
                        old_cost_incl_vat = open_credit_order.cost_including_vat
                        open_credit_order.cost_excluding_vat += new_cost
                        open_credit_order.cost_including_vat += new_cost + order_item.get_rebate_vat_amount(new_cost)
                        open_credit_order.save()
                        activity_message = 'Updated the credit order {}'.format(open_credit_order.order_number)
                        EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                       admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                    else:
                        current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                        CreditOrders(order_id=order_item.order_id, order_number=order_item.order.order_number, cost_excluding_vat=new_cost,
                                     cost_including_vat=(new_cost + order_item.get_rebate_vat_amount(new_cost)), type='hotel',
                                     item_name=item_name, created_by_id=admin_id, invoice_ref=current_invoice_ref).save()
                        activity_message = 'New credit order created to order: {}'.format(order_item.order.order_number)
                        EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id, admin_id)
            else:
                # print('phase cancel order')
                place_order = True
                print('Order {} is cancelled. Creating new order.'.format(order_item.order.order_number))

            if place_order:
                # print('phase place_order')
                if new_booking_id:
                    item_booking_id = new_booking_id
                EconomyLibrary.place_order(event_id=event_id, user_id=user_id, item_type='hotel', item_id=room_id, booking_day_count=booking_day_count, booking_id=item_booking_id, admin_id=admin_id, new_extra_booking_dates=new_extra_booking_dates)

    def update_hotel_for_allotment(event_id, user_id, room_id, item_booking_id, old_booking_dates, new_booking_dates, admin_id=None):
        """ this method is additional functionality of update_hotel_cost for allotment,
            when day_count is same after updating booking but check_in or check_out is changed,
            where different allotment might have different cost, then we need to update order.
         """
        order_items = OrderItems.objects.filter(order__attendee_id=user_id, item_type='hotel', item_id=room_id,
                                                item_booking_id=item_booking_id, rebate_is_deleted=False).order_by('order__status')
        room_allotments = RoomAllotment.objects.filter(room_id=room_id, cost__gt=0)
        if order_items.exists() and room_allotments.exists():
            order_item = order_items[0]
            newly_added_dates = list(set(new_booking_dates) - set(old_booking_dates))
            removed_dates = list(set(old_booking_dates) - set(new_booking_dates))

            newly_added_dates_allotment = room_allotments.filter(available_date__in=newly_added_dates)
            newly_added_dates_cost = 0
            for a_item in newly_added_dates_allotment:
                newly_added_dates_cost += a_item.get_allotment_cost()

            removed_dates_cost_allotment = room_allotments.filter(available_date__in=removed_dates)
            removed_dates_cost = 0
            for a_item in removed_dates_cost_allotment:
                removed_dates_cost += a_item.get_allotment_cost()

            if newly_added_dates_cost != removed_dates_cost:
                if newly_added_dates_cost > removed_dates_cost:
                    added_cost = newly_added_dates_cost - removed_dates_cost
                    if order_item.order.status == "open":
                        rebates_on_item = OrderItems.objects.filter(order__attendee_id=user_id, item_type='rebate', rebate_for_item_id=room_id,
                                                                    rebate_for_item_type='hotel', rebate_is_deleted=False, applied_on_open_order=True)
                        rebate_amount = 0
                        for rebate in rebates_on_item:
                            if rebate.rebate and rebate.rebate.rebate_type == "percentage":
                                rebate_amount += rebate.rebate.get_rebate_amount(added_cost)

                        added_cost -= rebate_amount
                        order_item.cost += added_cost
                        order_item.save()
                        order_item.order.cost += added_cost
                        order_item.order.vat_amount += order_item.get_rebate_vat_amount(added_cost)
                        order_item.order.save()
                    elif order_item.order.status in ["pending", "paid"]:
                        order_id = None
                        open_order = EconomyLibrary.get_open_order_by_attendee(user_id)
                        if open_order:
                            order_number = open_order.get('order_number')
                            order_id = open_order.get('order_id')
                        else:
                            order_number = EconomyLibrary.get_next_order_number(event_id, user_id)
                        if not order_id:
                            open_order = Orders(attendee_id=user_id, order_number=order_number)
                            open_order.save()
                            order_id = open_order.id
                            activity_msg = 'New order created with order id: {0} and order number: {1}'.format(order_id, order_number)
                            EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, user_id, admin_id)

                        OrderItems(order_id=order_id, cost=added_cost, item_type='adjustment', item_id=0).save()
                        activity_msg = 'New order item adjustment: {0} added to {1} in order: {2} for changing booking allotment dates.'.format(
                            added_cost, order_item.get_item_name(), order_number)
                        EconomyLibrary.add_economy_log('register', 'order_item', event_id, activity_msg, user_id, admin_id)
                        order_to_update = Orders.objects.get(id=order_id)
                        order_to_update.cost += added_cost
                        order_to_update.vat_amount += order_item.get_rebate_vat_amount(added_cost)
                        order_to_update.save()
                else:
                    added_cost = removed_dates_cost - newly_added_dates_cost
                    if order_item.order.status == "open":
                        rebates_on_item = OrderItems.objects.filter(order__attendee_id=user_id, item_type='rebate', rebate_for_item_id=room_id,
                                                                    rebate_for_item_type='hotel', rebate_is_deleted=False, applied_on_open_order=True)
                        rebate_amount = 0
                        for rebate in rebates_on_item:
                            if rebate.rebate and rebate.rebate.rebate_type == "percentage":
                                rebate_amount += rebate.rebate.get_rebate_amount(added_cost)

                        added_cost -= rebate_amount
                        order_item.cost -= added_cost
                        order_item.save()
                        order_item.order.cost -= added_cost
                        order_item.order.vat_amount -= order_item.get_rebate_vat_amount(added_cost)
                        order_item.order.save()
                    elif order_item.order.status in ["pending", "paid"]:
                        open_credit_order = CreditOrders.objects.filter(order_id=order_item.order_id, status='open')
                        if open_credit_order.exists():
                            open_credit_order = open_credit_order.first()
                            old_cost_incl_vat = open_credit_order.cost_including_vat
                            open_credit_order.cost_excluding_vat += added_cost
                            open_credit_order.cost_including_vat += added_cost + order_item.get_rebate_vat_amount(added_cost)
                            open_credit_order.save()
                            activity_message = 'Updated the credit order {0}, for {1} cost: {2} reducing for changing booking allotment.'.format(
                                open_credit_order.order_number, order_item.get_item_name(), added_cost)
                            EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                           admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                        else:
                            current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                            order_number = order_item.order.order_number
                            item_name = '{} cost reduce'.format(order_item.get_item_name())
                            CreditOrders(order_id=order_item.order_id, order_number=order_number, cost_excluding_vat=added_cost,
                                         cost_including_vat=added_cost + order_item.get_rebate_vat_amount(added_cost),
                                         type='adjustment', item_name=item_name, created_by_id=admin_id, invoice_ref=current_invoice_ref).save()
                            activity_message = 'New credit order created to order: {}, for cost: {} reducing in {} for changing booking allotment.'.format(
                                order_number, added_cost, order_item.get_item_name())
                            EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id, admin_id)
        return

    def get_next_order_number(event_id, user_id):
        """ have to check that the user is in group registration or not.
            if does, then the user will share other gruop user's open order's order_number
        """
        order_number = None
        group_reg_info = EconomyLibrary.get_group_registration_info(user_id)
        if group_reg_info['group-attendee']:
            group_attendees = group_reg_info['grp-atts']
            open_orders = Orders.objects.filter(attendee_id__in=group_attendees, status='open').values('order_number')
            if open_orders:
                order_number = open_orders[0]['order_number']

        if not order_number:
            max_number = Orders.objects.filter(attendee__event_id=event_id).aggregate(max_order_number=Max('order_number'))
            checking_existing_order_number = lambda o_n: Payments.objects.filter(order_number=o_n).exists() or Orders.objects.filter(order_number=o_n).exists()
            if max_number['max_order_number']:
                max_order_number_arr = max_number['max_order_number'].split('-')
                if len(max_order_number_arr) > 1:
                    max_order_number = int(max_order_number_arr[1]) + 1
                    full_length_order_number = EconomyLibrary.full_length_order_number(str(max_order_number))
                    order_number = '{}-{}'.format(max_order_number_arr[0], full_length_order_number)
                    while checking_existing_order_number(order_number):
                        print('******* repeated order number *******')
                        max_order_number += 1
                        full_length_order_number = EconomyLibrary.full_length_order_number(str(max_order_number))
                        order_number = '{}-{}'.format(max_order_number_arr[0], full_length_order_number)
                else:
                    order_number = int(max_number['max_order_number']) + 1
                    while checking_existing_order_number(order_number):
                        order_number += 1
            else:
                order_number_setting = Setting.objects.filter(name='start_order_number', event_id=event_id)
                if order_number_setting.exists() and order_number_setting[0].value != '0':
                    max_order_number_arr = order_number_setting[0].value.split('-')
                    if len(max_order_number_arr) > 1:
                        max_order_number = int(max_order_number_arr[1])
                        full_length_order_number = EconomyLibrary.full_length_order_number(str(max_order_number))
                        order_number = '{}-{}'.format(max_order_number_arr[0], full_length_order_number)
                        while checking_existing_order_number(order_number):
                            max_order_number += 1
                            full_length_order_number = EconomyLibrary.full_length_order_number(str(max_order_number))
                            order_number = '{}-{}'.format(max_order_number_arr[0], full_length_order_number)
                    else:
                        order_number = int(order_number_setting[0].value) + 1
                        while checking_existing_order_number(order_number):
                            order_number += 1
                else:
                    order_number = '{}-0000001'.format(event_id)
                    Setting.objects.filter(name='start_order_number', event_id=event_id).delete()
                    Setting(name='start_order_number', value=order_number, event_id=event_id).save()
        return order_number

    def full_length_order_number(order_number):
        if len(order_number) < 7:
            zero_needed = 7 - len(order_number)
            zero_needed_txt = ''
            for i in range(0, zero_needed):
                zero_needed_txt += '0'
            order_number = zero_needed_txt + order_number
        return order_number

    def get_group_registration_info(attendee_id):
        """ This method returns, the attendee is part of group registration and
            attendee ids in both ways [only attendee_id when the attendee isn't part of group]
        """
        result = {'group-attendee': False, 'grp-atts': [attendee_id], 'is_owner': True, 'group_id': None}
        try:
            is_registrationGroupOwner = RegistrationGroupOwner.objects.filter(owner_id=attendee_id)
            if is_registrationGroupOwner:
                group_id = is_registrationGroupOwner[0].group_id
                group_attendees = Attendee.objects.filter(registration_group_id=group_id).values('id')
                group_attendees = [grp_att['id'] for grp_att in group_attendees]
                group_attendees.append(attendee_id)
                result['group-attendee'] = True
                result['grp-atts'] = group_attendees
                result['group_id'] = group_id
            else:
                attendee = Attendee.objects.get(id=attendee_id)
                if attendee.registration_group:
                    group_attendees = Attendee.objects.filter(registration_group_id=attendee.registration_group_id).values(
                        'id')
                    group_attendees = [grp_att['id'] for grp_att in group_attendees]
                    group_owner_id = RegistrationGroupOwner.objects.get(group_id=attendee.registration_group_id).owner_id
                    group_attendees.append(group_owner_id)
                    result['group-attendee'] = True
                    result['is_owner'] = False
                    result['grp-atts'] = group_attendees
                    result['group_id'] = attendee.registration_group_id
        except Exception as ex:
            ErrorR.efail(ex)
        return result

    def get_due_date(event_id):
        due_date_setting = Setting.objects.filter(name='due_date', event_id=event_id)
        if due_date_setting:
            due_date = datetime.now() + timedelta(days=int(due_date_setting[0].value))
        else:
            raise Exception('Due date is not set for this event')
        return due_date

    def apply_rebate(user_id, order_id, rebate_id, rebate_item_type=None, rebate_item_id=None, admin_id=None):
        response = {'result': False, 'download_credit_invoice': False}
        try:
            with transaction.atomic():
                rebate = Rebates.objects.get(id=rebate_id)
                rebate_item_types_ids = {'sessions': [], 'rooms': [], 'travels': []}
                if rebate_item_type:
                    # it's for public-front, when rebate_item_type & id is known
                    if rebate_item_type == 'session':
                        rebate_item_types_ids['sessions'].append(rebate_item_id)
                    elif rebate_item_type == 'hotel':
                        rebate_item_types_ids['rooms'].append(rebate_item_id)
                    elif rebate_item_type == 'travel':
                        rebate_item_types_ids['travels'].append(rebate_item_id)
                else:
                    # for admin, when a rebate can be applied to multiple item
                    rebate_item_types_ids = json.loads(rebate.type_id)

                download_applicable = False
                activity_flag = False
                for session_id in rebate_item_types_ids['sessions']:
                    result = EconomyLibrary.apply_individual_rebate(user_id, order_id, rebate, 'session', session_id, admin_id)
                    activity_flag = True if result['result'] else False
                    if result['download_applicable']:
                        download_applicable = True
                for room_id in rebate_item_types_ids['rooms']:
                    result = EconomyLibrary.apply_individual_rebate(user_id, order_id, rebate, 'hotel', room_id, admin_id)
                    activity_flag = True if result['result'] else False
                    if result['download_applicable']:
                        download_applicable = True
                for travel_id in rebate_item_types_ids['travels']:
                    result = EconomyLibrary.apply_individual_rebate(user_id, order_id, rebate, 'travel', travel_id, admin_id)
                    activity_flag = True if result['result'] else False
                    if result['download_applicable']:
                        download_applicable = True

                if activity_flag:
                    order_number = EconomyLibrary.get_order_number(user_id, order_id)
                    activity_message = 'Added rebate {0} to order: {1}'.format(rebate.name, order_number)
                    EconomyLibrary.add_economy_log('register', 'rebate', rebate.event_id, activity_message, user_id, admin_id)

                response['result'] = True
                response['download_credit_invoice'] = download_applicable
        except Exception as ex:
            ErrorR.efail(ex)
        return response

    def apply_individual_rebate(user_id, order_id, rebate, rebate_item_type, rebate_item_id, admin_id=None):
        rebate_exist = OrderItems.objects.filter(item_type='rebate', item_id=rebate.id, rebate_for_item_type=rebate_item_type,
                                                 rebate_for_item_id=rebate_item_id, rebate_is_deleted=False,
                                                 order__attendee_id=user_id)
        # temporary return [need to ask about when rebate is already exists]
        if rebate_exist:
            print('Applied rebate already exists')
            return {'result': True, 'download_applicable': False}

        applied_to = OrderItems.objects.filter(order_id=order_id, order__attendee_id=user_id,
                                               item_type=rebate_item_type, item_id=rebate_item_id)
        order = Orders.objects.get(id=order_id)
        event_id = order.attendee.event_id
        if applied_to:
            applied_item = applied_to[0]
            rebate_amount = rebate.get_rebate_amount(applied_item.cost)
            if order.status == 'open':
                previous_vat_amount = applied_item.get_vat_amount()
                applied_item.cost -= rebate_amount
                applied_item.rebate_amount += rebate_amount
                applied_item.rebate_id = rebate.id
                applied_item.save()

                order.cost -= rebate_amount
                order.rebate_amount += rebate_amount
                order.vat_amount -= (previous_vat_amount - applied_item.get_vat_amount())
                order.save()

                OrderItems(order_id=order_id, item_type='rebate', cost=rebate.value, item_id=rebate.id,
                           rebate_amount=rebate_amount,
                           rebate_for_item_id=rebate_item_id, rebate_for_item_type=rebate_item_type).save()

            elif order.status in ['pending', 'paid']:
                cost_including_vat = applied_item.get_rebate_vat_amount(rebate_amount) + rebate_amount
                open_credit_order = CreditOrders.objects.filter(order_id=order_id, status='open')
                if open_credit_order:
                    open_credit_order = open_credit_order[0]
                    old_cost_incl_vat = open_credit_order.cost_including_vat

                    open_credit_order.cost_excluding_vat += rebate_amount
                    open_credit_order.cost_including_vat += cost_including_vat
                    open_credit_order.save()

                    activity_message = 'Updated the credit order {}'.format(open_credit_order.order_number)
                    EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                   admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                else:
                    current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                    CreditOrders(order_id=order_id, order_number=order.order_number, cost_excluding_vat=rebate_amount,
                                 cost_including_vat=cost_including_vat, type='rebate',
                                 item_name=rebate.name, created_by_id=admin_id,invoice_ref=current_invoice_ref).save()
                    activity_message = 'New credit order created to order: {}'.format(order.order_number)
                    EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id, admin_id)

                OrderItems(order_id=order_id, item_type='rebate', cost=rebate.value, item_id=rebate.id,
                           rebate_amount=rebate_amount, rebate_for_item_id=rebate_item_id,
                           rebate_for_item_type=rebate_item_type, applied_on_open_order=False).save()

        else:
            applied_on_open_order = True
            if order.status in ['pending', 'paid']:
                applied_on_open_order = False

            OrderItems(order_id=order_id, item_type='rebate', cost=rebate.value, item_id=rebate.id,
                       rebate_for_item_id=rebate_item_id, rebate_for_item_type=rebate_item_type,
                       applied_on_open_order=applied_on_open_order).save()

        activity_message = 'New order item {0} added to order: {1}'.format(rebate.name, order.order_number)
        EconomyLibrary.add_economy_log('register', 'order_item', event_id, activity_message, user_id, admin_id)
        return {'result': True, 'download_applicable': len(applied_to) > 0 and order.status in ['pending', 'paid']}

    def remove_item_from_order(event_id, user_id, order_id, item_id, booking_id=None, admin_id=None, booking_allotment_dates=None):
        response = {'result': False, 'download_applicable': False}
        try:
            # this checking for hotel, where same hotel booking can have multiple orders(open, pending/paid)
            item_type_and_booking_id = OrderItems.objects.filter(order_id=order_id, item_id=item_id)
            if item_type_and_booking_id and item_type_and_booking_id[0].item_type == 'hotel':
                order_item_list = OrderItems.objects.filter(item_id=item_id, order__attendee_id=user_id, item_booking_id=booking_id)
            else:
                order_item_list = OrderItems.objects.filter(order_id=order_id, item_id=item_id)

            with transaction.atomic():
                download_applicable = False
                for order_item in order_item_list:
                    order = Orders.objects.get(id=order_item.order_id)
                    if order.status == 'open':
                        order.cost -= order_item.cost
                        order.rebate_amount -= order_item.rebate_amount
                        order.vat_amount -= order_item.get_vat_amount()
                        order.save()
                        applied_rebate_items = OrderItems.objects.filter(order_id=order_item.order_id, item_type='rebate',
                                                                         rebate_for_item_type=order_item.item_type,
                                                                         rebate_for_item_id=order_item.item_id)
                        for applied_rebate_item in applied_rebate_items:
                            applied_rebate_item.rebate_amount = 0
                            applied_rebate_item.save()

                        activity_message = 'Order Item {0} is removed from order: {1}'.format(order_item.get_item_name(), order.order_number)
                        EconomyLibrary.add_economy_log('delete', 'order_item', event_id, activity_message, user_id, admin_id)
                        order_item.delete()
                        order_item_count = OrderItems.objects.filter(order_id=order.id).count()
                        if order_item_count == 0:
                            order.delete()

                    elif order.status in ['pending', 'paid']:
                        rebate_item_list = OrderItems.objects.filter(order_id=order_item.order_id, item_type='rebate',
                                                                     rebate_for_item_type=order_item.item_type, rebate_for_item_id=order_item.item_id)

                        if order_item.item_type == 'hotel':
                            credit_value = 0
                            booking_allotments = RoomAllotment.objects.filter(room_id=item_id, available_date__in=booking_allotment_dates)
                            if booking_allotments.exists():
                                allotment_vat_rate = None
                                for allotment in booking_allotments:
                                    credit_value += allotment.get_allotment_cost()
                                    if not allotment_vat_rate:
                                        allotment_vat_rate = allotment.vat

                                credit_value_incl_vat = credit_value + ((credit_value * allotment_vat_rate) / 100)
                            else:
                                # if hotel item then we have to check make credit depend on effected_day_count
                                # that's why we need to get effected_day_count cost for the order_item
                                room = Room.objects.get(id=order_item.item_id)
                                credit_value = room.cost_excluded_vat()
                                room_vat_amount = room.get_vat_amount()
                                if order_item.effected_day_count > 1:
                                    credit_value *= order_item.effected_day_count
                                    credit_value = float('{:.2f}'.format(credit_value))
                                    credit_value_incl_vat = (room_vat_amount * order_item.effected_day_count) + credit_value
                                else:
                                    credit_value_incl_vat = room_vat_amount + credit_value

                            credit_value_incl_vat = float('{:.2f}'.format(credit_value_incl_vat))
                            for rebate_item in rebate_item_list:
                                if not rebate_item.applied_on_open_order and not rebate_item.rebate_is_deleted:
                                    rebate_amount = rebate_item.get_rebate_amount(credit_value)
                                    credit_value = credit_value - rebate_amount
                                    credit_value_incl_vat -= rebate_amount - order_item.get_rebate_vat_amount(rebate_amount)
                                elif rebate_item.applied_on_open_order and rebate_item.rebate_is_deleted:
                                    rebate_amount = rebate_item.get_rebate_amount(credit_value)
                                    credit_value += rebate_amount
                                    credit_value_incl_vat += rebate_amount + order_item.get_rebate_vat_amount(rebate_amount)
                        else:
                            credit_value = order_item.cost
                            credit_value_incl_vat = order_item.get_total_cost()
                            for rebate_item in rebate_item_list:
                                if not rebate_item.applied_on_open_order and not rebate_item.rebate_is_deleted:
                                    credit_value -= rebate_item.rebate_amount
                                    credit_value_incl_vat -= rebate_item.rebate_amount - order_item.get_rebate_vat_amount(rebate_item.rebate_amount)
                                elif rebate_item.applied_on_open_order and rebate_item.rebate_is_deleted:
                                    credit_value += rebate_item.rebate_amount
                                    credit_value_incl_vat += rebate_item.rebate_amount + order_item.get_rebate_vat_amount(rebate_item.rebate_amount)

                        open_credit_order = CreditOrders.objects.filter(order_id=order_item.order_id, status='open')
                        if open_credit_order.exists():
                            open_credit_order = open_credit_order.first()
                            old_cost_incl_vat = open_credit_order.cost_including_vat

                            open_credit_order.cost_excluding_vat += credit_value
                            open_credit_order.cost_including_vat += credit_value_incl_vat

                            open_credit_order.save()
                            activity_message = 'Updated the credit order: {}'.format(open_credit_order.order_number)
                            EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                           admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                        else:
                            current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                            CreditOrders(order_id=order_item.order_id, order_number=order.order_number, cost_excluding_vat=credit_value,
                                         cost_including_vat=credit_value_incl_vat, type=order_item.item_type,
                                         item_name=order_item.get_item_name(), created_by_id=admin_id, invoice_ref=current_invoice_ref).save()

                            activity_message = 'New credit order created to order: {}'.format(order_item.order.order_number)
                            EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id,
                                                           admin_id)
                        order_item.rebate_is_deleted = True
                        if order_item.item_type == 'hotel':
                            order_item.effected_day_count = 0
                        order_item.save()
                        download_applicable = True

                    response['result'] = True
                    response['download_applicable'] = download_applicable

        except Exception as ex:
            ErrorR.efail(ex)
        return response

    def remove_rebate_from_order(order_id, user_id, rebate_id, rebate_for_item_type, rebate_for_item_id, event_id, admin_id):
        try:
            with transaction.atomic():
                order_rebate_item = OrderItems.objects.filter(order_id=order_id, item_id=rebate_id, rebate_is_deleted=False,
                                                              rebate_for_item_type=rebate_for_item_type,
                                                              rebate_for_item_id=rebate_for_item_id)
                rebate = Rebates.objects.get(id=rebate_id)
                if order_rebate_item.exists():
                    order_rebate_item = order_rebate_item[0]
                    order_number_for_activity = order_rebate_item.order.order_number
                    rebate_affected_item = OrderItems.objects.filter(order_id=order_id, item_type=rebate_for_item_type,
                                                                     item_id=rebate_for_item_id)
                    if rebate_affected_item:
                        rebate_affected_item = rebate_affected_item[0]

                        if rebate_affected_item.order.status == 'open':
                            rebate_affected_item.cost += order_rebate_item.rebate_amount
                            rebate_affected_item.rebate_amount -= order_rebate_item.rebate_amount
                            rebate_affected_item.rebate = None
                            rebate_affected_item.save()

                            rebate_affected_item.order.cost += order_rebate_item.rebate_amount
                            rebate_affected_item.order.rebate_amount -= order_rebate_item.rebate_amount
                            rebate_affected_item.order.vat_amount += rebate_affected_item.get_rebate_vat_amount(
                                order_rebate_item.rebate_amount)
                            rebate_affected_item.order.save()
                            order_rebate_item.delete()

                        elif rebate_affected_item.order.status in ['pending', 'paid']:
                            order_rebate_item.rebate_is_deleted = True
                            order_rebate_item.save()
                            if order_rebate_item.rebate_amount > 0:
                                open_order = Orders.objects.filter(attendee_id=user_id, status='open')
                                if open_order:
                                    order = open_order[0]
                                else:
                                    order_number = EconomyLibrary.get_next_order_number(event_id, user_id)
                                    order = Orders(attendee_id=user_id, order_number=order_number, created_by_id=admin_id)
                                    order.save()
                                    activity_msg = 'New order created with order id: {0} and order number: {1}'.format(order.id,
                                                                                                                       order_number)
                                    EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, user_id,
                                                                   admin_id)

                                order_cost_incl_vat = order_rebate_item.rebate_amount + (
                                    rebate_affected_item.get_rebate_vat_amount(order_rebate_item.rebate_amount))
                                OrderItems(order_id=order.id, item_type='adjustment', item_id=0,
                                           cost=order_cost_incl_vat, rebate_id=order_rebate_item.item_id).save()
                                order.cost += order_cost_incl_vat
                                order.save()
                                activity_msg = 'New order item as adjustment for rebate {0} added to order: {1}'.format(
                                    rebate.name, order.order_number)
                                EconomyLibrary.add_economy_log('register', 'order_item', event_id, activity_msg, user_id,
                                                               admin_id)
                    else:
                        order_rebate_item.delete()

                    activity_msg = 'Removed rebate {0} from order: {1}'.format(rebate.name, order_number_for_activity)
                    EconomyLibrary.add_economy_log('delete', 'rebate', event_id, activity_msg, user_id, admin_id)

                    return True
        except Exception as ex:
            ErrorR.efail(ex)

    def get_order_id(user_id, item_type, item_id, booking_id=None):
        order_item = OrderItems.objects.filter(order__attendee_id=user_id, item_type=item_type, item_id=item_id,
                                               rebate_is_deleted=False, item_booking_id=booking_id).values('order_id', 'order__order_number')
        if order_item:
            return {
                'order_id': order_item[0]['order_id'],
                'order_number': order_item[0]['order__order_number']
            }
        else:
            return False

    def get_order_number(user_id, order_id):
        order = Orders.objects.filter(id=order_id, attendee_id=user_id).values('order_number')
        if order:
            return order[0]['order_number']
        else:
            return False

    def get_open_order_by_attendee(user_id):
        group_info = EconomyLibrary.get_group_registration_info(user_id)
        order = Orders.objects.filter(attendee_id__in=group_info['grp-atts'], status='open', cost__gt=0).values('id', 'order_number', 'status', 'due_date', 'attendee_id')
        order_id = ''
        for o_item in order:
            if user_id == o_item['attendee_id']:
                order_id = o_item['id']
        if order.exists():
            return {
                'order_id': order_id,
                'order_number': order[0]['order_number'],
                'status': order[0]['status'],
                'due_date': order[0]['due_date']
            }
        else:
            return False

    def create_order_for_rebate(event_id, attendee_id, order_number=None):
        if order_number:
            order_checking = Orders.objects.filter(order_number=order_number).first()
            if order_checking and order_checking.status != 'open':
                order_number = None

        if not order_number:
            group_info = EconomyLibrary.get_group_registration_info(attendee_id)
            open_orders = Orders.objects.filter(attendee_id__in=group_info['grp-atts'], status='open').values('order_number')
            if open_orders.exists():
                order_number = open_orders[0]['order_number']
            else:
                order_number = EconomyLibrary.get_next_order_number(event_id, attendee_id)

        order = Orders(attendee_id=attendee_id, order_number=order_number)
        order.save()
        # activity_msg = 'New order created with order id: {0} and order number: {1}'.format(order.id, order_number)
        # EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, attendee_id, None)
        return dict(id=order.id, order_number=order_number)

    def delete_empty_order(order_id):
        item_count = OrderItems.objects.filter(order_id=order_id).count()
        if item_count == 0:
            Orders.objects.filter(id=order_id, status='open').delete()
        return

    def get_total_payable_amount_for_order(order_number):
        order = Orders.objects.filter(order_number=order_number).aggregate(total=Sum(F('cost') + F('vat_amount')))
        credit = CreditUsages.objects.filter(order_number=order_number).aggregate(total=Sum(F('cost')))
        if credit['total'] != None:
            total_amount = order['total'] - credit['total']
        else:
            total_amount = order['total']

        return total_amount

    def change_order_status(order_number, status, event_id, attendee_id, admin_id=None):
        try:
            with transaction.atomic():
                due_date = ''
                found_all_paid = False
                orders = Orders.objects.filter(order_number=order_number, attendee__event_id=event_id).exclude(status=status)
                if not orders.exists() or EconomyLibrary.status_change_eligibility(orders[0].status, status):
                    return {
                        'status_changed': False,
                        'order_number': order_number,
                        'status': status,
                        'due_date': '',
                        'amount_due': ''

                    }
                if status == 'pending':
                    if orders[0].status == 'paid':
                        # this part is added when 22-06-2018, for task admin can change status from paid to pending
                        # need change order status, add activity history and delete payment records
                        for order in orders:
                            activity_message = "Changed the order status of order: {}".format(order_number)
                            EconomyLibrary.add_economy_log('update', 'order', event_id, activity_message, order.attendee.id,
                                                           admin_id, status, 'paid')

                        orders.update(status=status)
                        Payments.objects.filter(order_number=order_number).delete()
                        return dict(status_changed=True, status=status)
                    else:
                        due_date = EconomyLibrary.get_due_date(event_id)
                        current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                        invoice_date = datetime.now()
                        form = {
                            'invoice_ref': current_invoice_ref,
                            'invoice_date': invoice_date
                        }
                        orders.update(**form)
                        order_total_amount = EconomyLibrary.get_total_payable_amount_for_order(order_number)
                        group_reg_info = EconomyLibrary.get_group_registration_info(attendee_id)
                        group_attendees = group_reg_info['grp-atts']
                elif status == 'paid' and orders[0].status == 'open':
                    current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                    form = {
                        'due_date': EconomyLibrary.get_due_date(event_id),
                        'invoice_ref': current_invoice_ref,
                        'invoice_date': datetime.now()
                    }
                    orders.update(**form)
                elif status == 'cancelled':
                    CreditOrders.objects.filter(order_number=order_number).update(status='cancelled')

                for order in orders:
                    if found_all_paid:
                        break

                    if status == 'pending':
                        order.due_date = due_date
                        EconomyLibrary.set_order_item_booking_dates(order.id)
                    elif status == 'paid':
                        # for status==paid, we need just total_amount, not excluding credit_order_values
                        order_total_amount = Orders.objects.filter(order_number=order_number).aggregate(
                            total=Sum(F('cost') + F('vat_amount')))
                        EconomyLibrary.make_order_paid(order_number, order_total_amount['total'], None, 'admin', '', order.status, admin_id)
                        break

                    old_status = order.status
                    order.status = status
                    order.save()
                    activity_message = "Changed the order status of order: {}".format(order_number)
                    EconomyLibrary.add_economy_log('update', 'order', event_id, activity_message, order.attendee.id, admin_id,
                                                   status, old_status)
                    if status == 'pending':
                        credit_needed = order.get_total_cost()
                        credit_orders = CreditOrders.objects.filter(order__attendee__in=group_attendees, status='open',
                                                                    cost_including_vat__gt=0).order_by(
                            '-cost_including_vat')
                        for credit_order in credit_orders:
                            if credit_order.cost_including_vat < credit_needed:
                                credit_needed -= credit_order.cost_including_vat
                                CreditUsages(order_number=order_number, credit_order_id=credit_order.id,
                                             cost=credit_order.cost_including_vat).save()
                                activity_message = '-{0} from Credit Order ({1}) used to Order: {2}'.format(
                                    credit_order.cost_including_vat,
                                    credit_order.order_number,
                                    order.order_number)
                                EconomyLibrary.add_economy_log('register', 'credit_usage', event_id, activity_message,
                                                               order.attendee_id, admin_id)

                                credit_order.cost_excluding_vat = 0
                                credit_order.cost_including_vat = 0
                                credit_order.status = 'paid'
                                credit_order.save()
                                activity_message = "Changed the credit order status of order: {}".format(order_number)
                                EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message,
                                                               order.attendee.id,
                                                               admin_id, credit_order.status, 'open')
                            elif credit_order.cost_including_vat == credit_needed:
                                CreditUsages(order_number=order_number, credit_order_id=credit_order.id,
                                             cost=credit_order.cost_including_vat).save()
                                activity_message = '-{0} from Credit Order ({1}) used to Order: {2}'.format(
                                    credit_order.cost_including_vat, credit_order.order_number, order.order_number)
                                EconomyLibrary.add_economy_log('register', 'credit_usage', event_id, activity_message,
                                                               order.attendee_id, admin_id)

                                credit_order.cost_excluding_vat = 0
                                credit_order.cost_including_vat = 0
                                credit_order.status = 'paid'
                                credit_order.save()
                                activity_message = "Changed the credit order status of order: {}".format(order_number)
                                EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message,
                                                               order.attendee.id, admin_id, credit_order.status, 'open')

                                total_payable_remaining_amount = EconomyLibrary.get_total_payable_amount_for_order(order_number)
                                if total_payable_remaining_amount == 0:
                                    EconomyLibrary.make_order_paid(order_number, order_total_amount, None, 'admin', '', old_status, admin_id)
                                    found_all_paid = True
                                break
                            elif credit_order.cost_including_vat > credit_needed:
                                CreditUsages(order_number=order_number, credit_order_id=credit_order.id,
                                             cost=credit_needed).save()
                                activity_message = '-{0} from Credit Order ({1}) used to Order: {2}'.format(credit_needed,
                                                                                                            credit_order.order_number,
                                                                                                            order.order_number)
                                EconomyLibrary.add_economy_log('register', 'credit_usage', event_id, activity_message,
                                                               order.attendee_id, admin_id)

                                old_cost_incl_vat = credit_order.cost_including_vat
                                amount_reduce_to_cost_excl_vat = math.ceil((credit_order.cost_excluding_vat * credit_needed) / credit_order.cost_including_vat)
                                credit_order.cost_excluding_vat -= amount_reduce_to_cost_excl_vat
                                credit_order.cost_including_vat -= credit_needed
                                credit_order.save()
                                activity_message = 'Updated the credit order: {}'.format(credit_order.order_number)
                                EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message,
                                                               order.attendee_id, admin_id, credit_order.cost_including_vat,
                                                               old_cost_incl_vat)
                                total_payable_remaining_amount = EconomyLibrary.get_total_payable_amount_for_order(order_number)
                                if total_payable_remaining_amount == 0:
                                    EconomyLibrary.make_order_paid(order_number, order_total_amount, None, 'admin', '', old_status,
                                                                   admin_id)
                                    found_all_paid = True
                                break

                result = {
                    'status_changed': True,
                    'order_number': order_number,
                    'status': 'paid' if found_all_paid else status,
                    'due_date': str(due_date)[:10]
                }
                if status == 'paid' or found_all_paid:
                    result['amount_due'] = 0
                else:
                    result['amount_due'] = EconomyLibrary.get_total_payable_amount_for_order(order_number)
                return result

        except Exception as ex:
            ErrorR.efail(ex)

    def status_change_eligibility(old_status, new_status):
        if old_status == 'pending':
            if new_status == 'open':
                return True
        elif old_status == 'paid':
            if new_status not in ['cancelled', 'pending']:
                return True
        elif old_status == 'cancelled':
                return True

    @transaction.atomic
    def make_order_paid(order_number, amount, transaction, payment_type, details, old_status, admin_id=None):
        orders = Orders.objects.filter(order_number=order_number)
        for order in orders:
            order.status = 'paid'
            order.save()
            EconomyLibrary.set_order_item_booking_dates(order.id)
            activity_message = "Changed the order status of order: {}".format(order_number)
            EconomyLibrary.add_economy_log('update', 'order', order.attendee.event_id, activity_message,
                                           order.attendee_id, admin_id, 'paid', old_status)
            activity_message = 'Payment successfully made for order: {}'.format(order.order_number)
            EconomyLibrary.add_economy_log('register', 'payment', order.attendee.event_id, activity_message,
                                           order.attendee_id, admin_id)

        if admin_id and transaction is None:
            now = time.time()
            timestamp = str(now).replace(".", "")
            transaction = str(order_number) + "-" + timestamp

        current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
        Payments(order_number=order_number, method=payment_type, amount=amount, details=details,
                 transaction=transaction, created_by_id=admin_id,invoice_ref=current_invoice_ref).save()
        return

    def get_credit_usage_payment(order_number):
        credit_usage_list = []
        total_amount = 0
        try:
            credit_usages = CreditUsages.objects.filter(order_number=order_number)
            for credit_usage in credit_usages:
                credit_usage_list.append({
                    'name': 'Credit from {}'.format(credit_usage.credit_order.order_number),
                    'cost': credit_usage.cost
                })
                total_amount += credit_usage.cost
        except Exception as ex:
            ErrorR.efail(ex)
        return {'credit_usage': credit_usage_list, 'total_amount': total_amount}

    def get_receipt_data(event_id, attendee_id, order_number=None):
        receipt_list = []
        try:
            if order_number:
                paid_orders = [{'order_number': order_number}]
            else:
                paid_orders = Orders.objects.filter(attendee_id=attendee_id, status='paid').values('order_number')

            for order in paid_orders:
                context = {}
                order_info = EconomyLibrary.get_order_tables(attendee_id, event_id, True, order['order_number'])
                context['order_table_type'] = order_info['order_type']
                if order_info['order_type'] == 'group-order':
                    context['orders'] = EconomyLibrary.get_group_order_single_table(order_info['order_list'])
                else:
                    context['orders'] = order_info['order_list']
                context['payment'] = EconomyLibrary.get_payment_info(order['order_number'])
                receipt_list.append(context)
        except Exception as ex:
            ErrorR.efail(ex)
        return receipt_list

    def get_payment_info(order_number):
        try:
            payment = Payments.objects.filter(order_number=order_number)
            if payment:
                payment = payment[0]
                if len(payment.details) > 0:
                    payment.details = json.loads(payment.details)
                return payment
        except Exception as ex:
            ErrorR.efail(ex)

    def add_economy_log(activity_type, category, event_id, activity_message, attendee_id, admin_id=None, new_value='',
                        old_value=''):
        try:
            activity = ActivityHistory(attendee_id=attendee_id, admin_id=admin_id, category=category,
                                       activity_type=activity_type, activity_message=activity_message, new_value=new_value,
                                       old_value=old_value, event_id=event_id)
            activity.save()
        except Exception as ex:
            ErrorR.efail(ex)

    def get_event_currency(language_id):
        response = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_currency'])
        return response['langkey']['economy_txt_currency']

    def get_status_from_lang(language_id, status):
        status_lang = status
        if status == 'open':
            status_lang = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_status_open'])['langkey']['economy_txt_status_open']
        elif status == 'pending':
            status_lang = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_status_pending'])['langkey']['economy_txt_status_pending']
        elif status == 'paid':
            status_lang = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_status_paid'])['langkey']['economy_txt_status_paid']
        elif status == 'cancelled':
            status_lang = LanguageH.catch_lang_key_multiple(language_id, 'economy', ['economy_txt_status_cancelled'])['langkey']['economy_txt_status_cancelled']
        return status_lang

    def get_invoice_next_ref_id(value=None):
        current_invoice_ref_object = Setting.objects.filter(name='current_invoice_ref')
        if current_invoice_ref_object:
            current_invoice_ref_object = current_invoice_ref_object[0]
            current_invoice_ref = int(current_invoice_ref_object.value) + 1
            current_invoice_ref_object.value = str(current_invoice_ref)
            current_invoice_ref_object.save()
        else:
            current_invoice_ref = 1000001
            Setting(name='current_invoice_ref', event_id=1, value=str(current_invoice_ref)).save()

        return current_invoice_ref

    def get_group_owner_open_credit_order(attendee_id, order_number, event_id, admin_id):
        """ here attendee_id must be group member attendee ,
            this method returns attendee group owner's a open credit order"""
        open_credit_order = None
        try:
            attendee = Attendee.objects.get(id=attendee_id)
            if attendee.registration_group:
                group_owner_id = RegistrationGroupOwner.objects.get(group_id=attendee.registration_group_id).owner_id
                open_credit_order = CreditOrders.objects.filter(order__attendee_id=group_owner_id, order_number=order_number, status='open').first()
                if not open_credit_order:
                    owner_order = Orders.objects.filter(attendee_id=group_owner_id, order_number=order_number, status__in=['pending', 'paid']).first()
                    if not owner_order:
                        deleted_attendee_order = Orders.objects.get(attendee_id=attendee_id, order_number=order_number)
                        owner_order = Orders(attendee_id=group_owner_id, order_number=order_number, status=deleted_attendee_order.status, due_date=deleted_attendee_order.due_date,
                                             invoice_ref=deleted_attendee_order.invoice_ref, invoice_date=deleted_attendee_order.invoice_date, created_by_id=admin_id)
                        owner_order.save()
                        activity_msg = 'New order created with order id: {0} and order number: {1} with cost 0. Credit order needs an order.'.format(owner_order.id, order_number)
                        EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, group_owner_id, admin_id)

                    open_credit_order = CreditOrders(order_id=owner_order.id, order_number=order_number, cost_excluding_vat=0,
                                                     cost_including_vat=0, type='adjustment', item_name='credit order', created_by_id=admin_id)
                    open_credit_order.save()
                    activity_message = "New credit order created to order: {} with cost 0. Credit order is needed to keep removed/deleted group member attendee's order cost.".format(order_number)
                    EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, group_owner_id, admin_id)
        except Exception as ex:
            ErrorR.efail(ex)
        return open_credit_order

    def set_order_item_booking_dates(order_id):
        order_items = OrderItems.objects.filter(order_id=order_id, item_type='hotel')
        for item in order_items:
            if not item.booking_check_in:
                try:
                    booking = Booking.objects.get(id=item.item_booking_id, attendee_id=item.order.attendee_id)
                    item.booking_check_in = booking.check_in
                    item.booking_check_out = booking.check_out
                    item.save()
                except Exception as exp:
                    ErrorR.efail(exp)
                    print('Exception, because to get booking check-in and check-out, but booking is already deleted.')

    def admin_change_order_item_cost(order_item_id, new_cost, event_id, admin_id=None):
        result = dict(success=False, canceled_order=False, message="Something wrong!")
        try:
            order_item = OrderItems.objects.get(id=order_item_id)
            user_id = order_item.order.attendee_id
            if order_item.cost != new_cost:
                result['success'] = True
                result['message'] = "Cost updated."
                old_cost = order_item.cost
                if order_item.order.status == 'open':
                    order_item.order.vat_amount -= order_item.get_vat_amount()
                    if new_cost > order_item.cost:
                        order_item.order.cost += new_cost - order_item.cost
                    else:
                        order_item.order.cost -= order_item.cost - new_cost

                    order_item.cost = new_cost
                    order_item.save()
                    order_item.order.vat_amount += order_item.get_vat_amount()
                    order_item.order.save()
                    activity_message = "updated {} cost for order {}.".format(order_item.get_item_name(), order_item.order.order_number)
                    EconomyLibrary.add_economy_log('update', 'order_item', event_id, activity_message, user_id, admin_id, new_cost, old_cost)
                elif order_item.order.status in ['pending', 'paid']:
                    if new_cost > old_cost:
                        order_id = None
                        open_order = EconomyLibrary.get_open_order_by_attendee(user_id)
                        if open_order:
                            order_number = open_order.get('order_number')
                            order_id = open_order.get('order_id')
                        else:
                            order_number = EconomyLibrary.get_next_order_number(event_id, user_id)
                        if not order_id:
                            open_order = Orders(attendee_id=user_id, order_number=order_number)
                            open_order.save()
                            order_id = open_order.id
                            activity_msg = 'New order created with order id: {0} and order number: {1}'.format(order_id, order_number)
                            EconomyLibrary.add_economy_log('register', 'order', event_id, activity_msg, user_id, admin_id)

                        applicable_cost = new_cost - old_cost
                        OrderItems(order_id=order_id, cost=applicable_cost, item_type='adjustment', item_id=0).save()
                        activity_msg = 'New order item adjustment: {0} added to {1} in order: {2}'.format(applicable_cost, order_item.get_item_name(), order_number)
                        EconomyLibrary.add_economy_log('register', 'order_item', event_id, activity_msg, user_id, admin_id)
                        order_to_update = Orders.objects.get(id=order_id)
                        order_to_update.cost += applicable_cost
                        order_to_update.save()
                    else:
                        open_credit_order = CreditOrders.objects.filter(order_id=order_item.order_id, status='open')
                        applicable_cost = old_cost - new_cost
                        if open_credit_order.exists():
                            open_credit_order = open_credit_order.first()
                            old_cost_incl_vat = open_credit_order.cost_including_vat
                            open_credit_order.cost_excluding_vat += applicable_cost
                            open_credit_order.cost_including_vat += applicable_cost
                            open_credit_order.save()
                            activity_message = 'Updated the credit order {0}, for {1} cost: {2} reducing.'.format(
                                open_credit_order.order_number, order_item.get_item_name(), applicable_cost)
                            EconomyLibrary.add_economy_log('update', 'credit_order', event_id, activity_message, user_id,
                                                           admin_id, open_credit_order.cost_including_vat, old_cost_incl_vat)
                        else:
                            current_invoice_ref = EconomyLibrary.get_invoice_next_ref_id()
                            order_number = order_item.order.order_number
                            item_name = '{} cost reduce'.format(order_item.get_item_name())
                            CreditOrders(order_id=order_item.order_id, order_number=order_number, cost_excluding_vat=applicable_cost, cost_including_vat=applicable_cost,
                                         type='adjustment', item_name=item_name, created_by_id=admin_id, invoice_ref=current_invoice_ref).save()
                            activity_message = 'New credit order created to order: {}, for cost: {} reducing in {}'.format(order_number, applicable_cost, order_item.get_item_name())
                            EconomyLibrary.add_economy_log('register', 'credit_order', event_id, activity_message, user_id, admin_id)
                else:
                    result['canceled_order'] = True
                    result['message'] = "Operation can't be applied to canceled order."
        except Exception as ex:
            result['success'] = False
            result['message'] = 'Something wrong!'
            ErrorR.efail(ex)
        return result
