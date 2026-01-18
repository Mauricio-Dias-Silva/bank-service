from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Account, Transaction, PixKey, Card
import hashlib
import uuid
from django.core.exceptions import ValidationError

class BankingService:
    @staticmethod
    def create_account(user):
        """
        Creates a new bank account for a user.
        Generates a unique account number.
        """
        # Check if account already exists
        if hasattr(user, 'bank_account'):
            return user.bank_account

        # Generate unique account number (simple logic for now)
        # Format: 7 digits + 1 check digit (e.g., 1234567-8)
        # Using UUID integer for randomness
        account_number = str(uuid.uuid4().int)[:7] 
        # Ensure Uniqueness loop could be here
        
        account = Account.objects.create(
            user=user,
            account_number=account_number,
            # agency removed
            balance=Decimal('1000.00'), # Welcome Bonus!
            # account_type removed
        )
        return account

    @staticmethod
    def get_balance(user):
        if hasattr(user, 'bank_account'):
            return user.bank_account.balance
        return Decimal('0.00')

    @staticmethod
    def process_transfer(sender_user, receiver_account_number, amount, description=""):
        """
        Processes a transfer between accounts.
        """
        amount = Decimal(amount)
        if amount <= 0:
            raise ValidationError("O valor deve ser positivo.")

        sender_account = getattr(sender_user, 'bank_account', None)
        if not sender_account:
            raise ValidationError("Remetente não possui conta bancária.")

        if sender_account.balance < amount:
            raise ValidationError("Saldo insuficiente.")

        try:
            receiver_account = Account.objects.get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            raise ValidationError("Conta de destino não encontrada.")

        if sender_account == receiver_account:
            raise ValidationError("Não pode transferir para a mesma conta.")

        with transaction.atomic():
            # Debit
            sender_account.balance -= amount
            sender_account.save()

            # Credit
            receiver_account.balance += amount
            receiver_account.save()

            # Ledger
            LedgerService.record_transaction(
                sender=sender_account,
                receiver=receiver_account,
                amount=amount,
                transaction_type='TRANSFER',
                description=description
            )

        return True

class LedgerService:
    @staticmethod
    def record_transaction(sender, receiver, amount, transaction_type='TRANSFER', description=""):
        # Generate Hash
        # SHA256(sender + receiver + amount + timestamp + nonce)
        # Ideally, we link to previous hash for blockchain-like integrity, but simpler for now.
        
        timestamp = timezone.now()
        data_string = f"{sender.id}{receiver.id}{amount}{timestamp.isoformat()}{uuid.uuid4()}"
        tx_hash = hashlib.sha256(data_string.encode()).hexdigest()

        Transaction.objects.create(
            sender=sender,
            receiver=receiver,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            timestamp=timestamp,
            transaction_hash=tx_hash,
            # is_success removed
        )

class IoTWalletService:
    """
    Handles machine-to-machine payments.
    """
    @staticmethod
    def process_machine_payment(device_id, receiver_account_number, amount, description="IoT Payment"):
        """
        Executes a payment initiated by an IoT Machine.
        """
        try:
            device = IoTDevice.objects.get(device_id=device_id, is_active=True)
        except IoTDevice.DoesNotExist:
            raise ValidationError("Dispositivo não encontrado ou inativo.")
            
        if not device.owner_account:
            raise ValidationError("Dispositivo sem conta vinculada.")
            
        sender_account = device.owner_account
        amount = Decimal(amount)
        
        # Reuse BankingService logic but we need to inject source_device into the transaction
        # So we can't strictly use process_transfer unless we modify it or copy logic.
        # Let's copy atomic logic for granular control of 'source_device' field.
        
        try:
            receiver_account = Account.objects.get(account_number=receiver_account_number)
        except Account.DoesNotExist:
            raise ValidationError("Conta destinatária inválida.")

        if sender_account.balance < amount:
            raise ValidationError(f"Saldo insuficiente na conta do dispositivo (Saldo: {sender_account.balance})")

        with transaction.atomic():
            sender_account.balance -= amount
            receiver_account.balance += amount
            
            sender_account.save()
            receiver_account.save()
            
            # Record with Source Device
            timestamp = timezone.now()
            data_string = f"{sender_account.id}{receiver_account.id}{amount}{timestamp.isoformat()}{device.id}"
            tx_hash = hashlib.sha256(data_string.encode()).hexdigest()
            
            Transaction.objects.create(
                sender=sender_account,
                receiver=receiver_account,
                amount=amount,
                transaction_type='PAYMENT', # Machine Payment
                description=f"[IoT] {device.name}: {description}",
                timestamp=timestamp,
                transaction_hash=tx_hash,
                source_device=device
            )
            
        return True
