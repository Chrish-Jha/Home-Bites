from .models import User


def session_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return User.objects.filter(id=user_id).first()


def require_session_user(request):
    user = session_user(request)
    if not user:
        return None
    return user
