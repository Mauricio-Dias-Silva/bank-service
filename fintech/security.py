from .models import IoTDevice
from django.core.exceptions import PermissionDenied

class IoTSecurityService:
    @staticmethod
    def authenticate_device(device_id, token):
        """
        Validates if the device_id matches the secret_token.
        """
        try:
            device = IoTDevice.objects.get(device_id=device_id)
            if device.secret_token == token and device.is_active:
                return device
            raise PermissionDenied("Token inválido ou dispositivo inativo.")
        except IoTDevice.DoesNotExist:
            raise PermissionDenied("Dispositivo não encontrado.")
            
    @staticmethod
    def rotate_token(device):
        """
        Rotates the secret token for a device (Security Best Practice).
        """
        import uuid
        new_token = str(uuid.uuid4())
        device.secret_token = new_token
        device.save()
        return new_token
