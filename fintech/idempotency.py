from functools import wraps
from django.http import JsonResponse
from django.utils import timezone
from .models import IdempotencyLog
import json

def idempotent(view_func):
    """
    Decorator to ensure idempotency based on 'Idempotency-Key' header.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method != 'POST':
            return view_func(request, *args, **kwargs)

        key = request.headers.get('Idempotency-Key')
        if not key:
            # If strictly required, return 400. For now, optional but recommended.
            return view_func(request, *args, **kwargs)

        # Check for existing key
        existing_log = IdempotencyLog.objects.filter(key=key).first()
        if existing_log:
            return JsonResponse(
                existing_log.response_json, 
                status=existing_log.response_status, 
                safe=False
            )

        # Process Request
        response = view_func(request, *args, **kwargs)

        # Save Response if successful (or even if failed, depending on policy)
        if 200 <= response.status_code < 300:
            # Only cache success for now? Or everything? 
            # Usually we cache everything to prevent re-execution.
            response_data = {}
            try:
                # Try to parse content if it's JSON
                if hasattr(response, 'content'):
                    response_data = json.loads(response.content)
                elif isinstance(response, JsonResponse):
                    # Accessing private data in JsonResponse is tricky without parsing content
                    response_data = json.loads(response.content)
            except:
                pass 

            IdempotencyLog.objects.create(
                key=key,
                response_json=response_data,
                response_status=response.status_code
            )

        return response
    return _wrapped_view
