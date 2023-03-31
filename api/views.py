from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django import forms

from api.models import Appliance
from api.validation_schema import MyValidationForm

# Create your views here.
def index(request):
    
    appliance_json = get_appliance_statuses()
    
    return HttpResponse(appliance_json)


# def user(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         email = request.POST.get('email')
#         user = User.create(username, password, email)
#         user.save()
#         return JsonResponse({"code": "200", "message": "User created successfully", "new_id": user.id})
#     elif request.method == 'GET':
#         try:
#             user = User.objects.get(id=request.GET.get('id'))
#             return JsonResponse({"code": "200", "message": "User found", "user": { "username": user.username, "email": user.email}})
#         except User.DoesNotExist:
#             return JsonResponse({"code": "404", "message": "User not found"})
#     else:
#         return JsonResponse({"code": "400", "message": "Invalid request method"})

def get_appliance_statuses():

    appliances = Appliance.objects.all()
    appliance_list = []

    for appliance in appliances:
        appliance_list.append({"id: ":appliance.id, "title: ":appliance.title,
                               "status: ":appliance.status, "x: ":appliance.x,
                               "y: ":appliance.y})

    return JsonResponse({"appliances": appliance_list})

    