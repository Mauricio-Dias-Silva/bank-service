from decimal import Decimal
from django.utils import timezone
from .models import Transaction

class RuleEngine:
    @staticmethod
    def check_spending_limit(device, amount):
        """
        Simple rule: Daily spending limit.
        Hardcoded to 50.00 for prototype. 
        TODO: Move limit to IoTDevice model.
        """
        DAILY_LIMIT = Decimal("50.00")
        
        today = timezone.now().date()
        
        # Calculate usage today
        usage = sum(
            t.amount for t in Transaction.objects.filter(
                source_device=device,
                timestamp__date=today
            )
        )
        
        # Check if adding new amount exceeds limit
        if (usage + amount) > DAILY_LIMIT:
            return False, f"Limite diário excedido (Usado: {usage}, Limite: {DAILY_LIMIT})"
            
        return True, "Approved"
