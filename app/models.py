from django.db import models
from datetime import datetime, timedelta, date
from django.utils import timezone
from .serializers import ChatRoomListSerializer, MessageItemSerializer
import json, re

# from pygments.lexers import get_all_lexers
# from pygments.styles import get_all_styles
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


class EnumField(models.Field):
    def __init__(self, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        assert self.choices, "Need choices for enumeration"

    def db_type(self, connection):
        if not all(isinstance(col, basestring) for col, _ in self.choices):
            raise ValueError("MySQL ENUM values should be strings")
        return "ENUM({})".format(','.join("'{}'".format(col)
                                          for col, _ in self.choices))


class AttendeeSessionStatus(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('attending', 'Attending'),
            ('in-queue', 'In Cue'),
            ('not-attending', 'Not Attending'),
            ('deciding', 'Deciding')
        ]
        kwargs.setdefault('choices', roles)
        super(AttendeeSessionStatus, self).__init__(*args, **kwargs)


class UserRoles(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('student', 'Student'),
            ('participant', 'Participant'),
            ('speaker', 'Speaker'),
            ('vip', 'Vip'),
        ]
        kwargs.setdefault('choices', roles)
        super(UserRoles, self).__init__(*args, **kwargs)


class UserTypes(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('super_admin', 'SuperAdmin'),
            ('admin', 'Admin'),
            ('third_party_admin', 'ThirdPartyAdmin')
        ]
        kwargs.setdefault('choices', types)
        super(UserTypes, self).__init__(*args, **kwargs)


class AttendeeTypes(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('user', 'User'),
            ('guest', 'Guest')
        ]
        kwargs.setdefault('choices', types)
        super(AttendeeTypes, self).__init__(*args, **kwargs)


class UserStatus(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
        ]
        kwargs.setdefault('choices', types)
        super(UserStatus, self).__init__(*args, **kwargs)


class Users(models.Model):
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45)
    company = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    password = models.CharField(max_length=150)
    phonenumber = models.CharField(max_length=45)
    role = UserRoles(max_length=20, default='vip')
    type = UserTypes(max_length=50)
    status = UserStatus(max_length=20, default='active')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            firstname=self.firstname,
            lastname=self.lastname,
            company=self.company,
            email=self.email,
            phonenumber=self.phonenumber,
            role=self.role,
            type=self.type,
            status=self.status,
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "users"


class Events(models.Model):
    name = models.CharField(max_length=45)
    created = models.DateTimeField(auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    description = models.TextField()
    url = models.CharField(max_length=50, null=True)
    address = models.TextField(null=True)
    admin = models.ForeignKey(Users, null=True)
    is_show = models.BooleanField(default=True)
    created_by = models.ForeignKey(Users, related_name='created_by_event')
    last_updated_by = models.ForeignKey(Users, related_name='last_updated_by_event')
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        admin = self.admin.as_dict() if self.admin != None else ''
        return dict(
            id=self.id,
            name=self.name,
            start=str(self.start),
            end=str(self.end),
            description=self.description,
            created=str(self.created),
            url=self.url,
            address=self.address,
            admin=admin,
            updated=str(self.updated),
            is_show=self.is_show,
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict()
        )

    class Meta:
        db_table = "events"


class GroupType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        type = [
            ('attendee', 'Attendee'),
            ('session', 'Session'),
            ('hotel', 'Hotel'),
            ('filter', 'Filter'),
            ('payment', 'Payment'),
            ('question', 'Question'),
            ('location', 'Location'),
            ('travel', 'Travel'),
            ('export_filter', 'Export Filter'),
            ('menu', 'Menu'),
            ('email', 'Email')

        ]
        kwargs.setdefault('choices', type)
        super(GroupType, self).__init__(*args, **kwargs)


class Group(models.Model):
    name = models.CharField(max_length=255)
    name_lang = models.TextField(default=None, null=True)
    type = GroupType(max_length=50)
    color = models.CharField(max_length=20, default=None, null=True)
    event = models.ForeignKey(Events)
    group_order = models.IntegerField(default=1)
    is_show = models.BooleanField(default=True)
    is_searchable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            name_lang=self.name_lang,
            type=self.type,
            color=self.color,
            event=self.event.as_dict(),
            group_order=self.group_order,
            is_searchable=self.is_searchable,
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "groups"


class Locations(models.Model):
    name = models.CharField(max_length=45)
    name_lang = models.TextField(default=None, null=True)
    description = models.TextField(default=None, blank=True, null=True)
    description_lang = models.TextField(default=None, null=True)
    group = models.ForeignKey(Group)
    address = models.TextField(default=None, blank=True, null=True)
    address_lang = models.TextField(default=None, null=True)
    latitude = models.CharField(max_length=50, blank=True, default=None, null=True)
    longitude = models.CharField(max_length=50, blank=True, default=None, null=True)
    map_highlight = models.CharField(max_length=255, blank=True, null=True, default=None)
    contact_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    contact_name_lang = models.TextField(default=None, null=True)
    contact_web = models.TextField(blank=True, null=True, default=None)
    contact_email = models.CharField(max_length=255, blank=True, null=True, default=None)
    contact_phone = models.CharField(max_length=255, blank=True, null=True, default=None)
    location_order = models.IntegerField()
    show_map_highlight = models.BooleanField(default=False)
    show_contact_name = models.BooleanField(default=False)
    show_contact_web = models.BooleanField(default=False)
    show_contact_email = models.BooleanField(default=False)
    show_contact_phone = models.BooleanField(default=False)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            name_lang=self.name_lang,
            description=self.description,
            description_lang=self.description_lang,
            group=self.group.as_dict(),
            address=self.address,
            address_lang=self.address_lang,
            latitude=self.latitude,
            longitude=self.longitude,
            map_highlight=self.map_highlight,
            contact_name=self.contact_name,
            contact_name_lang=self.contact_name_lang,
            contact_web=self.contact_web,
            contact_phone=self.contact_phone,
            contact_email=self.contact_email,
            location_order=self.location_order,
            show_map_highlight=self.show_map_highlight,
            show_contact_name=self.show_contact_name,
            show_contact_web=self.show_contact_web,
            show_contact_email=self.show_contact_email,
            show_contact_phone=self.show_contact_phone
        )

    class Meta:
        db_table = "locations"


class Seminars(models.Model):
    name = models.CharField(max_length=45)
    date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seminars"


class AttendeeStatus(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        status = [
            ('canceled', 'Canceled'),
            ('registered', 'Registered'),
            ('pending', 'Pending')
        ]
        kwargs.setdefault('choices', status)
        super(AttendeeStatus, self).__init__(*args, **kwargs)


class Presets(models.Model):
    preset_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users)
    event = models.ForeignKey(Events, null=True)
    language_code = models.CharField(max_length=10, default='en')
    date_format = models.CharField(max_length=50, default='Y-m-d')
    time_format = models.CharField(max_length=50, default='H:i')
    datetime_format = models.CharField(max_length=50, default='Y-m-d H:i')
    datetime_language = models.TextField(null=True,default=None)

    def as_dict(self):
        event = self.event.as_dict() if self.event != None else ''
        return dict(
            id=self.id,
            preset_name=self.preset_name,
            created_at=str(self.created_at),
            created_by=self.created_by.as_dict(),
            event=event,
            language_code=self.language_code,
            date_format=self.date_format,
            time_format=self.time_format,
            datetime_format=self.datetime_format,
            datetime_language=self.datetime_language
        )

    class Meta:
        db_table = "presets"


class RegistrationGroups(models.Model):
    name = models.CharField(max_length=256)
    event = models.ForeignKey(Events)
    created_at = models.DateTimeField(auto_now_add=True)
    is_show = models.BooleanField(default=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            eveent=self.event.as_dict(),
            is_show=self.is_show,
            created_at=str(self.created_at)
        )

    class Meta:
        db_table = "registration_groups"


class Attendee(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=45)
    company = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    password = models.CharField(max_length=500)
    phonenumber = models.CharField(max_length=45)
    event = models.ForeignKey(Events)
    type = AttendeeTypes(max_length=50, default='user')
    tag = models.CharField(max_length=255)
    checksum = models.TextField(null=True)
    checksum_flag = models.BooleanField(default=False)
    status = AttendeeStatus(max_length=50, default='registered')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    avatar = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=50, unique=True, null=True)
    bid = models.CharField(max_length=50, unique=True, null=True)
    push_notification_status = models.BooleanField(default=True)
    language = models.ForeignKey(Presets)
    registration_group = models.ForeignKey(RegistrationGroups, null=True, on_delete=models.SET_NULL)

    def as_dict(self):
        registration_group = self.registration_group.as_dict() if self.registration_group != None else ''
        return dict(
            id=self.id,
            firstname=self.firstname,
            lastname=self.lastname,
            company=self.company,
            email=self.email,
            phonenumber=self.phonenumber,
            event=self.event.as_dict(),
            type=self.type,
            tag=self.tag,
            status=self.status,
            secret_key=self.secret_key,
            bid=self.bid,
            created=str(self.created),
            updated=str(self.updated),
            avatar=self.avatar,
            push_notification_status=self.push_notification_status,
            language=self.language.as_dict(),
            registration_group=registration_group,
            full_name=self.get_full_name()
        )

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    class Meta:
        db_table = "attendees"


class RegistrationGroupOwner(models.Model):
    group = models.ForeignKey(RegistrationGroups)
    owner = models.ForeignKey(Attendee)

    def as_dict(self):
        return dict(
            id=self.id,
            group=self.group.as_dict(),
            owner=self.owner.as_dict()
        )

    class Meta:
        db_table = "registration_group_owner"


class EventAdmin(models.Model):
    admin = models.ForeignKey(Users)
    event = models.ForeignKey(Events)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            admin=self.admin.as_dict(),
            event=self.event.as_dict(),
            updated_at=str(self.updated_at)
        )

    class Meta:
        db_table = "event_admins"


class DefaultAnswerStatus(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        status = [
            ('set', 'Set Value'),
            ('leave', 'Leave as is'),
            ('empty', 'Empty Value')
        ]
        kwargs.setdefault('choices', status)
        super(DefaultAnswerStatus, self).__init__(*args, **kwargs)


class Questions(models.Model):
    title = models.CharField(max_length=255)
    title_lang = models.TextField(default=None, null=True)
    type = models.CharField(max_length=255)
    description = models.TextField(default=None, null=True)
    description_lang = models.TextField(default=None, null=True)
    min_character = models.IntegerField(null=True)
    max_character = models.IntegerField(null=True)
    regular_expression = models.TextField(default=None, null=True)
    default_answer = models.TextField(default=None, null=True)
    default_answer_status = DefaultAnswerStatus(default='leave', max_length=50)
    question_class = models.CharField(max_length=255, null=True)
    group = models.ForeignKey(Group)
    required = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    question_order = models.IntegerField()
    actual_definition = models.CharField(max_length=50, null=True)
    show_description = models.BooleanField(default=False)
    from_date = models.DateField(null=True,default=None,blank=True)
    to_date = models.DateField(null=True,default=None,blank=True)
    from_time = models.TimeField(null=True,default=None,blank=True)
    to_time = models.TimeField(null=True,default=None,blank=True)
    time_interval=models.CharField(max_length=2,null=True)

    def as_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            title_lang=self.title_lang,
            type=self.type,
            description=self.description,
            description_lang=self.description_lang,
            min_character=self.min_character,
            max_character=self.max_character,
            regular_expression=self.regular_expression,
            question_class=self.question_class,
            group=self.group.as_dict(),
            default_answer=self.default_answer,
            default_answer_status=self.default_answer_status,
            required=self.required,
            created=str(self.created),
            question_order=self.question_order,
            actual_definition=self.actual_definition,
            show_description = self.show_description,
            from_date = str(self.from_date),
            to_date = str(self.to_date),
            from_time = str(self.from_time),
            to_time = str(self.to_time),
            time_interval = self.time_interval
        )

    class Meta:
        db_table = "questions"


class Answers(models.Model):
    user = models.ForeignKey(Attendee)
    question = models.ForeignKey(Questions)
    value = models.TextField()

    def as_dict(self):
        return dict(
            id=self.id,
            user=self.user.as_dict(),
            question=self.question.as_dict(),
            value=self.value
        )

    class Meta:
        db_table = "answers"


class Tag(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Events, default=10)
    created = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            event=self.event.as_dict()
        )

    class Meta:
        db_table = "tags"


class ExportState(models.Model):
    file_name = models.CharField(max_length=255)
    admin = models.ForeignKey(Users)
    event = models.ForeignKey(Events)
    status = models.IntegerField(default=3, help_text="0=on progress, 1= found and done, 2=not found")
    created = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            file_name=self.file_name,
            admin=self.admin.as_dict(),
            event=self.event.as_dict(),
            status=self.status
        )

    class Meta:
        db_table = "export_state"


class AttendeeTag(models.Model):
    attendee = models.ForeignKey(Attendee)
    tag = models.ForeignKey(Tag)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            tag=self.tag.as_dict()
        )

    class Meta:
        db_table = "attendee_tags"


class Hotel(models.Model):
    name = models.CharField(max_length=255)
    name_lang = models.TextField(default=None, null=True)
    location = models.ForeignKey(Locations)
    group = models.ForeignKey(Group)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            name_lang=self.name_lang,
            location=self.location.as_dict(),
            group=self.group.as_dict(),
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "hotels"


class Room(models.Model):
    description = models.CharField(max_length=255)
    description_lang = models.TextField(default=None, null=True)
    cost = models.FloatField(default=0, null=True)
    beds = models.IntegerField()
    vat = models.FloatField(null=True)
    hotel = models.ForeignKey(Hotel)
    room_order = models.IntegerField()
    keep_hotel = models.BooleanField(default=True)
    pay_whole_amount = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def cost_excluded_vat(self):
        cost = self.cost
        try:
            if not self.pay_whole_amount and self.cost and self.beds > 1:
                divided_value = cost / self.beds
                cost = float('{:.2f}'.format(divided_value))
        except Exception as ex:
            print(ex)
            pass
        return cost

    def cost_included_vat(self):
        cost = self.cost_excluded_vat()
        total_cost = cost
        try:
            if cost and self.vat:
                total_cost = self.get_vat_amount() + cost
                total_cost = float('{:.2f}'.format(total_cost))
        except Exception as ex:
            print(ex)
            pass
        return total_cost

    def get_vat_amount(self):
        vat_amount = 0.0
        cost = self.cost_excluded_vat()
        if cost and self.vat:
            vat_amount = cost * (self.vat / 100)
            vat_amount = float('{:.2f}'.format(vat_amount))
        elif self.vat:
            vat_amount = self.vat
        return vat_amount

    def get_cost_detail(self):
        cost_detail = {
            'id': self.id, 'name': self.name, 'cost': self.cost, 'vat_rate': "{}".format(self.vat),
            'vat_amount': self.get_vat_amount(), 'total_cost': self.cost_included_vat()
        }
        return json.dumps(cost_detail)

    def as_dict(self):
        return dict(
            id=self.id,
            description=self.description,
            description_lang=self.description_lang,
            cost=self.cost,
            beds=self.beds,
            vat=self.vat,
            keep_hotel=self.keep_hotel,
            hotel=self.hotel.as_dict(),
            room_order=self.room_order,
            pay_whole_amount=self.pay_whole_amount,
            cost_included_vat=self.cost_included_vat(),
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "rooms"


class RoomAllotment(models.Model):
    room = models.ForeignKey(Room)
    allotments = models.IntegerField()
    available_date = models.DateField()
    cost = models.FloatField(default=0, null=True)
    vat = models.FloatField(null=True)

    def get_allotment_cost(self):
        cost = self.cost
        try:
            if self.cost and self.room.beds > 1:
                divided_value = cost / self.room.beds
                cost = float('{:.2f}'.format(divided_value))
        except Exception as ex:
            print(ex)
            pass
        return cost

    def as_dict(self):
        return dict(
            id=self.id,
            room=self.room.as_dict(),
            allotments=self.allotments,
            available_date=self.available_date,
            cost=self.cost,
            vat=self.vat
        )

    class Meta:
        db_table = "room_allotments"


class Session(models.Model):
    name = models.CharField(max_length=255)
    name_lang = models.TextField(default=None, null=True)
    description = models.TextField()
    description_lang = models.TextField(default=None, null=True)
    group = models.ForeignKey(Group)
    start = models.DateTimeField()
    end = models.DateTimeField()
    reg_between_start = models.DateField()
    reg_between_end = models.DateField()
    max_attendees = models.IntegerField(null=True, default=None)
    allow_attendees_queue = models.BooleanField(default=False)
    location = models.ForeignKey(Locations)
    speakers = models.CharField(max_length=1024, default=None, null=True)
    has_time = models.BooleanField(default=True)
    receive_answer = models.BooleanField(default=False)
    show_on_evaluation = models.BooleanField(default=True)
    show_on_next_up = models.BooleanField(default=True)
    allow_overlapping = models.BooleanField(default=False)
    all_day = models.BooleanField(default=False)
    session_order = models.IntegerField()
    default_answer = AttendeeSessionStatus(max_length=20, default='attending')
    default_answer_status = DefaultAnswerStatus(default='leave', max_length=50)
    cost = models.FloatField(default=0, null=True)
    vat = models.FloatField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def cost_included_vat(self):
        try:
            # error occurred when session is created [cost and are found str]
            if self.cost and self.vat:
                if type(self.cost) is str:
                    self.cost = float(self.cost)
                if type(self.vat) is str:
                    self.vat = float(self.vat)
                return self.cost*(self.vat/100)+self.cost
            else:
                return self.cost
        except:
            return self.cost

    def get_vat_amount(self):
        vat_amount = 0.0
        if self.cost and self.vat:
            vat_amount = self.cost*(self.vat/100)
        elif self.vat:
            vat_amount = self.vat
        return vat_amount

    def get_cost_detail(self):
        cost_detail = {
            'id':self.id, 'name': self.name, 'cost': self.cost, 'vat_rate': "{}".format(self.vat),
            'vat_amount': self.get_vat_amount(), 'total_cost': self.cost_included_vat()
        }
        return json.dumps(cost_detail)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            name_lang=self.name_lang,
            description=self.description,
            description_lang=self.description_lang,
            group=self.group.as_dict(),
            start=str(self.start),
            end=str(self.end),
            reg_between_start=str(self.reg_between_start),
            reg_between_end=str(self.reg_between_end),
            max_attendees=self.max_attendees,
            allow_attendees_queue=self.allow_attendees_queue,
            location=self.location.as_dict(),
            speakers=self.speakers,
            has_time=self.has_time,
            status='',
            receive_answer=self.receive_answer,
            show_on_evaluation=self.show_on_evaluation,
            show_on_next_up=self.show_on_next_up,
            allow_overlapping=self.allow_overlapping,
            all_day=self.all_day,
            session_order=self.session_order,
            default_answer=self.default_answer,
            default_answer_status=self.default_answer_status,
            cost = self.cost,
            vat_rate = self.vat,
            cost_included_vat = self.cost_included_vat(),
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "sessions"


class SeminarSpeakers(models.Model):
    speaker = models.ForeignKey(Attendee)
    session = models.ForeignKey(Session)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            session=self.session.as_dict(),
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "seminars_has_speakers"


class TravelBound(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('homebound', 'HomeBound'),
            ('outbound', 'OutBound')
        ]
        kwargs.setdefault('choices', roles)
        super(TravelBound, self).__init__(*args, **kwargs)


class Travel(models.Model):
    name = models.CharField(max_length=255)
    name_lang = models.TextField(default=None, null=True)
    description = models.TextField()
    description_lang = models.TextField(default=None, null=True)
    group = models.ForeignKey(Group)
    departure_city = models.CharField(max_length=255)
    arrival_city = models.CharField(max_length=255)
    departure = models.DateTimeField()
    arrival = models.DateTimeField()
    reg_between_start = models.DateField()
    reg_between_end = models.DateField()
    travel_bound = TravelBound(max_length=20)
    max_attendees = models.IntegerField()
    allow_attendees_queue = models.BooleanField(default=False)
    location = models.ForeignKey(Locations)
    travel_order = models.IntegerField()
    default_answer = AttendeeSessionStatus(max_length=20, default='attending')
    default_answer_status = DefaultAnswerStatus(default='leave', max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            name_lang=self.name_lang,
            description=self.description,
            description_lang=self.description_lang,
            group=self.group.as_dict(),
            departure_city=self.departure_city,
            arrival_city=self.arrival_city,
            departure=str(self.departure),
            arrival=str(self.arrival),
            reg_between_start=str(self.reg_between_start),
            reg_between_end=str(self.reg_between_end),
            max_attendees=self.max_attendees,
            travel_bound=self.travel_bound,
            allow_attendees_queue=self.allow_attendees_queue,
            location=self.location.as_dict(),
            status='',
            travel_order=self.travel_order,
            default_answer=self.default_answer,
            default_answer_status=self.default_answer_status,
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "travels"


class TravelBoundRelation(models.Model):
    travel_outbound = models.ForeignKey(Travel, related_name='travel_outbound')
    travel_homebound = models.ForeignKey(Travel, related_name='travel_homebound')

    def as_dict(self):
        return dict(
            id=self.id,
            travel_outbound=self.travel_outbound.as_dict(),
            travel_homebound=self.travel_homebound.as_dict()
        )

    class Meta:
        db_table = "travel_bound_relation"


class SeminarsUsers(models.Model):
    attendee = models.ForeignKey(Attendee)
    session = models.ForeignKey(Session)
    status = AttendeeSessionStatus(max_length=20, default='attending')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    queue_order = models.IntegerField(default=1)
    status_socket_nextup = models.BooleanField(default=False)
    status_socket_evaluation = models.BooleanField(default=False)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            session=self.session.as_dict(),
            status=self.status,
            created=str(self.created),
            updated=str(self.updated),
            queue_order=self.queue_order,
            status_socket_nextup=self.status_socket_nextup,
            status_socket_evaluation=self.status_socket_evaluation
        )

    class Meta:
        db_table = "seminars_has_users"


class TravelAttendee(models.Model):
    attendee = models.ForeignKey(Attendee)
    travel = models.ForeignKey(Travel)
    status = AttendeeSessionStatus(max_length=20, default='attending')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    queue_order = models.IntegerField(default=1)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            travel=self.travel.as_dict(),
            status=self.status,
            created=str(self.created),
            updated=str(self.updated),
            queue_order=self.queue_order
        )

    class Meta:
        db_table = "travel_has_attendees"


class Booking(models.Model):
    attendee = models.ForeignKey(Attendee)
    room = models.ForeignKey(Room)
    check_in = models.DateField()
    check_out = models.DateField()
    broken_up = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            room=self.room.as_dict(),
            check_in=str(self.check_in),
            check_out=str(self.check_out),
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = "bookings"


class RequestedBuddy(models.Model):
    booking = models.ForeignKey(Booking, related_name='buddies')
    buddy = models.ForeignKey(Attendee, null=True)
    exists = models.BooleanField(default=True)
    email = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        buddy = self.buddy.as_dict() if self.buddy != None else ''
        return dict(
            id=self.id,
            booking=self.booking.as_dict(),
            buddy=buddy,
            exists=self.exists,
            email=self.email,
            created=str(self.created),
            updated=str(self.updated)
        )

    def as_dict_alt(self):
        return dict(
            id=self.id,
            booking=self.booking.as_dict(),
            buddy='',
            exists=self.exists,
            email=self.email
        )

    class Meta:
        db_table = "requested_buddies"


class Match(models.Model):
    room = models.ForeignKey(Room)
    start_date = models.DateField()
    end_date = models.DateField()
    all_dates = models.CharField(max_length=1000, default=None)

    def as_dict(self):
        return dict(
            id=id,
            room=self.room.as_dict(),
            start_date=str(self.start_date),
            end_date=str(self.end_date),
            all_dates=self.all_dates
        )

    class Meta:
        db_table = 'matches'


class MatchLine(models.Model):
    match = models.ForeignKey(Match, related_name='lines')
    booking = models.ForeignKey(Booking)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            booking=self.booking.as_dict(),
            created=str(self.created),
            updated=str(self.updated)
        )

    class Meta:
        db_table = 'match_line'


class RuleSet(models.Model):
    name = models.CharField(max_length=100)
    preset = models.TextField()
    group = models.ForeignKey(Group)
    created_by = models.ForeignKey(Users)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    rule_order = models.IntegerField()
    is_limit = models.BooleanField(default=False)
    limit_amount = models.IntegerField(default=0)
    matchfor = models.CharField(max_length=1, null=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            preset=self.preset,
            group=self.group.as_dict(),
            rule_order=self.rule_order,
            is_limit=self.is_limit,
            limit_amount=self.limit_amount,
            matchfor=self.matchfor
        )

    class Meta:
        db_table = "rule_set"


class UsedRule(models.Model):
    rule = models.ForeignKey(RuleSet, related_name='rules')
    user = models.ForeignKey(Users)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "used_rule"


class Option(models.Model):
    question = models.ForeignKey(Questions)
    option = models.CharField(max_length=255)
    option_lang = models.TextField(default=None, null=True)
    option_order = models.IntegerField(default=1)
    default_value = models.BooleanField(default=False)

    def as_dict(self):
        return dict(
            id=self.id,
            question=self.question.as_dict(),
            option=self.option,
            option_lang=self.option_lang,
            option_order=self.option_order,
            default_value=self.default_value
        )

    class Meta:
        db_table = "options"


class NotificationTypes(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('session', 'Session'),
            ('admin', 'Admin'),
            ('attendee', 'Attendee'),
            ('group', 'Group'),
            ('session_attend', 'Session_attend'),
            ('filter_message', 'Filter_message'),

        ]
        kwargs.setdefault('choices', roles)
        super(NotificationTypes, self).__init__(*args, **kwargs)


class MessageType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('push_or_sms', 'Push_or_Sms'),
            ('sms_and_push', 'Sms_and_Push'),
            ('sms', 'Sms'),
            ('push', 'Push'),
            ('plugin_message', 'Plugin_Message')
        ]
        kwargs.setdefault('choices', types)
        super(MessageType, self).__init__(*args, **kwargs)


class MessageContents(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    sender_name = models.CharField(max_length=255)
    type = MessageType(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='message_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='message_last_updated_by')
    is_show = models.BooleanField(default=True)
    event = models.ForeignKey(Events)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            content=self.content,
            sender_name=self.sender_name,
            type=self.type,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict(),
            is_show=self.is_show,
            event=self.event.as_dict()
        )

    class Meta:
        db_table = "message_contents"


class MessageLanguageContents(models.Model):
    content = models.TextField()
    language = models.ForeignKey(Presets)
    message_content = models.ForeignKey(MessageContents)

    def as_dict(self):
        return dict(
            id=self.id,
            content=self.content,
            language=self.language.as_dict(),
            message_content=self.message_content.as_dict()
        )

    class Meta:
        db_table = "message_language_contents"


class Notification(models.Model):
    type = NotificationTypes(max_length=100)
    message = models.TextField()
    sender_attendee = models.ForeignKey(Attendee, related_name='notification_sender_attendee', null=True)
    to_attendee = models.ForeignKey(Attendee, related_name='notification_to_attendee')
    new_session = models.ForeignKey(Session, related_name='notification_new_session', null=True)
    clash_session = models.ForeignKey(Session, related_name='notification_clash_session', null=True)
    message_content = models.ForeignKey(MessageContents, null=True)
    status = models.BooleanField(default=False)
    status_socket_message = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def as_dict_alt(self):
        message_content = self.message_content.as_dict() if self.message_content != None else ''
        return dict(
            id=self.id,
            type=self.type,
            message=self.message,
            sender_attendee='',
            to_attendee=self.to_attendee.as_dict(),
            new_session=self.new_session.as_dict(),
            clash_session=self.clash_session.as_dict(),
            status=self.status,
            created_at=self.created_at,
            message_content=message_content
        )

    def as_dict(self):
        message_content = self.message_content.as_dict() if self.message_content != None else ''
        return dict(
            id=self.id,
            type=self.type,
            message=self.message,
            sender_attendee=self.sender_attendee.as_dict(),
            to_attendee=self.to_attendee.as_dict(),
            new_session='',
            clash_session='',
            status=self.status,
            status_socket_message=self.status_socket_message,
            created_at=self.created_at,
            message_content=message_content
        )

    class Meta:
        db_table = "notifications"


class Setting(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    event = models.ForeignKey(Events)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            value=self.value,
            event=self.event.as_dict()
        )

    class Meta:
        db_table = "settings"


class ChatRoom(models.Model):
    serializer_class = ChatRoomListSerializer
    created_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            type=self.type,
            session=self.session.as_dict(),
            attendee=self.attendee.as_dict(),
            created_at=self.created_at
        )

    class Meta:
        db_table = "chat_rooms"


class ChatTypes(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('session', 'Session'),
            ('filter', 'Filter'),
            ('private', 'Private'),

        ]
        kwargs.setdefault('choices', roles)
        super(ChatTypes, self).__init__(*args, **kwargs)


class ChatParticipant(models.Model):
    chat_room = models.ForeignKey(ChatRoom)
    type = ChatTypes(max_length=100)
    session = models.ForeignKey(Session, null=True)
    attendee = models.ForeignKey(Attendee, null=True)

    class Meta:
        db_table = "chat_participants"


class Message(models.Model):
    serializer_class = MessageItemSerializer
    chat_room = models.ForeignKey(ChatRoom)
    sender = models.ForeignKey(Attendee)
    text = models.TextField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            chat_room=self.chat_room.as_dict(),
            sender=self.sender.as_dict(),
            text=self.text,
            created_at=self.created_at
        )

    class Meta:
        db_table = "messages"


class TagType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('session', 'Session'),
            ('hotel', 'Hotel'),
            ('room', 'Room'),
            ('travel', 'Travel')
        ]
        kwargs.setdefault('choices', roles)
        super(TagType, self).__init__(*args, **kwargs)


class GeneralTag(models.Model):
    name = models.CharField(max_length=100)
    event = models.ForeignKey(Events, default=11)
    category = TagType(max_length=50, default='session')
    created = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            category=self.category,
            event = self.event.as_dict()
        )

    class Meta:
        db_table = "general_tags"


class SessionTags(models.Model):
    session = models.ForeignKey(Session)
    tag = models.ForeignKey(GeneralTag)

    def as_dict(self):
        return dict(
            id=self.id,
            tag=self.tag.as_dict(),
            session=self.session.as_dict()
        )

    class Meta:
        db_table = "session_has_tags"


class TravelTag(models.Model):
    travel = models.ForeignKey(Travel)
    tag = models.ForeignKey(GeneralTag)

    def as_dict(self):
        return dict(
            id=self.id,
            tag=self.tag.as_dict(),
            travel=self.travel.as_dict()
        )

    class Meta:
        db_table = "travel_has_tags"


class Checkpoint(models.Model):
    name = models.CharField(max_length=255)
    filter = models.ForeignKey(RuleSet, null=True)
    event = models.ForeignKey(Events)
    session = models.ForeignKey(Session, null=True)
    questions = models.TextField()
    defaults = models.TextField(null=True, default=None)
    allow_re_entry = models.BooleanField(default=False)
    is_hide = models.BooleanField(default=False)
    created_by = models.ForeignKey(Users)
    created_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        session = self.session.as_dict() if self.session != None else ''
        filter = self.filter.as_dict() if self.filter != None else ''
        return dict(
            id=self.id,
            name=self.name,
            filter=filter,
            event=self.event.as_dict(),
            session=session,
            questions=self.questions,
            defaults=self.defaults,
            allow_re_entry=self.allow_re_entry,
            is_hide=self.is_hide,
            created_by=self.created_by.as_dict(),
            created_at=str(self.created_at)
        )

    class Meta:
        db_table = "checkpoints"


class Scan(models.Model):
    attendee = models.ForeignKey(Attendee)
    checkpoint = models.ForeignKey(Checkpoint, null=True, default=None)
    status = models.SmallIntegerField(default=0)
    scan_time = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            checkpoint=self.checkpoint.as_dict(),
            status=self.status,
            scan_time=str(self.scan_time)
        )

    class Meta:
        db_table = "scans"


class SessionRating(models.Model):
    session = models.ForeignKey(Session)
    attendee = models.ForeignKey(Attendee)
    rating = models.IntegerField()

    def as_dict(self):
        return dict(
            id=self.id,
            session=self.session.as_dict(),
            attendee=self.attendee.as_dict(),
            rating=self.rating
        )

    class Meta:
        db_table = "session_ratings"


class ExportRule(models.Model):
    name = models.CharField(max_length=100)
    preset = models.TextField()
    group = models.ForeignKey(Group)
    created_by = models.ForeignKey(Users)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.DateField(auto_now=True)
    export_order = models.IntegerField()

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            preset=self.preset,
            group=self.group.as_dict(),
            export_order=self.export_order
        )

    class Meta:
        db_table = "export_rules"


class MessageHistoryType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('sms', 'SMS'),
            ('push', 'Push'),
            ('mail', 'Mail')
        ]
        kwargs.setdefault('choices', roles)
        super(MessageHistoryType, self).__init__(*args, **kwargs)


class MessageHistory(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    admin = models.ForeignKey(Users)
    type = MessageHistoryType(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            subject=self.subject,
            message=self.message,
            admin=self.admin.as_dict(),
            type=self.type,
            created=str(self.created)
        )

    class Meta:
        db_table = "message_history"


# class AttendeeMessage(models.Model):
#     attendee = models.ForeignKey(Attendee)
#     message = models.ForeignKey(MessageHistory)
#
#     def as_dict(self):
#         return dict(
#             id=self.id,
#             attendee=self.attendee.as_dict(),
#             message=self.message.as_dict()
#         )
#
#     class Meta:
#         db_table = "attendee_message"

class TemplateCategories(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        levels = [
            ('web_pages', 'Web Pages'),
            ('email_templates', 'Email Templates'),
            ('invoices', 'Invoices'),
            ('pdf', 'Pdf')
        ]
        kwargs.setdefault('choices', levels)
        super(TemplateCategories, self).__init__(*args, **kwargs)


class EmailTemplates(models.Model):
    name = models.CharField(max_length=255)
    content = models.TextField()
    category = TemplateCategories(max_length=25)
    event = models.ForeignKey(Events)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='template_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='template_last_updated_by')
    is_show = models.BooleanField(default=True)

    def as_dict(self):
        return dict(
            id=self.id,
            content=self.content,
            name=self.name,
            category=self.category,
            event=self.event.as_dict(),
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict(),
            is_show=self.is_show
        )

    class Meta:
        db_table = "email_templates"

class PageContent(models.Model):
    url = models.CharField(max_length=255, null=True)
    content = models.TextField()
    template = models.ForeignKey(EmailTemplates)
    login_required = models.BooleanField(default=False)
    event = models.ForeignKey(Events)
    filter = models.TextField(default=None, null=True)
    element_filter = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='created_by')
    last_updated_by = models.ForeignKey(Users, related_name='last_updated_by')
    is_show = models.BooleanField(default=True)
    disallow_logged_in = models.BooleanField(default=False)

    def as_dict(self):
        return dict(
            id=self.id,
            url=self.url,
            content=self.content,
            template=self.template.as_dict(),
            login_required=self.login_required,
            event=self.event.as_dict(),
            filter=self.filter,
            element_filter=self.element_filter,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict(),
            is_show=self.is_show,
            disallow_logged_in=self.disallow_logged_in
        )

    class Meta:
        db_table = "page_contents"


class PageImage(models.Model):
    path = models.TextField()
    event = models.ForeignKey(Events)
    page = models.ForeignKey(PageContent, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users)
    is_shown = models.BooleanField(default=True)

    def as_dict(self):
        return dict(
            id=self.id,
            path=self.path,
            event=self.event.as_dict(),
            page=self.page.as_dict(),
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            is_shown=self.is_shown
        )

    class Meta:
        db_table = "page_images"


class MenuItem(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True)
    title = models.CharField(max_length=50)
    title_lang = models.TextField(default=None, null=True)
    url = models.CharField(max_length=255, null=True)
    uid_include = models.BooleanField(default=False)
    accept_login = models.BooleanField(default=False)
    only_speaker = models.BooleanField(default=False)
    content = models.ForeignKey(PageContent, null=True, blank=True)
    level = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_visible = models.BooleanField(default=True)
    available_offline = models.BooleanField(default=False)
    created_by = models.ForeignKey(Users, related_name='menu_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='menu_last_updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allow_unregistered = models.BooleanField(default=False)
    event = models.ForeignKey(Events, null=True, default=None)

    def as_dict(self):
        parent = self.parent.as_dict() if self.parent != None else ''
        content = self.content.as_dict() if self.content != None else ''
        return dict(
            id=self.id,
            parent=parent,
            title=self.title,
            title_lang=self.title_lang,
            url=self.url,
            uid_include=self.uid_include,
            accept_login=self.accept_login,
            only_speaker=self.only_speaker,
            content=content,
            level=self.level,
            rank=self.rank,
            start_time=str(self.start_time),
            end_time=str(self.end_time),
            is_visible=self.is_visible,
            available_offline=self.available_offline,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict(),
            allow_unregistered=self.allow_unregistered,
            event_id=self.event.as_dict()
        )

    class Meta:
        db_table = "menu_items"


#
#
# class MenuPermission(models.Model):
#     menu = models.ForeignKey(MenuItem)
#     group = models.ForeignKey(Group)
#
#     def as_dict(self):
#         return dict(
#             id=self.id,
#             menu=self.menu.as_dict(),
#             group=self.group.as_dict()
#         )
#
#     class Meta:
#         db_table = "menu_permission"



class MenuPermission(models.Model):
    menu = models.ForeignKey(MenuItem)
    rule = models.ForeignKey(RuleSet, null=True, default=None)

    def as_dict(self):
        return dict(
            id=self.id,
            menu=self.menu.as_dict(),
            rule=self.rule.as_dict()
        )

    class Meta:
        db_table = "menu_permission"


class PagePermission(models.Model):
    page = models.ForeignKey(PageContent)
    rule = models.ForeignKey(RuleSet, null=True, default=None)

    def as_dict(self):
        return dict(
            id=self.id,
            page=self.page.as_dict(),
            rule=self.rule.as_dict()
        )

    class Meta:
        db_table = "page_permission"

class PhotoGroup(models.Model):
    name = models.CharField(max_length=100)
    page = models.ForeignKey(PageContent)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            page=self.page.as_dict(),
            created_at=str(self.created_at),
            created_by=self.created_by.as_dict()
        )

    class Meta:
        db_table = "photo_group"


class Photo(models.Model):
    attendee = models.ForeignKey(Attendee)
    photo = models.CharField(max_length=1000)
    is_approved = models.IntegerField(default=0)
    thumb_image = models.CharField(max_length=1000, null=True)
    comment = models.TextField(null=True)
    group = models.ForeignKey(PhotoGroup, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        group = self.group.as_dict() if self.group != None else ''
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            photo=self.photo,
            is_appoved=self.is_approved,
            thumb_image=self.thumb_image,
            comment=self.comment,
            group=self.group,
            uploaded_at=str(self.uploaded_at)
        )

    class Meta:
        db_table = "photos"


class ActivityHistoryType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('update', 'Update'),
            ('delete', 'Delete'),
            ('register', 'Register'),
            ('message', 'Message'),
            ('offline', 'Offline Download'),
            ('check-in', 'Check In')

        ]
        kwargs.setdefault('choices', roles)
        super(ActivityHistoryType, self).__init__(*args, **kwargs)


class ActivityCategoryType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('event', 'Event'),
            ('session', 'Session'),
            ('question', 'Question'),
            ('travel', 'Travel'),
            ('room', 'Room'),
            ('message', 'Message'),
            ('profile', 'Profile'),
            ('push_notification', 'Push_notification'),
            ('group', 'Group'),
            ('tag', 'Tag'),
            ('package', 'Package'),
            ('checkpoint', 'Checkpoint'),
            ('photo', 'Photo'),
            ('registration_group', 'Registration_group'),
            ('rebate', 'Rebate'),
            ('order', 'Order'),
            ('order_item', 'Order Item'),
            ('credit_order', 'Credit Order'),
            ('credit_usage', 'Credit Usage'),
            ('payment', 'Payment')
        ]
        kwargs.setdefault('choices', roles)
        super(ActivityCategoryType, self).__init__(*args, **kwargs)


class ActivityHistory(models.Model):
    attendee = models.ForeignKey(Attendee)
    admin = models.ForeignKey(Users, null=True)
    activity_type = ActivityHistoryType(max_length=50)
    category = ActivityCategoryType(max_length=50)
    message = models.ForeignKey(MessageHistory, null=True)
    session = models.ForeignKey(Session, null=True)
    question = models.ForeignKey(Questions, null=True)
    travel = models.ForeignKey(Travel, null=True)
    room = models.ForeignKey(Room, null=True)
    photo = models.ForeignKey(Photo, null=True)
    old_value = models.TextField()
    new_value = models.TextField()
    event = models.ForeignKey(Events)
    checkpoint = models.ForeignKey(Checkpoint, null=True)
    registration_group = models.ForeignKey(RegistrationGroups, null=True)
    created = models.DateTimeField(auto_now_add=True)
    activity_message = models.TextField(null=True)

    def as_dict(self):
        message = self.message.as_dict() if self.message != None else ''
        admin = self.admin.as_dict() if self.admin != None else ''
        session = self.session.as_dict() if self.session != None else ''
        question = self.question.as_dict() if self.question != None else ''
        travel = self.travel.as_dict() if self.travel != None else ''
        room = self.room.as_dict() if self.room != None else ''
        checkpoint = self.checkpoint.as_dict() if self.checkpoint != None else ''
        photo = self.photo.as_dict() if self.photo != None else ''
        registration_group = self.registration_group.as_dict() if self.registration_group != None else ''

        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            admin=admin,
            activity_type=self.activity_type,
            category=self.category,
            message=message,
            session=session,
            question=question,
            travel=travel,
            room=room,
            checkpoint=checkpoint,
            photo=photo,
            registration_group=registration_group,
            old_value=self.old_value,
            new_value=self.new_value,
            activity_message= self.activity_message,
            event=self.event.as_dict(),
            created=str(self.created)
        )

    class Meta:
        db_table = "activity_history"


class AccessLevel(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        levels = [
            ('read', 'Read'),
            ('write', 'Write'),
            ('none', 'None')
        ]
        kwargs.setdefault('choices', levels)
        super(AccessLevel, self).__init__(*args, **kwargs)


class GroupPermission(models.Model):
    admin = models.ForeignKey(Users)
    group = models.ForeignKey(Group)
    access_level = AccessLevel(max_length=10, default='none')
    description = models.CharField(max_length=100, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            admin=self.admin.as_dict(),
            group=self.group.as_dict(),
            access_level=self.access_level,
            description=self.description,
            updated_at=str(self.updated_at)
        )

    class Meta:
        db_table = "group_permissions"


class ContentType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        contents = [
            ('event', 'Event'),
            ('attendee', 'Attendee'),
            ('deleted_attendee', 'DeletedAttendee'),
            ('session', 'Session'),
            ('question', 'Question'),
            ('travel', 'Travel'),
            ('location', 'Location'),
            ('hotel', 'Hotel'),
            ('page', 'Page'),
            ('menu', 'Menu'),
            ('template', 'Template'),
            ('css', 'Css'),
            ('filter', 'Filter'),
            ('export_filter', 'ExportFilter'),
            ('photo_reel', 'PhotoReel'),
            ('message', 'Message'),
            ('file_browser', 'FileBrowser'),
            ('checkpoints', 'Checkpoints'),
            ('language', 'Language'),
            ('economy', 'Economy'),
            ('setting', 'Setting'),
            ('assign_session', 'AssignSession'),
            ('assign_travel', 'AssignTravel'),
            ('assign_hotel', 'AssignHotel'),
            ('group_registration', 'GroupRegistration')
        ]
        kwargs.setdefault('choices', contents)
        super(ContentType, self).__init__(*args, **kwargs)


class ContentPermission(models.Model):
    admin = models.ForeignKey(Users)
    content = ContentType(max_length=20)
    event = models.ForeignKey(Events)
    access_level = AccessLevel(max_length=10, default='none')
    description = models.CharField(max_length=100, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            admin=self.admin.as_dict(),
            event=self.event.as_dict(),
            content=self.content,
            access_level=self.access_level,
            description=self.description,
            updated_at=str(self.updated_at)
        )

    def permission_dict(self):
        return dict(
            id=self.id,
            access_level=self.access_level
        )

    class Meta:
        db_table = "content_permissions"


class QuestionPreRequisite(models.Model):
    question = models.ForeignKey(Questions, related_name='question')
    pre_req_question = models.ForeignKey(Questions, related_name='pre_req_question')
    pre_req_answer = models.ForeignKey(Option)
    action = models.BooleanField(default=True)

    def as_dict(self):
        return dict(
            id=self.id,
            question=self.question.as_dict(),
            pre_req_question=self.pre_req_question.as_dict(),
            pre_req_answer=self.pre_req_answer.as_dict(),
            action=self.action
        )

    class Meta:
        db_table = "question_pre_requisite"


class ExportNotification(models.Model):
    file_name = models.CharField(max_length=255, null=False, unique=True)
    admin = models.ForeignKey(Users)
    event = models.ForeignKey(Events)
    status = models.SmallIntegerField()
    request_time = models.DateTimeField()

    def as_dict(self):
        return dict(
            id=self.id,
            file_name=self.file_name,
            admin=self.admin.as_dict(),
            event=self.event.as_dict(),
            status=self.status,
            request_time=str(self.request_time)
        )

    class Meta:
        db_table = "export_notification"


class ImportChangeRequest(models.Model):
    event = models.ForeignKey(Events)
    changed_data = models.TextField()
    imported_by = models.ForeignKey(Users, related_name='imported_by')
    approved_by = models.ForeignKey(Users, related_name='approved_by', null=True)
    status = models.SmallIntegerField()
    type = models.CharField(max_length=50, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True)

    def as_dict(self):
        return dict(
            id=self.id,
            event=self.event.as_dict(),
            changed_data=self.changed_data,
            imported_by=self.imported_by.as_dict(),
            approved_by=self.approved_by.as_dict(),
            status=self.status,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at)
        )

    class Meta:
        db_table = "import_change_request"


class ImportChangeStatus(models.Model):
    filename = models.TextField()
    message = models.TextField(null=True)
    duplicate_attendees = models.TextField(null=True)
    status = models.SmallIntegerField()
    import_change = models.ForeignKey(ImportChangeRequest, null=True)

    def as_dict(self):
        return dict(
            id=self.id,
            filename=self.filename,
            message=self.message,
            duplicate_attendees=self.duplicate_attendees,
            status=self.status,
            import_change=self.import_change_id.as_dict()
        )

    class Meta:
        db_table = "import_change_status"


class ElementType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('plugin', 'Plugin'),
            ('public_notification', 'Public_notification'),
            ('default_plugin', 'Default_plugin')
        ]
        kwargs.setdefault('choices', roles)
        super(ElementType, self).__init__(*args, **kwargs)


class Elements(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    type = ElementType(max_length=20, default='plugin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='element_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='element_last_updated_by')

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            slug=self.slug,
            type=self.type,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict()
        )

    class Meta:
        db_table = "elements"


class OsType(EnumField, models.IntegerField):
    def __init__(self, *args, **kwargs):
        os = [
            ('1', 'Android'),
            ('2', 'IOS'),
        ]
        kwargs.setdefault('choices', os)
        super(OsType, self).__init__(*args, **kwargs)


class DeviceToken(models.Model):
    device_unique_id = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    os_type = OsType()
    arn_enpoint = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    attendee = models.ForeignKey(Attendee, null=True, blank=True)
    offline_pakage_status = models.BooleanField(default=True)
    package_download_count = models.IntegerField(default=0)
    package_created_at = models.DateTimeField(null=True)
    package_version = models.IntegerField(default=0)

    def as_dict(self):
        return dict(
            id=self.id,
            device_unique_id=self.device_unique_id,
            token=self.token,
            os_type=self.os_type,
            offline_pakage_status=self.offline_pakage_status,
            package_download_count=self.package_download_count,
            attendee=self.attendee.as_dict(),
            package_created_at=str(self.package_created_at),
            package_version=self.package_version
        )

    class Meta:
        db_table = "devices_token"


class StyleSheet(models.Model):
    style = models.TextField()
    event = models.ForeignKey(Events)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users, default=None)
    version = models.IntegerField(default=1)

    def as_dict(self):
        return dict(
            id=self.id,
            style=self.style,
            created_by=self.created_by.as_dict(),
            event=self.event.as_dict(),
            version = self.version,
            updated_at=str(self.updated_at),
            created_at=str(self.created_at),

        )

    class Meta:
        db_table = "event_stylesheets"


class CurrentEvent(models.Model):
    event = models.ForeignKey(Events)
    admin = models.ForeignKey(Users)

    def as_dict(self):
        return dict(
            id=self.id,
            event=self.event.as_dict(),
            admin=self.admin.as_dict(),

        )

    class Meta:
        db_table = "current_event"


class CurrentFilter(models.Model):
    event = models.ForeignKey(Events)
    admin = models.ForeignKey(Users)
    filter = models.ForeignKey(RuleSet, null=True, default=None)
    visible_columns = models.TextField(null=True, default=None)
    show_rows = models.IntegerField(null=True, default=None)
    table_type = models.CharField(default='attendee', max_length=100)
    sorted_column = models.IntegerField(null=True, default=1)
    sorting_order = models.CharField(default='asc', max_length=32)

    def as_dict(self):
        return dict(
            id=self.id,
            event=self.event.as_dict(),
            admin=self.admin.as_dict(),
            filter=self.filter.as_dict(),
            visible_columns=self.visible_columns,
            show_rows=self.show_rows,
            table_type=self.table_type,
            sorted_column=self.sorted_column,
            sorting_order=self.sorting_order

        )

    class Meta:
        db_table = "current_filter"


class ColumnType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('session', 'Session'),
            ('hotel', 'Hotel'),
        ]
        kwargs.setdefault('choices', types)
        super(ColumnType, self).__init__(*args, **kwargs)


class VisibleColumns(models.Model):
    event = models.ForeignKey(Events)
    admin = models.ForeignKey(Users)
    visible_columns = models.TextField(null=True, default=None)
    type = ColumnType(max_length=50)

    def as_dict(self):
        return dict(
            id=self.id,
            event=self.event.as_dict(),
            admin=self.admin.as_dict(),
            visible_columns=self.visible_columns,
            type=self.type
        )

    class Meta:
        db_table = "visible_columns"


class EmailContents(models.Model):
    subject = models.TextField()
    subject_lang = models.TextField(default=None, null=True)
    content = models.TextField()
    name = models.CharField(max_length=255)
    template = models.ForeignKey(EmailTemplates)
    sender_email = models.CharField(max_length=255, default='registration@eventdobby.com')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='content_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='content_last_updated_by')
    is_show = models.BooleanField(default=True)

    def as_dict(self):
        return dict(
            id=self.id,
            content=self.content,
            subject=self.subject,
            subject_lang=self.subject_lang,
            name=self.name,
            template=self.template.as_dict(),
            sender_email=self.sender_email,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict(),
            is_show=self.is_show
        )

    class Meta:
        db_table = "email_contents"


class EmailLanguageContents(models.Model):
    content = models.TextField()
    language = models.ForeignKey(Presets)
    email_content = models.ForeignKey(EmailContents)

    def as_dict(self):
        return dict(
            id=self.id,
            content=self.content,
            language=self.language.as_dict(),
            email_content=self.email_content.as_dict()
        )

    class Meta:
        db_table = "email_language_contents"


class ReceiversStatus(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('sent', 'Sent'),
            ('not_sent', 'Not_sent'),
        ]
        kwargs.setdefault('choices', types)
        super(ReceiversStatus, self).__init__(*args, **kwargs)


class EmailReceivers(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    status = ReceiversStatus(max_length=100, default='not_sent')
    email_content = models.ForeignKey(EmailContents)
    attendee = models.ForeignKey(Attendee, null=True)
    last_received = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(Users)
    is_show = models.BooleanField(default=True)

    def as_dict(self):
        attendee = self.attendee.as_dict() if self.attendee != None else ''
        return dict(
            id=self.id,
            firstname=self.firstname,
            lastname=self.lastname,
            email=self.email,
            status=self.status,
            email_content=self.email_content.as_dict(),
            attendee=attendee,
            last_received=str(self.last_received),
            added_by=self.added_by.as_dict(),
            is_show=self.is_show
        )

    class Meta:
        db_table = "email_receivers"


class MessageReceivers(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    mobile_phone = models.CharField(max_length=255)
    status = ReceiversStatus(max_length=100, default='not_sent')
    message_content = models.ForeignKey(MessageContents)
    attendee = models.ForeignKey(Attendee, null=True)
    last_received = models.DateTimeField(auto_now=True)
    added_by = models.ForeignKey(Users)
    is_show = models.BooleanField(default=True)
    push = models.BooleanField(default=False)

    def as_dict(self):
        attendee = self.attendee.as_dict() if self.attendee != None else ''
        return dict(
            id=self.id,
            firstname=self.firstname,
            lastname=self.lastname,
            mobile_phone=self.mobile_phone,
            status=self.status,
            message_content=self.message_content.as_dict(),
            attendee=attendee,
            last_received=str(self.last_received),
            added_by=self.added_by.as_dict(),
            is_show=self.is_show,
            push=self.push
        )

    class Meta:
        db_table = "message_receivers"


class EmailReceiversHistory(models.Model):
    receiver = models.ForeignKey(EmailReceivers)
    sending_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            receiver=self.receiver.as_dict(),
            sending_at=str(self.sending_at)
        )

    class Meta:
        db_table = "email_receivers_history"


class MessageHistoryType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        types = [
            ('sms', 'SMS'),
            ('push', 'PUSH'),
        ]
        kwargs.setdefault('choices', types)
        super(MessageHistoryType, self).__init__(*args, **kwargs)


class MessageReceiversHistory(models.Model):
    receiver = models.ForeignKey(MessageReceivers)
    type = MessageHistoryType(max_length=100)
    sending_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            receiver=self.receiver.as_dict(),
            type=self.type,
            sending_at=str(self.sending_at)
        )

    class Meta:
        db_table = "message_receivers_history"


class PasswordResetRequest(models.Model):
    user = models.ForeignKey(Users)
    hash_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField(default=None)
    already_used = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_requests"


class ElementsQuestions(models.Model):
    name = models.CharField(max_length=1000)
    group = models.ForeignKey(Elements)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='element_question_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='element_question_last_updated_by')
    question_key = models.CharField(max_length=1000)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            group=self.group.as_dict(),
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict(),
            question_key=self.question_key
        )

    class Meta:
        db_table = "elements_questions"


class ElementsAnswers(models.Model):
    element_question = models.ForeignKey(ElementsQuestions)
    answer = models.TextField()
    description = models.TextField()
    box_id = models.IntegerField()
    page = models.ForeignKey(PageContent)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Users, related_name='element_answer_created_by')
    last_updated_by = models.ForeignKey(Users, related_name='element_answer_last_updated_by')

    def as_dict(self):
        return dict(
            id=self.id,
            element_question=self.element_question.as_dict(),
            answer=self.answer,
            description=self.description,
            box_id=self.box_id,
            page=self.page.as_dict(),
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            created_by=self.created_by.as_dict(),
            last_updated_by=self.last_updated_by.as_dict()
        )

    class Meta:
        db_table = "elements_answers"


class PluginType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('text', 'Text'),
            ('item_text', 'Item Text'),
            ('button', 'Button'),
            ('notification', 'Notification'),
            ('validation_text', 'Validation Text')
        ]
        kwargs.setdefault('choices', roles)
        super(PluginType, self).__init__(*args, **kwargs)


class ElementDefaultLang(models.Model):
    element = models.ForeignKey(Elements)
    type = PluginType(max_length=100, default='text')
    lang_key = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    default_value = models.TextField()

    def as_dict(self):
        return dict(
            id=self.id,
            element=self.element.as_dict(),
            type=self.type,
            lang_key=self.lang_key,
            name=self.name,
            default_value=self.default_value
        )

    class Meta:
        db_table = "element_default_lang"


class ElementPresetLang(models.Model):
    preset = models.ForeignKey(Presets, on_delete=models.CASCADE)
    element_default_lang = models.ForeignKey(ElementDefaultLang)
    value = models.TextField()

    def as_dict(self):
        return dict(
            id=self.id,
            preset=self.presets.as_dict(),
            element_default_lang=self.element_default_lang.as_dict(),
            value=self.value
        )

    class Meta:
        db_table = "element_preset_lang"


class PresetEvent(models.Model):
    event = models.ForeignKey(Events)
    preset = models.ForeignKey(Presets, on_delete=models.CASCADE)

    def as_dict(self):
        return dict(
            event=self.event.as_dict(),
            preset=self.preset.as_dict()
        )

    class Meta:
        db_table = "preset_event"


class AttendeeGroups(models.Model):
    attendee = models.ForeignKey(Attendee)
    group = models.ForeignKey(Group)

    def as_dict(self):
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            group=self.group.as_dict()
        )

    class Meta:
        db_table = "attendee_groups"


class CustomClasses(models.Model):
    classname = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users)
    event = models.ForeignKey(Events)

    def as_dict(self):
        return dict(
            id=self.id,
            classname=self.classname,
            event=self.event.as_dict(),
            created_at=str(self.created_at),
            created_by=self.created_by.as_dict()
        )

    class Meta:
        db_table = "custom_classes"


class PageContentClasses(models.Model):
    page = models.ForeignKey(PageContent)
    box_id = models.IntegerField()
    classname = models.ForeignKey(CustomClasses)

    def as_dict(self):
        return dict(
            id=self.id,
            page=self.page.as_dict(),
            box_id=self.box_id,
            classname=self.classname.as_dict()
        )

    class Meta:
        db_table = "page_content_classes"


class DeletedAttendee(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    phonenumber = models.CharField(max_length=45)
    event = models.ForeignKey(Events)
    deleted_at = models.DateTimeField(auto_now_add=True)
    deleted_by = models.ForeignKey(Users)

    def as_dict(self):
        return dict(
            id=self.id,
            firstname=self.firstname,
            lastname=self.lastname,
            email=self.email,
            phonenumber=self.phonenumber,
            event=self.event.as_dict(),
            deleted_at=str(self.deleted_at),
            deleted_by=self.deleted_by.as_dict()
        )

    class Meta:
        db_table = "deleted_attendees"


class DeletedHistory(models.Model):
    attendee = models.ForeignKey(DeletedAttendee)
    admin = models.ForeignKey(Users, null=True)
    activity_type = ActivityHistoryType(max_length=50)
    category = ActivityCategoryType(max_length=50)
    message = models.ForeignKey(MessageHistory, null=True)
    session = models.ForeignKey(Session, null=True)
    question = models.ForeignKey(Questions, null=True)
    travel = models.ForeignKey(Travel, null=True)
    room = models.ForeignKey(Room, null=True)
    photo = models.ForeignKey(Photo, null=True)
    registration_group = models.ForeignKey(RegistrationGroups, null=True)
    old_value = models.TextField()
    new_value = models.TextField()
    event = models.ForeignKey(Events)
    created = models.DateTimeField()
    activity_message = models.TextField(null=True)

    def as_dict(self):
        message = self.message.as_dict() if self.message != None else ''
        admin = self.admin.as_dict() if self.admin != None else ''
        session = self.session.as_dict() if self.session != None else ''
        question = self.question.as_dict() if self.question != None else ''
        travel = self.travel.as_dict() if self.travel != None else ''
        room = self.room.as_dict() if self.room != None else ''
        photo = self.photo.as_dict() if self.photo != None else ''
        registration_group = self.registration_group.as_dict() if self.registration_group != None else ''

        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            admin=admin,
            activity_type=self.activity_type,
            category=self.category,
            message=message,
            session=session,
            question=question,
            travel=travel,
            room=room,
            photo=photo,
            registration_group=registration_group,
            old_value=self.old_value,
            new_value=self.new_value,
            event=self.event.as_dict(),
            created=str(self.created),
            activity_message=self.activity_message
        )

    class Meta:
        db_table = "deleted_history"


class Cookie(models.Model):
    cookie_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def as_dict(self):
        return dict(
            id=self.id,
            cookie_key=self.cookie_key,
            created_at=str(self.created)
        )

    class Meta:
        db_table = "cookie"


class CookiePage(models.Model):
    cookie = models.ForeignKey(Cookie)
    page = models.ForeignKey(PageContent)
    visit_count = models.IntegerField()
    visit_date = models.DateField()

    def as_dict(self):
        return dict(
            id=self.id,
            cookie=self.cookie.as_dict(),
            page=self.page.as_dict(),
            visit_count=self.visit_count,
            visit_date=self.visit_date
        )

    class Meta:
        db_table = "cookie_page"


class DashboardPlugin(models.Model):
    setting_data = models.TextField()
    event = models.ForeignKey(Events)
    modified_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(Users)

    def as_dict(self):
        return dict(
            id=self.id,
            setting_data=self.setting_data,
            event=self.event.as_dict(),
            modified_at=str(self.modified_at),
            modified_by=self.modified_by.as_dict()
        )

    class Meta:
        db_table = "dashboard_plugin"


class PluginSubmitButton(models.Model):
    name = models.CharField(max_length=100)
    page = models.ForeignKey(PageContent)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            page=self.page.as_dict(),
            created_at=str(self.created_at),
            created_by=self.created_by.as_dict()
        )

    class Meta:
        db_table = "plugin_submit_button"


class PluginPdfButton(models.Model):
    name = models.CharField(max_length=100)
    page = models.ForeignKey(PageContent)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users)

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            page=self.page.as_dict(),
            created_at=str(self.created_at),
            created_by=self.created_by.as_dict()
        )

    class Meta:
        db_table = "plugin_pdf_button"


class AttendeeSubmitButton(models.Model):
    button = models.ForeignKey(PluginSubmitButton)
    attendee = models.ForeignKey(Attendee, null=True)
    hit_count = models.IntegerField()

    def as_dict(self):
        attendee = self.attendee.as_dict() if self.attendee != None else ''
        return dict(
            id=self.id,
            button=self.button.as_dict(),
            attendee=attendee,
            hit_count=self.hit_count
        )

    class Meta:
        db_table = "attendee_submit_button"


class AttendeePasswordResetRequest(models.Model):
    attendee = models.ForeignKey(Attendee)
    hash_code = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expired_at = models.DateTimeField(default=None)
    already_used = models.BooleanField(default=False)

    class Meta:
        db_table = "attendee_password_reset_requests"


class ElementHtml(models.Model):
    page = models.ForeignKey(PageContent)
    box_id = models.IntegerField()
    language = models.ForeignKey(Presets, null=True)
    compiled = models.TextField()
    uncompiled = models.TextField()
    created_by = models.ForeignKey(Users)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            page=self.page.as_dict(),
            box_id=self.box_id,
            language=self.language.as_dict(),
            compiled=self.compiled,
            uncompiled=self.uncompiled,
            created_at=str(self.created_at),
            created_by=self.created_by.as_dict(),
            updated_at=str(self.updated_at)
        )

    class Meta:
        db_table = "element_html"

class MultiLanguageType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('menu_title', 'Menu Title'),
            ('question_label', 'Question Label'),
            ('question_description', 'Question Description'),
            ('session_name', 'Session Name'),
            ('session_description', 'Session Description'),
            ('travel_name','Travel Name'),
            ('travel_description', 'Travel Description'),
            ('location_name', 'Location Name'),
            ('location_description', 'Location Description'),
            ('location_address', 'Location Address'),
            ('contact_name', 'Contact Name'),
            ('hotel_name', 'Hotel Name'),
            ('hotel_room_description', 'Hotel Room Description'),
            ('group_name', 'Group Name'),
            ('question_option', 'Question Option')
        ]
        kwargs.setdefault('choices', roles)
        super(MultiLanguageType, self).__init__(*args, **kwargs)


class OrderStatus(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('open', 'Open'),
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('cancelled', 'Cancelled')
        ]
        kwargs.setdefault('choices', roles)
        super(OrderStatus, self).__init__(*args, **kwargs)


class Orders(models.Model):
    attendee = models.ForeignKey(Attendee)
    order_number = models.CharField(max_length=100)
    cost = models.FloatField(default=0)
    rebate_amount = models.FloatField(default=0)
    vat_amount = models.FloatField(default=0)
    due_date = models.DateTimeField(null=True)
    status = OrderStatus(max_length=100, default='open')
    invoice_ref = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(Users, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice_date = models.DateTimeField(null=True, default=None)
    is_preselected = models.BooleanField(default=False)

    def get_total_cost(self):
        """total cost(including rebate) is cost including vat"""
        if self.vat_amount:
            return self.cost + self.vat_amount
        else:
            return self.cost

    def get_past_due(self):
        """if order status is 'paid' then no need for past_due
           otherwise checking due_date passed"""
        if self.status == 'pending':
            return date.today() > self.due_date.date()
        else:
            return False

    def as_dict(self):
        created_by = self.created_by.as_dict() if self.created_by != None else ''
        return dict(
            id=self.id,
            attendee=self.attendee.as_dict(),
            order_number=self.order_number,
            cost=self.cost,
            total_cost=self.get_total_cost(),
            rebate_amount = self.rebate_amount,
            vat_amount = self.vat_amount,
            due_date = str(self.due_date),
            due_date_datetype = self.due_date,
            past_due = self.get_past_due(),
            status = self.status,
            invoice_ref = self.invoice_ref,
            invoice_date = str(self.invoice_date),
            created_by = created_by,
            is_preselected = self.is_preselected,
            created_at = str(self.created_at),
            updated_at = str(self.updated_at)
        )

    class Meta:
        db_table = "orders"


class OrderItemType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('session', 'Session'),
            ('hotel', 'Hotel'),
            ('travel', 'Travel'),
            ('rebate', 'Rebate'),
            ('adjustment', 'Adjustment')
        ]
        kwargs.setdefault('choices', roles)
        super(OrderItemType, self).__init__(*args, **kwargs)


class RebateType(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('percentage', 'Percentage'),
            ('fixed', 'Fixed sum')
        ]
        kwargs.setdefault('choices', roles)
        super(RebateType, self).__init__(*args, **kwargs)


class Rebates(models.Model):
    name = models.CharField(max_length=255)
    type_id = models.TextField(default=None, null=True)
    rebate_type = RebateType(max_length=100)
    value = models.FloatField()
    event = models.ForeignKey(Events, null=True)
    created_by = models.ForeignKey(Users)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_rebate_amount(self, item_cost):
        if self.rebate_type == 'percentage':
            amount = (item_cost * self.value) / 100
        else:
            amount = self.value
        return amount

    def as_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            type_id=self.type_id,
            rebate_type=self.rebate_type,
            value=self.value,
            event=self.event.as_dict(),
            created_by=self.created_by.as_dict(),
            created_at=str(self.created_at),
            updated_at=str(self.updated_at)
        )

    def __str__(self):
        return  self.name
    
    class Meta:
        db_table = "rebates"


class OrderItems(models.Model):
    order = models.ForeignKey(Orders)
    item_type = OrderItemType(max_length=100)
    item_id = models.IntegerField()
    # including rebate_amount
    # value when item_type is rebate (could be percentage value)
    cost = models.FloatField(default=0)
    #
    # only rebate amount
    rebate_amount = models.FloatField(default=0)
    rebate = models.ForeignKey(Rebates, null=True, on_delete=models.SET_NULL)

    # this field same as item_id for item type and order item id for rebate type
    # this field is created for order by [so-that a rebate can stay after the applied item]
    # and also to keep track on which item rebate applied
    # will be null, only unused rebate
    rebate_for_item_id = models.IntegerField(null=True)
    vat_rate = models.FloatField(null=True)
    rebate_for_item_type = OrderItemType(max_length=100, null=True)

    # rebate applied when order was "open" Or ["pending","paid"]
    # needed for item_type='rebate'
    # if rebate applied when [pending, paid] then we do not show in public but show in admin
    # applied_on_open_order will distinguish which applied rebate to show and not to show in public
    applied_on_open_order = models.BooleanField(default=True)

    # when order is [pending, paid], if rebate is removed then
    # we create new order for that but we need to keep the record that
    # the rebate is deleted. [note: we do not change value when order is [pending, paid]]
    # so, admin will not able to delete again and still stay with pending/paid order
    # so it's not violating order_table when order is pending or paid
    # this field is also been used for item too, [usage: get_order_id()]
    rebate_is_deleted = models.BooleanField(default=False)
    # item_booking_id needs to keep track on multiple order on same room
    # effected on only 'hotel' item type
    item_booking_id = models.IntegerField(null=True)
    # effected_day_count needs to keep same booking multiple orders day_count
    # effected on only 'hotel' item type
    # day_count specifies how much cost is effecting in this order_item [mostly needed for pending
    # and paid order_item where cost can't be changed but when credit order created against this order_item when
    # booking stay reduced, then we can change the effected_day_count value that represents the cost effecting from
    # this order_item]
    effected_day_count = models.IntegerField(null=True)
    # booking check-in and check-out dates needed because
    # order table need to show those dates with hotel order item name
    # these dates are set when order turn open to pending/paid
    booking_check_in = models.DateField(null=True)
    booking_check_out = models.DateField(null=True)

    def get_vat_amount(self):
        # not using for item_type='rebate'
        if self.vat_rate:
            value = (self.cost * self.vat_rate) / 100
        else:
            value = 0
        return value

    def get_rebate_vat_amount(self, amount):
        """
        This function is to get specific vat amount depend on different value.
        [when credit order is created, vat amount is needed respect to rebate amount]
        Must call by rebate_affected_item
        """
        if self.vat_rate:
            value = (amount * self.vat_rate) / 100
        else:
            value = 0
        return value

    def get_total_cost(self):
        value = self.cost + self.get_vat_amount()
        return value

    def get_item_name(self):
        name = 'Not exists'
        if self.item_type == 'session':
            session = Session.objects.filter(id=self.item_id)
            if session:
                name = session[0].name
        elif self.item_type == 'hotel':
            room = Room.objects.filter(id=self.item_id)
            if room.exists():
                booking_check_in = self.booking_check_in
                booking_check_out = self.booking_check_out
                check_in_check_out = ""
                if not booking_check_in:
                    item_booking = Booking.objects.filter(id=self.item_booking_id).first()
                    if item_booking:
                        booking_check_in = item_booking.check_in
                        booking_check_out = item_booking.check_out
                if booking_check_in:
                    lang_id = self.order.attendee.language_id
                    check_in_check_out = "{} - {}".format(self.get_formated_date_string(booking_check_in, lang_id), self.get_formated_date_string(booking_check_out, lang_id))
                name = '{} {} {}'.format(room[0].hotel.name, room[0].description, check_in_check_out)
        elif self.item_type == 'travel':
            travel = Travel.objects.filter(id=self.item_id)
            if travel:
                name = travel[0].name
        elif self.item_type == 'rebate':
            rebate = Rebates.objects.filter(id=self.item_id)
            if rebate:
                name = rebate[0].name
        elif self.item_type == 'adjustment':
            name = "Cost adjustment"
            if self.rebate_id:
                rebate = Rebates.objects.filter(id=self.rebate_id)
                if rebate:
                    name = "Adjustment for {}".format(rebate[0].name)

        return name

    def get_formated_date_string(self, date_value, lang_id):
        try:
            date_format = Presets.objects.get(id=lang_id).date_format
            compiled_re = re.compile('[a-zA-Z]')
            matched_keys = compiled_re.findall(date_format)
            for key in matched_keys:
                date_format = date_format.replace(key, '%' + key)

            date_string = date_value.strftime(date_format)
        except Exception as excep:
            date_string = ''

        return date_string

    def get_rebate_amount(self, value):
        amount = self.cost
        rebate = Rebates.objects.filter(id=self.item_id)
        if rebate.exists():
            rebate = rebate.first()
            if rebate.rebate_type == 'percentage':
                amount = (value * self.cost) / 100
        return amount

    def as_dict(self):
        rebate = self.rebate.as_dict() if self.rebate != None else ''
        return dict(
            id=self.id,
            order=self.order.as_dict(),
            item_type=self.item_type,
            item_id=self.item_id,
            item_name=self.get_item_name(),
            cost=self.cost,
            total_cost=self.get_total_cost(),
            rebate_amount=self.rebate_amount,
            rebate=rebate,
            rebate_for_item_id=self.rebate_for_item_id,
            rebate_for_item_type=self.rebate_for_item_type,
            vat_rate=self.vat_rate,
            applied_on_open_order=self.applied_on_open_order,
            rebate_is_deleted=self.rebate_is_deleted,
            item_booking_id=self.item_booking_id,
            effected_day_count=self.effected_day_count,
            vat_amount=self.get_vat_amount()
        )

    class Meta:
        db_table = "order_items"


class CreditOrders(models.Model):
    order = models.ForeignKey(Orders)
    order_number = models.CharField(max_length=100)
    cost_excluding_vat = models.FloatField()
    cost_including_vat = models.FloatField(default=0)
    type = OrderItemType(max_length=100)
    # rebate name OR item name(session, hotel, travel)
    item_name = models.CharField(max_length=255)
    status = OrderStatus(max_length=100, default='open')
    invoice_ref = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(Users, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_vat_amount(self):
        return self.cost_including_vat - self.cost_excluding_vat

    def as_dict(self):
        created_by = self.created_by.as_dict() if self.created_by != None else ''
        return dict(
            id=self.id,
            order=self.order.as_dict(),
            order_number=self.order_number,
            cost_excluding_vat=self.cost_excluding_vat,
            cost_including_vat=self.cost_including_vat,
            type=self.type,
            item_name=self.item_name,
            status=self.status,
            invoice_ref=self.invoice_ref,
            created_by=created_by,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at)
        )

    class Meta:
        db_table = "credit_orders"


class PaymentMethod(EnumField, models.CharField):
    def __init__(self, *args, **kwargs):
        roles = [
            ('dibs', 'Dibs'),
            ('admin', 'Admin')
        ]
        kwargs.setdefault('choices', roles)
        super(PaymentMethod, self).__init__(*args, **kwargs)


class Payments(models.Model):
    order_number = models.CharField(max_length=100, default=0)
    method = PaymentMethod(max_length=100)
    amount = models.FloatField()
    details = models.TextField()
    currency = models.CharField(max_length=32, null=True)
    transaction = models.CharField(max_length=100, null=True)
    invoice_ref = models.CharField(max_length=100, null=True)
    created_by = models.ForeignKey(Users, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def as_dict(self):
        created_by = self.created_by.as_dict() if self.created_by != None else ''
        return dict(
            id=self.id,
            order_number=self.order_number,
            method=self.method,
            amount=self.amount,
            details = self.details,
            invoice_ref=self.invoice_ref,
            created_by = created_by,
            created_at = str(self.created_at),
        )

    class Meta:
        db_table = "payments"


class CreditUsages(models.Model):
    ## order_number is where the cost applied
    order_number = models.CharField(max_length=100)
    credit_order = models.ForeignKey(CreditOrders)
    cost = models.FloatField()
    created_at = models.DateField(auto_now_add=True)

    def as_dict(self):
        return dict(
            id=self.id,
            order_number=self.order_number,
            credit_order=self.credit_order.as_dict(),
            cost=self.cost,
            created_at=str(self.created_at)
        )

    class Meta:
        db_table = 'credit_usages'


class SessionClasses(models.Model):
    session = models.ForeignKey(Session)
    classname = models.ForeignKey(CustomClasses)

    def as_dict(self):
        return dict(
            id=self.id,
            classname=self.classname.as_dict(),
            session=self.session.as_dict()
        )

    class Meta:
        db_table = "session_has_classes"


class PaymentSettings(models.Model):
    currency = models.CharField(max_length=10)
    merchant_id = models.CharField(max_length=100)
    payment_types = models.CharField(max_length=100)
    key1 = models.CharField(max_length=100)
    key2 = models.CharField(max_length=100)
    event = models.ForeignKey(Events)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Users)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return dict(
            id=self.id,
            currency=self.currency,
            merchant_id=self.merchant_id,
            payment_types=self.payment_types,
            key1=self.key1,
            key2=self.key2,
            event=self.event.as_dict(),
            created_by=self.created_by.as_dict(),
            created_at=str(self.created_at),
            updated_at=str(self.updated_at)

        )

    class Meta:
        db_table = 'payment_settings'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDL = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    # Reset
    Color_Off = "\033[0m"  # Text Reset

    # Regular Colors
    Black = "\033[0;30m"  # Black
    Red = "\033[0;31m"  # Red
    Green = "\033[0;32m"  # Green
    Yellow = "\033[0;33m"  # Yellow
    Blue = "\033[0;34m"  # Blue
    Purple = "\033[0;35m"  # Purple
    Cyan = "\033[0;36m"  # Cyan
    White = "\033[0;37m"  # White

    # Bold
    BBlack = "\033[1;30m"  # Black
    BRed = "\033[1;31m"  # Red
    BGreen = "\033[1;32m"  # Green
    BYellow = "\033[1;33m"  # Yellow
    BBlue = "\033[1;34m"  # Blue
    BPurple = "\033[1;35m"  # Purple
    BCyan = "\033[1;36m"  # Cyan
    BWhite = "\033[1;37m"  # White

    # Underline
    UBlack = "\033[4;30m"  # Black
    URed = "\033[4;31m"  # Red
    UGreen = "\033[4;32m"  # Green
    UYellow = "\033[4;33m"  # Yellow
    UBlue = "\033[4;34m"  # Blue
    UPurple = "\033[4;35m"  # Purple
    UCyan = "\033[4;36m"  # Cyan
    UWhite = "\033[4;37m"  # White

    # Background
    On_Black = "\033[40m"  # Black
    On_Red = "\033[41m"  # Red
    On_Green = "\033[42m"  # Green
    On_Yellow = "\033[43m"  # Yellow
    On_Blue = "\033[44m"  # Blue
    On_Purple = "\033[45m"  # Purple
    On_Cyan = "\033[46m"  # Cyan
    On_White = "\033[47m"  # White

    # High Intensty
    IBlack = "\033[0;90m"  # Black
    IRed = "\033[0;91m"  # Red
    IGreen = "\033[0;92m"  # Green
    IYellow = "\033[0;93m"  # Yellow
    IBlue = "\033[0;94m"  # Blue
    IPurple = "\033[0;95m"  # Purple
    ICyan = "\033[0;96m"  # Cyan
    IWhite = "\033[0;97m"  # White

    # Bold High Intensty
    BIBlack = "\033[1;90m"  # Black
    BIRed = "\033[1;91m"  # Red
    BIGreen = "\033[1;92m"  # Green
    BIYellow = "\033[1;93m"  # Yellow
    BIBlue = "\033[1;94m"  # Blue
    BIPurple = "\033[1;95m"  # Purple
    BICyan = "\033[1;96m"  # Cyan
    BIWhite = "\033[1;97m"  # White

    # High Intensty backgrounds
    On_IBlack = "\033[0;100m"  # Black
    On_IRed = "\033[0;101m"  # Red
    On_IGreen = "\033[0;102m"  # Green
    On_IYellow = "\033[0;103m"  # Yellow
    On_IBlue = "\033[0;104m"  # Blue
    On_IPurple = "\033[10;95m"  # Purple
    On_ICyan = "\033[0;106m"  # Cyan
    On_IWhite = "\033[0;107m"  # White

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDL = ''
        self.BOLD = ''
        self.UNDERLINE = ''

        self.Color_Off = ''
        self.Black = ''
        self.Red = ''
        self.Green = ''
        self.Yellow = ''
        self.Blue = ''
        self.Purple = ''
        self.Cyan = ''
        self.White = ''
        self.BBlack = ''
        self.BRed = ''
        self.BGreen = ''
        self.BYellow = ''
        self.BBlue = ''
        self.BPurple = ''
        self.BCyan = ''
        self.BWhite = ''
        self.UBlack = ''
        self.URed = ''
        self.UGreen = ''
        self.UYellow = ''
        self.UBlue = ''
        self.UPurple = ''
        self.UCyan = ''
        self.UWhite = ''
        self.On_Black = ''
        self.On_Red = ''
        self.On_Green = ''
        self.On_Yellow = ''
        self.On_Blue = ''
        self.On_Purple = ''
        self.On_Cyan = ''
        self.On_White = ''
        self.IBlack = ''
        self.IRed = ''
        self.IGreen = ''
        self.IYellow = ''
        self.IBlue = ''
        self.IPurple = ''
        self.ICyan = ''
        self.IWhite = ''
        self.BIBlack = ''
        self.BIRed = ''
        self.BIGreen = ''
        self.BIYellow = ''
        self.BIBlue = ''
        self.BIPurple = ''
        self.BICyan = ''
        self.BIWhite = ''
        self.On_IBlack = ''
        self.On_IRed = ''
        self.On_IGreen = ''
        self.On_IYellow = ''
        self.On_IBlue = ''
        self.On_IPurple = ''
        self.On_ICyan = ''
        self.On_IWhite = ''
