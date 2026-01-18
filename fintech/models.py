from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import hashlib
import uuid

# --- FUNÇÃO PARA GERAR NÚMERO DE CONTA ---
def generate_account_number():
    """Gera um número de conta único e curto."""
    return str(uuid.uuid4())[:10].replace('-', '')

# --- MODELO: Account ---
class Account(models.Model):
    account_number = models.CharField(max_length=20, unique=True, default=generate_account_number)
    
    # BaaS Integration
    provider_account_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="ID no Provedor Bancário"
    )
    
    # [PYTHONJET FUSION] Link direto ao User
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bank_account',
        verbose_name="Usuário"
    )
    
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="Saldo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    def __str__(self):
        return f"Conta {self.account_number} ({self.user.username}) - Saldo: {self.balance:.2f}"

# --- MODELO: IoTDevice (Lazarus Integration) ---
class IoTDevice(models.Model):
    """
    Representa um dispositivo IoT (Lazarus Project) que pode transacionar.
    """
    device_id = models.CharField(max_length=100, unique=True, verbose_name="ID do Dispositivo")
    name = models.CharField(max_length=255, verbose_name="Nome do Dispositivo")
    
    # Security
    secret_token = models.CharField(max_length=255, verbose_name="Token Secreto (API Key)", default=uuid.uuid4)
    
    owner_account = models.ForeignKey(
        Account,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='iot_devices',
        verbose_name="Conta do Proprietário"
    )
    
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Localização")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    def __str__(self):
        return f"IoT: {self.name} ({self.device_id})"

# --- MODELO: PixKey ---
class PixKey(models.Model):
    """
    Chaves Pix para receber pagamentos.
    """
    KEY_TYPE_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
        ('EMAIL', 'E-mail'),
        ('PHONE', 'Telefone'),
        ('RANDOM', 'Chave Aleatória'),
    ]
    key_type = models.CharField(max_length=10, choices=KEY_TYPE_CHOICES, verbose_name="Tipo de Chave")
    key_value = models.CharField(max_length=255, unique=True, verbose_name="Valor da Chave")
    
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='pix_keys', 
        verbose_name="Conta Associada"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")

    class Meta:
        verbose_name = "Chave Pix"
        verbose_name_plural = "Chaves Pix"
        unique_together = ('key_type', 'key_value')

    def __str__(self):
        return f"{self.key_type}: {self.key_value}"

# --- MODELO: Card ---
class Card(models.Model):
    """
    Cartão Virtual para compras no Marketplace.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='cards',
        verbose_name="Conta Associada"
    )
    card_number = models.CharField(
        max_length=16,
        unique=True,
        help_text="Número do cartão (fictício, 16 dígitos)",
        verbose_name="Número do Cartão"
    )
    pin = models.CharField(max_length=4, verbose_name="PIN")
    expiration_date = models.DateField(verbose_name="Validade")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cartão Fictício"
        verbose_name_plural = "Cartões Fictícios"

    def __str__(self):
        return f"Cartão {self.card_number}"

    def save(self, *args, **kwargs):
        if len(self.pin) != 4 or not self.pin.isdigit():
            raise ValidationError("O PIN deve conter exatamente 4 dígitos numéricos.")
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.is_active and self.expiration_date >= timezone.now().date()

    def validate_pin(self, submitted_pin):
        return self.pin == submitted_pin

# --- MODELO: Transaction (Ledger) ---
class Transaction(models.Model):
    """
    Ledger imutável.
    """
    sender = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.PROTECT, verbose_name="Remetente")
    receiver = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.PROTECT, verbose_name="Destinatário")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    
    TRANSACTION_TYPES = [
        ('TRANSFER', 'Transferência'),
        ('DEPOSIT', 'Depósito'),
        ('WITHDRAW', 'Saque'),
        ('PAYMENT', 'Pagamento'),
        ('PIX_SENT', 'Pix Enviado'),
        ('PIX_RECEIVED', 'Pix Recebido'),
        ('PURCHASE', 'Compra Marketplace'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='TRANSFER', verbose_name="Tipo")
    
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Data/Hora")
    
    # Segurança / Blockchain-like
    transaction_hash = models.CharField(max_length=64, unique=True, blank=True, verbose_name="Hash SHA256")
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Descrição")

    source_device = models.ForeignKey(
        IoTDevice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_transactions',
        verbose_name="Device Origem"
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Transação"
        verbose_name_plural = "Transações" 

    def __str__(self):
        return f"{self.amount:.2f} | {self.sender.user.username} -> {self.receiver.user.username}"

    def _generate_transaction_hash(self):
        """Gera um hash único baseado nos dados da transação para garantir integridade."""
        data_string = f"{self.sender.account_number}{self.receiver.account_number}{self.amount}{self.timestamp}{self.description or ''}"
        return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.transaction_hash:
            self.transaction_hash = self._generate_transaction_hash()
        super().save(*args, **kwargs)

    def process_transaction(self):
        """Executa a movimentação financeira de forma atômica."""
        # Nota: Idealmente isso deve ser chamado dentro de um block transaction.atomic() externo
        if self.sender.balance >= self.amount:
            self.sender.balance -= self.amount
            self.receiver.balance += self.amount
            self.sender.save()
            self.receiver.save()
            self.save()
            return True
        return False

# --- MODELO: IdempotencyLog ---
class IdempotencyLog(models.Model):
    key = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_json = models.JSONField(default=dict)
    response_status = models.IntegerField()

    def __str__(self):
        return f"Idempotency Key: {self.key}"
