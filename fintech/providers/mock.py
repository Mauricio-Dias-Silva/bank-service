from .base import BankingProvider
from decimal import Decimal
import uuid
import random
from typing import Dict, Any

class MockBankingProvider(BankingProvider):
    """
    In-memory Mock Provider for local development and testing.
    Simulates a real bank API response.
    """

    def create_account(self, name: str, tax_id: str) -> Dict[str, Any]:
        return {
            "provider_account_id": f"mock-{uuid.uuid4()}",
            "status": "active",
            "account_number": str(random.randint(100000, 999999)),
            "branch": "0001"
        }

    def get_balance(self, account_id: str) -> Decimal:
        # Returns a fake balance for testing
        return Decimal("1000.00")

    def transfer(self, sender_id: str, receiver_id: str, amount: Decimal) -> Dict[str, Any]:
        return {
            "transaction_id": f"tx-{uuid.uuid4()}",
            "status": "success",
            "amount": str(amount),
            "fee": "0.00"
        }

    def generate_pix_key(self, account_id: str) -> Dict[str, Any]:
        return {
            "key": str(uuid.uuid4()),
            "type": "random",
            "qr_code": "mock-qr-code-data"
        }
