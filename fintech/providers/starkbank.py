from .base import BankingProvider
from decimal import Decimal
from typing import Dict, Any, Optional
import os

# Try to import starkbank, but don't fail if not installed yet (for CI/CD safety)
try:
    import starkbank
except ImportError:
    starkbank = None

class StarkBankProvider(BankingProvider):
    """
    Stark Bank Adapter for JetBank.
    Docs: https://starkbank.com/docs/api
    """

    def __init__(self):
        # Initialize credentials from ENV
        project_id = os.getenv("STARKBANK_PROJECT_ID")
        private_key = os.getenv("STARKBANK_PRIVATE_KEY_CONTENT")
        environment = os.getenv("STARKBANK_ENV", "sandbox")

        if starkbank and project_id and private_key:
            user = starkbank.Project(
                environment=environment,
                id=project_id,
                private_key=private_key
            )
            starkbank.user = user

    def create_account(self, name: str, tax_id: str) -> Dict[str, Any]:
        """
        Stark Bank doesn't have "sub-accounts" in the traditional sense for all plans.
        Usually we create a 'Corporate' account or just map internal ledger to one Stark Project.
        For MVP, we mock this mapping or use their specific API if available for the plan.
        """
        # For Sandbox, we will just return a mocked success, 
        # as opening real accounts needs manual approval.
        return {
            "provider_account_id": f"stark-mock-{tax_id}",
            "status": "pending_approval",
            "account_number": "N/A", # Provided later
            "tax_id": tax_id
        }

    def get_balance(self, account_id: str) -> Decimal:
        if not starkbank:
            return Decimal("0.00")
        
        balance = starkbank.balance.get()
        return Decimal(str(balance.amount)) / 100

    def transfer(self, sender_id: str, receiver_id: str, amount: Decimal) -> Dict[str, Any]:
        if not starkbank:
            raise Exception("StarkBank SDK not installed")

        # Convert to cents
        amount_cents = int(amount * 100)
        
        transfer = starkbank.Transfer(
            amount=amount_cents,
            tax_id=receiver_id, # Simplified: In real life needs name, bank_code, branch, account
            name=" Receiver Name", # TODO: Get from args
            bank_code="20018183", # Stark Bank Code (Example)
            branch_code="0001",
            account_number="123456" # TODO: Real data
        )
        
        created_transfer = starkbank.transfer.create([transfer])[0]
        
        return {
            "transaction_id": created_transfer.id,
            "status": created_transfer.status,
            "amount": str(amount),
            "fee": str(created_transfer.fee)
        }

    def generate_pix_key(self, account_id: str) -> Dict[str, Any]:
        # TODO: Implement Dynamic Pix QR Code generation
        return {
            "key": "random-uuid-key",
            "type": "random"
        }
