from django.urls import path
from . import views
from learning.controller import authview, checkout, bulk, zoom

urlpatterns = [
    path('', views.courses, name='home'),
    path('', views.courses, name='courses'),
    path('<int:about_id>/', views.about, name="about"),
    path('register/', authview.register, name="register"),
    path('login/', authview.loginpage, name="loginpage"),
    path('logout/', authview.logoutpage, name="logoutpage"),
    path('<int:enroll_id>/enroll/', views.enroll, name="enroll"),
    path('<int:enroll_id>/upgrade_enroll/<int:payment_id>', views.upgrade_enroll, name="upgrade_enroll"),
    path('checkout', checkout.index, name="checkout"),
    path('checkouts', checkout.upgrade_index, name="upgrade_checkout"),
    path('coupon/', checkout.AddCouponView, name="coupon"),

    path('join_live/<int:zoom_id>/', zoom.join_classes, name="join_zoom_live"),

    path('start_live/<int:zoom_id>/', zoom.start_classes, name="start_zoom_live"),

    path('place-order', checkout.payment, name="placeholder"),

    path('upgrade', checkout.upgrade_payment, name="placeorder"),
    path('<int:about_id>/live_class', views.classes, name='classes'),
    path('video', views.video, name='video'),
    path('<int:about_id>/no_class_available', views.no_class, name='no_class'),

    path('bulk', bulk.bulkclass, name='bulk'),

]
