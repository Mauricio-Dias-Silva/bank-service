from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Optional

class BankingProvider(ABC):
    """
    Abstract Base Class for Banking Providers (BaaS).
    Adapters (Stark Bank, Celcoin, Mock) must implement this interface.
    """

    @abstractmethod
    def create_account(self, name: str, tax_id: str) -> Dict[str, Any]:
        """Creates a banking account at the provider."""
        pass

    @abstractmethod
    def get_balance(self, account_id: str) -> Decimal:
        """Fetches the real balance at the provider."""
        pass

    @abstractmethod
    def transfer(self, sender_id: str, receiver_id: str, amount: Decimal) -> Dict[str, Any]:
        """Executes an internal transfer at the provider."""
        pass

    @abstractmethod
    def generate_pix_key(self, account_id: str) -> Dict[str, Any]:
        """Generates a random Pix key for the account."""
        pass
