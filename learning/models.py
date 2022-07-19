from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from .utils import get_random_code
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from datetime import datetime, timezone
from django.conf import settings
from django.db.models import Q
from django_zoom_meetings import ZoomMeetings

# from django_countries.fields import CountryField

def create_zoom(date, topic, meeting_duration, meeting_password):
        info = Zoom_information.objects.all()[0]
        api = info.api_key
        secret = info.secret_key
        email = info.zoom_email_address
        if api and secret and email:
            my_zoom = ZoomMeetings(api, secret, email)
            create_meet = my_zoom.CreateMeeting(date, topic, meeting_duration, meeting_password)
            return create_meet
        else:
            return

@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, *args, **kwargs):
    if created:
        p = Profile.objects.create(user=instance)
        p.save()

class Ban(models.Model):
    receiver = models.OneToOneField(User, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, related_name='ban_creator', null=True, blank=True, default=None, on_delete=models.CASCADE)
    end_date = models.DateTimeField(null=True, blank=True, default=None)

class Warn(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, related_name='warn_creator', on_delete=models.CASCADE)

@receiver(pre_save, sender=Ban)
def pre_save_ban(sender, instance, **kwargs):
    try:
        ban = Ban.objects.get(receiver=instance.receiver)
        if instance.end_date is None or instance.end_date > ban.end_date:
            ban.delete()
        else:
            instance.delete()
    except Ban.DoesNotExist:
        pass

    instance.receiver.is_active = False


@receiver(post_delete, sender=Ban)
def post_delete_ban(sender, instance, **kwargs):
    instance.receiver.is_active = True


@receiver(pre_save, sender=Warn)
def pre_save_warn(sender, instance, **kwargs):
    threshold = getattr(settings, 'WARNS_THRESHOLD', None)

    if threshold:
        warns = Warn.objects.filter(receiver=instance.receiver)

        if warns.count() >= threshold-1:
            Ban.objects.create(receiver=instance.receiver)
            warns.delete()
            instance.delete()

    if instance:
        now = datetime.now(timezone.utc)
        bans = Ban.objects.filter(receiver=instance.receiver).filter(Q(end_date__isnull=True) | Q(end_date__gt=now))
        if bans.count() > 0:
            instance.delete()


class Course(models.Model):
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    name = models.CharField(max_length=150, null=False, blank=False)
    number_of_bulks = models.IntegerField(default=0, null=False, blank=False)
    about_to_start = models.BooleanField(default=False)
    as_started = models.BooleanField(default=False)
    starting_date = models.DateTimeField(
        'starting date', null=True, blank=True)
    payment_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Unappove_course(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    description = models.TextField(blank=False)
    image = models.ImageField(
        upload_to='testing_images/', null=True, blank=True)
    name = models.CharField(max_length=150, null=False, blank=False)
    about_to_start = models.BooleanField(default=False)
    as_started = models.BooleanField(default=False)
    starting_date = models.DateTimeField(
        'starting date', null=True, blank=True)
    payment_expired = models.BooleanField(default=False)
    approve = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Project(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    topic = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True)

    def __str__(self):
        return "%s_%s" % (self.course, self.topic)


class Frequently_asked_question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    question = models.CharField(max_length=150, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s-%s" % (self.course, self.question)


class Instructor(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='teams/', null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    facebook = models.URLField(max_length=200, null=True, blank=True)
    linkedln = models.URLField(max_length=200, null=True, blank=True)
    twitter = models.URLField(max_length=200, null=True, blank=True)
    instagram = models.URLField(max_length=200, null=True, blank=True)


class Payment(models.Model):
    FREE = 'FR'
    PREMIUM = 'PE'
    PRO = 'PR'
    ENTERPRISE = 'EN'

    PAYMENT_TYPE_CHOICES = [
        ('Free', FREE),
        ('Premium', PREMIUM),
        ('Pro', PRO),
        ('Enterprise', ENTERPRISE),
    ]
    COLOUR = [
        ('primary', 'primary'),
        ('secondary', 'secondary'),
        ('danger', 'danger'),
        ('dark', 'dark'),
        ('light', 'light'),
    ]
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    payment_type = models.CharField(
        max_length=10, choices=PAYMENT_TYPE_CHOICES, default='Free')
    color = models.CharField(
        max_length=9, choices=COLOUR, default='primary')

    # def is_upperclass(self):
    #     return self.payment_type in {self.PREMIUM, self.PRO}
    amount = models.FloatField(null=True, blank=True)
    discount = models.FloatField(null=True, blank=True)
    expired_date = models.DateTimeField(auto_now=False, auto_now_add=False)

    allow_to_watch_download_video = models.BooleanField(default=False)
    allow_to_live_class = models.BooleanField(default=False)
    access_assignment = models.BooleanField(default=False)
    allow_to_access_career_page = models.BooleanField(default=False)
    get_access_certificate = models.BooleanField(default=False)
    get_access_forum = models.BooleanField(default=False)
    get_access_editor = models.BooleanField(default=False)

    def __str__(self):
        return self.payment_type
    def get_final_price(self):
        price = self.amount
        if self.discount:
            price -= self.discount
        return price

class New_subscriber(models.Model):
    email = models.EmailField(max_length=150, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class News_for_new_subscriber(models.Model):
    send_to = models.ForeignKey(
        New_subscriber, on_delete=models.CASCADE, null=True)
    SENDER_CHOICES = [
        ('al', 'all'),
        ('st', send_to),
    ]
    sending_to = models.CharField(
        max_length=2, choices=SENDER_CHOICES, default='al')
    heading = models.CharField(max_length=150, null=True, blank=True)
    new = models.TextField(null=True, blank=True)
    send_date = models.DateTimeField(
        auto_now_add=False, auto_now=False, blank=True, null=True)
    send = models.BooleanField(default=False)

    def __str__(self):
        return self.heading


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    zoomUserName = models.CharField(max_length=150, null=True, blank=True)
    postal = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    timeZone = models.CharField(max_length=50, null=True, blank=True)
    continent = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.ImageField(default='avatar.png', upload_to='user_img/', null=True, blank=True)
    ipaddress = models.CharField(max_length=20, blank=True, null=True)
    error = models.CharField(max_length=50, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    os_type = models.CharField(max_length=150, blank=True, null=True)
    os_version = models.CharField(max_length=150, blank=True, null=True)
    browser_type = models.CharField(max_length=150, blank=True, null=True)
    brower_version = models.CharField(max_length=150, blank=True, null=True)
    device_type = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    bio = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    statisfy = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}-{self.created}"
    
    def save(self, *args, **kwargs):
        ex = False
        if self.first_name and self.last_name:
            to_slug = slugify(str(self.first_name)+ " " + str(self.last_name))
            ex = Profile.objects.filter(slug=to_slug).exists()
            while ex:
                to_slug = slugify(to_slug + " " + str(get_random_code()))
                ex = Profile.objects.filter(slug=to_slug).exists()
        else:
            to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)


class Bulked_class(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    bulk_at = models.DateTimeField(auto_now_add=True)
    is_pay = models.BooleanField(default=False)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=False)

class Coupon(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    verlied = models.BooleanField(default=True, null=True)

    def __str__(self):
        return self.code

class Payed_class(models.Model):
    PAYMENT_STATUS = [
        ('np', 'not paided'),
        ('pg', 'pending'),
        ('ep', 'expired'),
        ('pd', 'paid'),
    ]
    status = models.CharField(
        max_length=2, choices=PAYMENT_STATUS, default='np')
    ref_code = models.CharField(unique=True, max_length=20, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    fname = models.CharField(max_length=150, null=True, blank=False)
    lname = models.CharField(max_length=150, null=True, blank=False)
    uname = models.CharField(max_length=150, null=True, blank=False)
    email = models.CharField(max_length=150, null=True, blank=False)
    address2 = models.TextField(null=True)
    city = models.CharField(max_length=150, null=True, blank=False)
    state = models.CharField(max_length=150, null=True, blank=False)
    country = models.CharField(max_length=150, null=True, blank=False)
    # country = CountryField(blank_label='(Choose...)', null=False)
    zip = models.CharField(max_length=150, null=True, blank=False)
    payment_mode = models.CharField(max_length=150, null=True, blank=False)
    amount = models.FloatField(blank=True, null=True)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}-{self.course.name}-{self.payment.payment_type}"

    
    def save(self, *args, **kwargs):  
        total = 0
        total += self.payment.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        self.amount = total
        super().save(*args, **kwargs)

    def final_price(self):
        course = self.payment.get_final_price()
        return course
    def live_video(self):
        course = self.payment.allow_to_live_class
        return course
    def watch_download_video(self):
        course = self.payment.allow_to_watch_download_video
        return course
    def access_assignment(self):
        course = self.payment.access_assignment
        return course
    def access_career_page(self):
        course = self.payment.allow_to_access_career_page
        return course
    def get_access_certificate(self):
        course = self.payment.get_access_certificate
        return course
    def get_access_forum(self):
        course = self.payment.get_access_forum
        return course
    def get_access_editor(self):
        course = self.payment.get_access_editor
        return course


class Expire_class(models.Model):
    ref_code = models.CharField(unique=True, max_length=20, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    fname = models.CharField(max_length=150, null=True, blank=False)
    lname = models.CharField(max_length=150, null=True, blank=False)
    uname = models.CharField(max_length=150, null=True, blank=False)
    email = models.CharField(max_length=150, null=True, blank=False)
    address2 = models.TextField(null=True)
    city = models.CharField(max_length=150, null=True, blank=False)
    state = models.CharField(max_length=150, null=True, blank=False)
    country = models.CharField(max_length=150, null=True, blank=False)
    # country = CountryField(blank_label='(Choose...)', null=False)
    zip = models.CharField(max_length=150, null=True, blank=False)
    payment_mode = models.CharField(max_length=150, null=True, blank=False)
    amount = models.FloatField(blank=True, null=True)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, blank=True, null=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    expired_date = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}-{self.course.name}-{self.payment.payment_type}"

class Create_class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, blank=False)
    topic = models.CharField(max_length=150, null=False, blank=False)
    duration = models.IntegerField(null=False, blank=False)
    password = models.CharField(max_length=150, null=False, blank=False)


@receiver(post_save, sender=Create_class)
def create_zoom_class(sender, instance, **kwargs):
    course = instance.course
    date = instance.date
    topic = instance.topic
    meeting_duration = instance.duration
    meeting_duration = int(meeting_duration)
    if meeting_duration > 40:
        meeting_duration = 40
        print("new duration: " + str(meeting_duration))
    meeting_password = instance.password
    if create_zoom(date, topic, meeting_duration, meeting_password) is None:
        pass
    else:
        try:
            zoom = create_zoom(date, topic, meeting_duration, meeting_password)
            print(zoom)
            classe = zoom_classes.objects.create(course=course, zoom_id = zoom['id'], host_email = zoom['host_email'], topic = zoom['topic'], start_time=zoom['start_time'], duration = zoom['duration'], created_at = zoom['created_at'], start_url = zoom['start_url'], join_url = zoom['join_url'], password = zoom['password'])
            classe.save()
        except Exception as e:
            print("error: ")
            print(e)

class zoom_classes(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    zoom_id = models.IntegerField(null=True, blank=False)
    host_email = models.EmailField(max_length=150, null=True, blank=False)
    topic = models.CharField(max_length=100, null=True, blank=False)
    start_time = models.DateTimeField(null=True, blank=False)
    duration = models.IntegerField()
    created_at = models.DateTimeField(null=True, blank=False)
    start_url = models.URLField(max_length=1000, null=True, blank=False)
    join_url = models.URLField(max_length=1000, null=True, blank=False)
    password = models.CharField(max_length=20, null=True, blank=False)
    has_started = models.BooleanField(default=False)
    has_ended = models.BooleanField(default=False)
    next_to_start = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.course.name}-{self.host_email}-{self.topic}-{self.zoom_id}"

class subscribe_class(models.Model):
    name = models.CharField(max_length=150, null=True, blank=False)
    email = models.EmailField(max_length=150, null=True, blank=False, unique=True)
    
    def __str__(self):
        return self.name

class Zoom_information(models.Model):
    api_key = models.CharField(max_length=100, null=True, blank=False)
    secret_key = models.CharField(max_length=100, null=True, blank=False)
    sdk_key = models.CharField(max_length=100, null=True, blank=False)
    verification_token = models.CharField(max_length=100, null=True, blank=False)
    zoom_email_address = models.EmailField(max_length=50, null=True, blank=False)

    def __str__(self):
        return self.zoom_email_address



@receiver(post_save, sender=Payed_class)
def delete_payed_course(sender, instance, **kwargs):
    try:
        expire = Payed_class.objects.get(ref_code=instance.ref_code)
        if instance.status == 'ep':
            expire.delete()
    except Payed_class.DoesNotExist:
        pass
    except Exception as e:
        print(e)

@receiver(post_save, sender=Coupon)
def validate_coupon(sender, instance, **kwargs):
    course = Course.objects.filter(pk=instance.course_id)
    if len(course) > 0:
        course = get_object_or_404(Course, pk=instance.course_id)
        payment = course.payment_set.all().order_by('amount').first()
        pay_price = payment.get_final_price()
        coupon_price = instance.amount
        if coupon_price > (pay_price + 10):
            instance.delete()
            
    else:
        instance.delete()

@receiver(pre_delete, sender=Payed_class)
def create_expire_course(sender, instance, **kwargs):
    if instance.status == 'ep':
        expired = Expire_class.objects.create(ref_code = instance.ref_code, user = instance.user, course = instance.course, fname = instance.fname, lname = instance.lname, uname = instance.uname, email = instance.email, address2 = instance.address2, city = instance.city, state = instance.state, country = instance.country, zip = instance.zip, payment_mode = instance.payment_mode, amount = instance.amount, coupon = instance.coupon, payment = instance.payment, ordered_date = instance.ordered_date)
        expired.save()














