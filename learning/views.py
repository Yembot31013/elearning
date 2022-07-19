from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Course, Profile, zoom_classes, Payed_class
from .form import SubscribersForm, ClassSubscribersForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip2 import GeoIP2


def courses(request):
    if request.method == 'POST':
        form = SubscribersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Great!!! for taking the right decision to subscribe')
            return redirect('/')
    else:
        form = SubscribersForm()
    if request.user.is_authenticated:
        check = Profile.objects.filter(user=request.user, statisfy=False)
        if check:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            device_type = ""
            brower_type = ""
            brower_version = ""
            os_type = ""
            os_version = ""
            
            if request.user_agent.is_mobile:
                device_type = "Mobile"
            if request.user_agent.is_tablet:
                device_type = "Tablet"
            if request.user_agent.is_pc:
                device_type = "PC"

            brower_type = request.user_agent.browser.family
            brower_version = request.user_agent.browser.version_string

            os_type = request.user_agent.os.family
            os_version = request.user_agent.os.version_string
            try:
                g=GeoIP2()
                result=g.city(ip)
                error = ""
                statisfy = True
                city = result['city']
                continent = result['continent_name']
                country = result['country_name']
                lat = result['latitude']
                lon = result['longitude']
                postal = result['postal_code']
                timeZone = result['time_zone']
            except Exception as e:
                error = e
                statisfy = False
                city=""
                continent=""
                country=""
                lat=""
                lon=""
                postal=""
                timeZone=""
            profile = Profile.objects.get(user=request.user)
            if (profile):
                profile.statisfy = statisfy
                profile.country = country
                profile.ipaddress=ip
                profile.longitude=lon
                profile.latitude=lat
                profile.os_type=os_type
                profile.browser_type=brower_type
                profile.device_type=device_type
                profile.brower_version=brower_version
                profile.os_version=os_version
                profile.error=error
                profile.continent=continent
                profile.city=city
                profile.postal=postal
                profile.timeZone=timeZone
                profile.save()
    cour = Course.objects.all()
    context = {
        'courses': cour,
        'form': form,
    }
    return render(request, 'course.html', context)

@login_required(login_url="loginpage")
def about(request, about_id):
    about_course = get_object_or_404(Course, pk=about_id)
    faq = about_course.frequently_asked_question_set.all()
    instructor = about_course.instructor_set.all()
    project = about_course.project_set.all()
    payeds = False
    payed = about_course.payed_class_set.filter(user = request.user, ordered = True)
    pays = Payed_class.objects.filter(user_id = request.user.id, course_id = about_id)
    zoom_class = about_course.zoom_classes_set.all()
    there_is_zoom = False
    if len(zoom_class) > 0:
        there_is_zoom = True
    else:
        there_is_zoom = False
        messages.success(request, "no zoom class is available for now")
    payment_id = None
    if len(pays) > 0:
        pays = get_object_or_404(Payed_class, user_id = request.user.id, course_id = about_id)
        payment_id = pays.id
    if len(payed) > 0:
        payeds = True
    else:
        payeds = False

    if request.method == 'POST':
        form = SubscribersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Great!!! for taking the right decision to subscribe')
            return redirect('/%s/' % (about_id))
    else:
        form = SubscribersForm()
    context = {
        'payment_id': payment_id,
        'payeds': payeds,
        'form': form,
        'faq': faq,
        'instructor': instructor,
        'abouts': about_course,
        'project': project,
        "there_is_zoom": there_is_zoom,
    }
    return render(request, 'aboutus.html', context)

@login_required(login_url="loginpage")
def enroll(request, enroll_id):
    pay_cour = get_object_or_404(Course, pk=enroll_id)
    payment = pay_cour.payment_set.all().order_by('amount')
    contest = {
        'objects': payment,
    }
    return render(request, 'payment/payment.html', contest)

@login_required(login_url="loginpage")
def upgrade_enroll(request, enroll_id, payment_id):
    pay_cour = get_object_or_404(Course, pk=enroll_id)
    payment_id = get_object_or_404(Payed_class, pk=payment_id)
    payment = pay_cour.payment_set.all().order_by('amount')
    amount = payment_id.final_price()
    price = payment_id.amount
    contest = {
        'objects': payment,
        'amount': amount,
        'price': price
    }
    return render(request, 'payment/update_payment.html', contest)

@login_required(login_url="loginpage")
def classes(request, about_id):
    if request.method=='POST' and request.POST.get('zoom_id'):
        zoom_id = int(request.POST.get('zoom_id'))
        user_id = int(request.user.id)
        course_id = request.POST.get('course_id')
        payed = get_object_or_404(Payed_class, user_id = user_id, course_id = course_id)
        z_class = zoom_classes.objects.get(zoom_id = zoom_id)
        z_class.has_started = True
        z_class.save()
        if payed.live_video():
            messages.success(request, 'enjoy your class')
            return JsonResponse({"status":"live", "id":zoom_id})
        else:
            messages.success(request, 'upgrade your bundle so that you can attend live class')
            return JsonResponse({"status":"video"})
    if request.method == 'POST':
        form = ClassSubscribersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Great!!! for taking the right decision to subscribe')
            return redirect('/%s/live_class' % (about_id))
    else:
        form = ClassSubscribersForm()
    zoom_cour = get_object_or_404(Course, pk=about_id)
    zoom = zoom_cour.zoom_classes_set.all().order_by('start_time').first()
    zoom_class = zoom_cour.zoom_classes_set.all().order_by('start_time')[1:]
    time = zoom.start_time
    time = time.timestamp()
    pays = Payed_class.objects.filter(user_id = request.user.id, course_id = about_id)
    payment_id = None
    if len(pays) > 0:
        pays = get_object_or_404(Payed_class, user_id = request.user.id, course_id = about_id)
        payment_id = pays.id
    context = {
        'zoom_classes': zoom_class,
        'payment_id': payment_id,
        'time': time,
        'zoom_id': zoom.zoom_id,
        'course_id': about_id,
        'form': form,
    }
    return render(request, 'counter/counter.html', context)

def video(request):
    context = {

    }
    return render(request, 'videos.html', context)

def no_class(request, about_id):
    if request.method == 'POST':
        form = ClassSubscribersForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Great!!! for taking the right decision to subscribe')
            return redirect('/%s/live_class' % (about_id))
    else:
        form = ClassSubscribersForm()
    zoom_cour = get_object_or_404(Course, pk=about_id)
    time = zoom_cour.starting_date
    time = time.timestamp()
    pays = Payed_class.objects.filter(user_id = request.user.id, course_id = about_id)
    zoom_class = zoom_cour.zoom_classes_set.all()
    payment_id = None
    if len(pays) > 0:
        pays = get_object_or_404(Payed_class, user_id = request.user.id, course_id = about_id)
        payment_id = pays.id
    if len(zoom_class) > 0 and len(pays) > 0:
        return redirect('/%s/live_class' % (about_id))

    elif len(pays) <= 0:
        messages.warn(request, 'make sure you buy your bundle before class started')
        return redirect('/')

    context = {
        'payment_id': payment_id,
        'time': time,
        'course_id': about_id,
        'form': form,
    }
    return render(request, 'counter/not_available.html', context)

