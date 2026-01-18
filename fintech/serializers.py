from rest_framework import serializers
from .models import Account, Transaction, PixKey, Card

class AccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Bank Account.
    ReadOnly fields protect balance from client-side editing.
    """
    balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'provider_account_id', 'balance', 'invested_collateral', 'credit_limit', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'amount', 'transaction_type', 
                  'description', 'timestamp', 'transaction_hash', 'is_success']
        read_only_fields = ['transaction_hash', 'timestamp']
        
    def to_representation(self, instance):
        # Flatten sender/receiver for better mobile display
        representation = super().to_representation(instance)
        representation['sender_name'] = instance.sender.user.username
        representation['receiver_name'] = instance.receiver.user.username
        return representation

class PixKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = PixKey
        fields = ['id', 'key_type', 'key_value', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        account = BankingService.create_account(user)
        validated_data['account'] = account
        return super().create(validated_data)

class TransferSerializer(serializers.Serializer):
    """
    Serializer to validate Transfer Inputs (Action-based).
    """
    receiver_account = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(max_length=255, required=False)
