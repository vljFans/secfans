from .models import User
from django.db.models import Q


class AuthBackend(object):
    supports_object_permissions = True
    supports_anonymous_user = False
    supports_inactive_user = False

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, username, password):
        try:
            users = User.objects.filter(
                Q(username=username) | Q(email=username) | Q(phone=username)
            )
        except:
            users = []
        if len(users) == 0:
            user = None
        elif len(users) > 1:
            user = users.filter(pswd_token=password).first()
        else:
            user = users[0]
        return user if user is not None and user.check_password(password) else None
        # try:
        #     user = User.objects.get(username=username)
        # except:
        #     user = None
        # return user if user is not None and user.check_password(password) else None
