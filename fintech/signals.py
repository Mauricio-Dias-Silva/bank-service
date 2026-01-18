from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Account

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_bank_account(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma conta bancária para cada novo usuário.
    """
    if created:
        pass
        # Account.objects.create(user=instance) # DISABLED: Let BankingService handle this to ensure Welcome Bonus & Provider ID
