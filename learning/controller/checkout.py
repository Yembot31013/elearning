import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from learning.form import CustomUserForm
from django.contrib.auth.decorators import login_required
from learning.models import Bulked_class, Coupon, Course, Expire_class, Payed_class
from learning.form import CouponForm
import random

@login_required(login_url = 'loginpage')
def index(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            courses_id = int(request.POST.get('course_id'))
            course_check = Course.objects.get(id=courses_id)
            if (course_check):
                payment_id = int(request.POST.get('payment_id'))
                payment_check = course_check.payment_set.get(id=payment_id)
                if (payment_check):
                    courses = get_object_or_404(Course, pk=courses_id)
                    payments = courses.payment_set.get(id=payment_id)
                    check_payment = Payed_class.objects.filter(user=request.user, course_id=courses.id)
                    if (check_payment):
                        paymenter = Payed_class.objects.get(user=request.user, course_id=courses.id)
                        paymenter.payment_id = payments.id
                        paymenter.save()
                        payment = Payed_class.objects.get(user=request.user, course_id=courses.id)
                    else:
                        payment = Payed_class.objects.create(user=request.user, course_id=courses.id, payment_id=payments.id, status='pg')
                        payment.save()
                    form = CouponForm()
                    contest = {
                        "course": courses,
                        "payment": payment,
                        'form': form,
                        'payments': payments,
                    }
                    return render(request, 'checkout/index.html', contest)
                messages.error(
                request, 'Error getting the payment info')
                return redirect('/')
            messages.warning(
            request, 'No such course found')
            return redirect('/')
        messages.warning(
        request, 'Login to Continue')
        return redirect('loginpage')
    return redirect('/')

@login_required(login_url = 'loginpage')
def upgrade_index(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            courses_id = int(request.POST.get('course_id'))
            course_check = Course.objects.get(id=courses_id)
            if (course_check):
                payment_id = int(request.POST.get('payment_id'))
                payment_check = course_check.payment_set.get(id=payment_id)
                if (payment_check):
                    courses = get_object_or_404(Course, pk=courses_id)
                    payments = courses.payment_set.get(id=payment_id)
                    check_payment = Payed_class.objects.filter(user=request.user, course_id=courses.id)
                    if (check_payment):
                        payment = Payed_class.objects.get(user=request.user, course_id=courses.id)
                        new_price = payments.get_final_price() - payment.amount
                        contest = {
                        "payment_profile": payment ,
                        "course": courses,
                        "payment": new_price,
                        "payments": payments,
                        }
                        return render(request, 'checkout/upgrade_index.html', contest)
                    else:
                        messages.error(request, 'You need to have a specific bundle first before upgrading')
                        return redirect('/')
                messages.error(
                request, 'Error getting the payment info')
                return redirect('/')
            messages.warning(
            request, 'No such course found')
            return redirect('/')
        messages.warning(
        request, 'Login to Continue')
        return redirect('loginpage')
    return redirect('/')

@login_required(login_url = 'loginpage')       
def AddCouponView(request):
    if request.method == 'POST':
        try:
            payments = int(request.POST.get('coupon'))
            course = int(request.POST.get('course'))
            codes = request.POST.get('codes')
            order = Payed_class.objects.get(user=request.user, ordered=False, pk=payments)
            try:
                coupons = Coupon.objects.get(code=codes, course_id=course, verlied=True)
                if (coupons):
                    order.coupon_id = coupons.id
                    order.save()
                    messages.success(request, "Successfully added coupon")
                    return JsonResponse({'status': 'Successfully added coupon'})
                else:
                    messages.info(request, "This coupon does not exist")
                    return JsonResponse({'status': 'This coupon does not exist'})   
            except:
                messages.info(request, "This coupon does not exist")
                return JsonResponse({'status': 'This coupon does not exist'})
        except Exception as e:
            print(request.POST.get('course'))
            print(e)
            messages.success(request, "sorry!!! an unknown error just occurs")
            return JsonResponse({'status': 'sorry!!! an unknown error just occurs'})
    # return JsonResponse({'status': 'This coupon no work'})


@login_required(login_url = 'loginpage')
def payment(request):
    if request.method == 'POST':
        course = request.POST.get('course')
        print(course)
        payments = int(request.POST.get('payment_id'))
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        country = request.POST.get('country')
        state = request.POST.get('state')
        zip = request.POST.get('zip')
        payment_mode = request.POST.get('payment_mode')
        neworder = Payed_class.objects.get(user=request.user, ordered=False, pk=payments, status='pg')
        neworder.fname = fname
        neworder.lname = lname
        neworder.uname = uname
        neworder.email = email
        neworder.address2 = address2
        neworder.city = city
        neworder.country = country
        neworder.state = state
        neworder.zip = zip
        neworder.payment_mode = payment_mode
        neworder.status = 'pd'
        neworder.ordered = True
        neworder.ordered_date = datetime.datetime.now()
        refcode = 'yembot' + str(random.randint(11111111111, 999999999999))
        while Payed_class.objects.filter(ref_code=refcode) is None or Expire_class.objects.filter(ref_code=refcode) is None:
            refcode = 'yembot' + str(random.randint(11111111111, 999999999999))
        neworder.ref_code = refcode
        neworder.save()
        try:
            bulkclass = Bulked_class.objects.filter(user=request.user, course_id=course.id)
            bulkclass.delete()
        except:
            pass
        messages.success(request, "Your course has been paided successfully")

    return redirect('/')

@login_required(login_url = 'loginpage')
def upgrade_payment(request):
    if request.method == 'POST':
        course = int(request.POST.get('course'))
        payments = int(request.POST.get('payment_id'))
        payment_mode = request.POST.get('payment_mode')
        neworder = Payed_class.objects.filter(user=request.user, course_id=course, status='pd')
        if len(neworder) > 0:
            neworder = Payed_class.objects.get(user=request.user, course_id=course, status='pd')
            neworder.payment_id = payments
            neworder.payment_mode = payment_mode
            neworder.update_date = datetime.datetime.now()
            neworder.save()
            messages.success(request, "Your bundle has been upgraded successfully")
        else:
            messages.error(request, "Unable to upgrade your bundle")
    return redirect('/')