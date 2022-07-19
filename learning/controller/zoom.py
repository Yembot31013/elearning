from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from learning.form import CustomUserForm
import hashlib
import hmac
import base64
import time
from django.contrib.auth.decorators import login_required
from learning.models import Course, Payed_class, Zoom_information, zoom_classes, Profile

def generateSignature(data):
  ts = int(round(time.time()*1000))-3000
  msg = data['apiKey'] + str(data['meetingNumber'])+str(ts)+ str(data['role'])
  message = base64.b64encode(bytes(msg, 'utf-8'))
  secret = bytes(data["apiSecret"], 'utf-8')
  hash = hmac.new(secret, message, hashlib.sha256)
  hash = base64.b64encode(hash.digest())
  hash = hash.decode("utf-8")
  tmpString = "%s.%s.%s.%s.%s" % (data["apiKey"], str(data["meetingNumber"]), str(ts), str(data["role"]), hash)
  signature = base64.b64encode(bytes(tmpString, "utf-8"))
  signature = signature.decode("utf-8")
  return signature.rstrip("=")

  # data = {
  #   "apiKey":"",
  #   "apiSecret": "",
  #   "meetingNumber": 888,
  #   "role": 0
  # }
  # generateSignature(data)

@login_required(login_url="loginpage")
def join_classes(request, zoom_id):
  user = request.user.id
  profile = Profile.objects.get(user_id = user)
  z_class = zoom_classes.objects.get(zoom_id = zoom_id)
  course_id = z_class.course.id
  u_class = Payed_class.objects.get(user_id = user, course_id = course_id)
  zoom_cred = Zoom_information.objects.all().first()
  apiKey = zoom_cred.api_key
  apiSecret = zoom_cred.secret_key
  zoomProfile = profile.zoomUserName

  if u_class.live_video():
    messages.success(request, "enjoy your class")
  else:
    messages.error(request, "upgrade your bundle so that you can access live class")
    return redirect("/")

  zoomNumber = z_class.zoom_id
  passWord = z_class.password
  sdkKey = zoom_cred.sdk_key

  data = {
   "apiKey":apiKey,
   "apiSecret": apiSecret,
   "meetingNumber": zoomNumber,
   "role": 0
 }
  signature = generateSignature(data)

  context={
    "zoomProfile": zoomProfile,
    "sdkKey" : sdkKey,
    "signature": signature,
    "passWord": passWord,
    "zoomNumber": zoomNumber,
    "user": request.user,
  }
  return render(request, 'zoom/join_index.html', context)

@login_required(login_url="loginpage")
def start_classes(request, zoom_id):
  user = request.user.id
  profile = Profile.objects.get(user_id = user)
  z_class = zoom_classes.objects.get(zoom_id = zoom_id)
  zoom_cred = Zoom_information.objects.all().first()
  apiKey = zoom_cred.api_key
  apiSecret = zoom_cred.secret_key
  zoomNumber = z_class.zoom_id
  passWord = z_class.password
  sdkKey = zoom_cred.sdk_key
  zoomProfile = profile.zoomUserName

  data = {
   "apiKey":apiKey,
   "apiSecret": apiSecret,
   "meetingNumber": zoomNumber,
   "role": 1
 }
  signature = generateSignature(data)
  takToken = zoom_cred.verification_token


  context={
    "zoomProfile": zoomProfile,
    "sdkKey" : sdkKey,
    "signature": signature,
    "passWord": passWord,
    "zoomNumber": zoomNumber,
    "takToken": takToken,
    "user": request.user,
  }
  return render(request, 'zoom/start_index.html', context)