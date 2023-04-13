from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from api.models import Appliance_Type

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello, world. You're at the main index.</h1>")
# ONly post air quality, management, budget, event logs 
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

# def appliance_type(request):
#     if request.method == 'POST':
#         title = request.POST.get('title')
#         wattage = request.POST.get('wattage')
#         gallons = request.POST.get('gallons')
#         is_active = request.POST.get('is_active')
#         appliance = Appliance.create(title, wattage, gallons, is_active)
#         appliance.save()
#         return JsonResponse({"code": "200", "message": "Appliance created successfully", "new_id": appliance.id})
#     elif request.method == 'GET':
#         try:
#             user = Appliance.objects.get(id=request.GET.get('id'))
#             return JsonResponse({"code": "200", "message": "Appliance found", "appliance": { "appname": appliance.appname, "wattage": appliance.wattage, "gallons": appliance.gallons}})
#         except Appliance.DoesNotExist:
#             return JsonResponse({"code": "404", "message": "Appliance not found"})
#     else:
#         return JsonResponse({"code": "400", "message": "Invalid request method"})
def appliance_type(request):
    if request.method == "POST":
        id = request.POST.get("id")
        title = request.POST.get("title")
        wattage = request.POST.get("wattage")
        gallons = request.POST.get("gallons")
        created_at = request.POST.get("created_at")
        is_active = request.POST.get("is_active")
    
  #  elif request.method == "GET":
      #  try:
            
    
    
        
        
        