from rest_framework import authentication, exceptions

from core.models.user import User


class UserIdHeaderAuthentication(authentication.BaseAuthentication):
    """Resolve the request's user from the ``X-User-Id`` header.

    ``core.User`` is a plain data model (not Django's auth user model), so
    this lightweight lookup stands in for real authentication. Requests
    without a valid header are rejected with ``401``.
    """

    keyword = "X-User-Id"

    def authenticate(self, request):
        raw_user_id = request.META.get("HTTP_X_USER_ID")
        if raw_user_id is None:
            raise exceptions.AuthenticationFailed(
                f"Missing {self.keyword} header."
            )

        try:
            user = User.objects.get(id_user=raw_user_id)
        except (User.DoesNotExist, ValueError):
            raise exceptions.AuthenticationFailed(
                f"Invalid {self.keyword} header."
            )

        return (user, None)

    def authenticate_header(self, request):
        return self.keyword
