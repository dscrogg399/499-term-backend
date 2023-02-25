from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from api.models import User

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello, world. You're at the main index.</h1>")

def user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = User.create(username, password, email)
        user.save()
        return JsonResponse({"code": "200", "message": "User created successfully", "new_id": user.id})
    elif request.method == 'GET':
        try:
            user = User.objects.get(id=request.GET.get('id'))
            return JsonResponse({"code": "200", "message": "User found", "user": { "username": user.username, "email": user.email}})
        except User.DoesNotExist:
            return JsonResponse({"code": "404", "message": "User not found"})
    else:
        return JsonResponse({"code": "400", "message": "Invalid request method"})

