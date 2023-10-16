from django.shortcuts import redirect

### function to check if the user is logged in or not. If yes, User will continue using the website else he will be redirected to login page ###
def login_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('signin')
        elif request.user.is_authenticated == True:
            return function(request, *args, **kwargs)
        else:
            return redirect('signin')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
