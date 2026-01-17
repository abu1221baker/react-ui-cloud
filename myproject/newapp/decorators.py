from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is in any of the allowed groups
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(role in user_groups for role in allowed_roles):
                return view_func(request, *args, **kwargs)
            
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        return _wrapped_view
    return decorator
