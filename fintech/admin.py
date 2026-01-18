from django.contrib import admin
from .models import Account, Transaction, PixKey, IoTDevice, Card

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'balance', 'created_at')
    search_fields = ('account_number', 'user__username', 'user__email')
    readonly_fields = ('balance', 'account_number') # Saldo é somente leitura no admin para integridade

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'amount', 'sender', 'receiver', 'transaction_hash')
    list_filter = ('timestamp',)
    readonly_fields = ('transaction_hash', 'timestamp', 'sender', 'receiver', 'amount') # Ledger imutável
    search_fields = ('transaction_hash', 'sender__account_number', 'receiver__account_number')

@admin.register(PixKey)
class PixKeyAdmin(admin.ModelAdmin):
    list_display = ('key_value', 'key_type', 'account')

@admin.register(IoTDevice)
class IoTDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'device_id', 'owner_account', 'is_active')

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'account', 'expiration_date', 'is_active')
