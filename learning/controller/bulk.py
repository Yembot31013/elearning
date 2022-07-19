
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from learning.models import Bulked_class, Course


def bulkclass(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            courses_id = int(request.POST.get('course_id'))
            course_check = Course.objects.get(id=courses_id)
            if(course_check):
                if(Bulked_class.objects.filter(user=request.user.id, course_id=courses_id)):
                    return JsonResponse({'status': 'warning', 'message': 'You Have already bulked this class', 'heading': 'Warning!!!'})
                else:
                    Bulked_class.objects.create(
                        user_id=request.user.id, course_id=courses_id)
                    bulk_value = Bulked_class.objects.filter(course_id=courses_id)
                    total = bulk_value.count()
                    course_value = Course.objects.get(id=courses_id)
                    course_value.number_of_bulks = total
                    course_value.save()
                    return JsonResponse({'status': 'success', 'message': 'Course bulked successfully', 'heading': 'Good job!'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No such course found', 'heading': 'Oops!!!'})
        else:
            return JsonResponse({'status': 'warning', 'message': 'Login to Continue', 'heading': 'Warning!!!'})

    return redirect('/')
