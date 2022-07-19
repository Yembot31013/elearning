
from django.contrib import admin
from .models import Course, Create_class, Expire_class, New_subscriber, News_for_new_subscriber, Payment, Unappove_course, Project, Frequently_asked_question, Instructor, Profile, Coupon, Payed_class, Bulked_class, Ban, Warn, Zoom_information, zoom_classes, subscribe_class
from datetime import datetime, timedelta, timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

USER_MODEL = get_user_model()

class ExtendedUserAdmin(UserAdmin):
    actions = [
        'ban_selected_users_permanently',
        'ban_selected_users_for_month',
        'ban_selected_users_for_week',
        'ban_selected_users_for_day',
        'warn_selected_users',
    ]

    def warn_selected_users(self, request, queryset):
        for user in queryset:
            Warn.objects.create(receiver=user, creator=request.user)
        self.message_user(request, "Successfully warned selected users.")

    def ban_selected_users_permanently(self, request, queryset):
        for user in queryset:
            Ban.objects.create(receiver=user, creator=request.user)
        self.message_user(request, "Successfully banned selected users permanently.")

    def ban_selected_users_for_month(self, request, queryset):
        self._ban(request, queryset, 30)
        self.message_user(request, "Successfully banned selected users for a month.")

    def ban_selected_users_for_week(self, request, queryset):
        self._ban(request, queryset, 7)
        self.message_user(request, "Successfully banned selected users for a week.")

    def ban_selected_users_for_day(self, request, queryset):
        self._ban(request, queryset, 1)
        self.message_user(request, "Successfully banned selected users for a day.")

    def _ban(self, request, queryset, days):
        end_date = datetime.now(timezone.utc) + timedelta(days=days)
        for user in queryset:
            Ban.objects.create(receiver=user, creator=request.user, end_date=end_date)


class BanAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'end_date', 'creator')


class WarnAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'creator')

class BulkedAdmin(admin.StackedInline):
    model = Bulked_class

class ProjectAdmin(admin.StackedInline):
    model = Project


class Frequently_asked_questionAdmin(admin.StackedInline):
    model = Frequently_asked_question


class NewAdmin(admin.StackedInline):
    model = News_for_new_subscriber


class PaymentAdmin(admin.StackedInline):
    model = Payment


class InstructorAdmin(admin.StackedInline):
    model = Instructor

class Create_classAdmin(admin.StackedInline):
    model = Create_class


class CourseAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'name', 'description', 'image'
            ),
        }),
        ('Starting Date', {
            "classes": ('collapse',),
            "fields": (
                'starting_date', 'as_started', 'about_to_start'
            ),
        }),
        ('Interested', {
            "classes": ('collapse',),
            "fields": (
                'number_of_bulks',
            ),
        }),
    )
    inlines = [BulkedAdmin, ProjectAdmin, PaymentAdmin,
               InstructorAdmin, Frequently_asked_questionAdmin, Create_classAdmin]


class NewAdmins(admin.ModelAdmin):
    fieldsets = (
        ('News Subscriber', {
            "fields": (
                'email', 'date'
            ),
        }),
    )
    inlines = [NewAdmin]


admin.site.register(Course, CourseAdmin)
admin.site.register(New_subscriber, NewAdmins)
admin.site.register(Unappove_course)
admin.site.register(Profile)
admin.site.register(Coupon)
admin.site.register(Payed_class)
admin.site.register(Expire_class)
admin.site.unregister(USER_MODEL)
admin.site.register(Zoom_information)
admin.site.register(zoom_classes)
admin.site.register(subscribe_class)
admin.site.register(USER_MODEL, ExtendedUserAdmin)

admin.site.register(Ban, BanAdmin)
admin.site.register(Warn, WarnAdmin)