from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse

import environ
env = environ.Env()
environ.Env.read_env()

context = {}
context['project_name'] = env("PROJECT_NAME")
context['client_name'] = env("CLIENT_NAME")

def messageStore(request):
    if request.POST['message_type'] == 'success':
        messages.success(request, request.POST['message'])
    elif request.POST['message_type'] == 'error':
        messages.error(request, request.POST['message'])
    elif request.POST['message_type'] == 'debug':
        messages.debug(request, request.POST['message'])
    elif request.POST['message_type'] == 'warning':
        messages.warning(request, request.POST['message'])
    else:
        messages.info(request, request.POST['message'])
    context.update({'status': 200, 'message': "Flash Message Stored"})
    return JsonResponse(context)


def signin(request):
    context.update({
        'page_title': "Signin"
    })
    return render(request, 'auth/signin.html', context)


def signup(request):
    return render(request, 'auth/signup.html', context)


def custom_page_not_found_view(request, exception):
    context.update({'page_title': "404"})
    return render(request, "errors/404.html", context)


def custom_error_view(request, exception=None):
    context.update({'page_title': "500"})
    return render(request, "errors/500.html", context)


def custom_permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", {})


def custom_bad_request_view(request, exception=None):
    return render(request, "errors/400.html", {})
