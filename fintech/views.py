from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from .models import Account, Transaction, IoTDevice
from .services import BankingService, LedgerService, IoTWalletService
from decimal import Decimal
from django.db.models import Q

@login_required
def bank_dashboard(request):
    """
    Main dashboard for the 'Bank of PythonJet'.
    Shows balance, recent transactions, and quick actions.
    """
    # Ensure account exists
    account = BankingService.create_account(request.user)
    
    # Get recent transactions (sent or received)
    transactions = Transaction.objects.filter(
        Q(sender=account) | Q(receiver=account)
    ).order_by('-timestamp')[:10]

    context = {
        'account': account,
        'transactions': transactions,
    }
    return render(request, 'dashboard/fintech/bank_dashboard.html', context)

@login_required
def transfer_view(request):
    if request.method == 'POST':
        receiver_account = request.POST.get('receiver_account')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        try:
            BankingService.process_transfer(request.user, receiver_account, amount, description)
            messages.success(request, "Transferência realizada com sucesso!")
            return redirect('fintech:bank_dashboard')
        except Exception as e:
            messages.error(request, f"Erro na transferência: {str(e)}")
            
    return render(request, 'dashboard/fintech/transfer.html')

@login_required
def iot_dashboard(request):
    """
    🎛️ Painel de Controle IoT (Lazarus wallet)
    """
    user_account = getattr(request.user, 'bank_account', None)
    if not user_account:
        return redirect('fintech:bank_dashboard')
        
    devices = IoTDevice.objects.filter(owner_account=user_account)
    
    context = {
        'account': user_account,
        'devices': devices,
        'iot_wallet_service': IoTWalletService, # Pass service class if needed or pre-calc
    }
    return render(request, 'dashboard/fintech/iot_dashboard.html', context)

@login_required
def register_device(request):
    """
    Registra um novo dispositivo IoT na conta do usuário.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        device_id = request.POST.get('device_id')
        
        # Ensure account exists
        user_account = BankingService.create_account(request.user)
        
        IoTDevice.objects.create(
            name=name,
            device_id=device_id,
            owner_account=user_account,
            is_active=True
        )
        messages.success(request, f"Dispositivo {name} conectado ao banco!")
        return redirect('fintech:iot_dashboard')
    return redirect('fintech:iot_dashboard')

@login_required
def simulate_iot_payment(request, device_id):
    """
    Simula um pagamento vindo de um dispositivo.
    """
    if request.method == 'POST':
        amount = request.POST.get('amount')
        target_account = request.POST.get('target_account') # Account Number
        
        try:
            IoTWalletService.process_machine_payment(
                device_id=device_id,
                receiver_account_number=target_account,
                amount=amount,
                description="Simulação via Painel"
            )
            messages.success(request, "Pagamento IoT executado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro IoT: {str(e)}")
            
# --- Mobile Simulator ---
def mobile_app(request):
    """
    Renders the Mobile App Simulator (PWA).
    """
    return render(request, 'dashboard/fintech/mobile_app.html')
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import AccountSerializer, TransactionSerializer, TransferSerializer, PixKeySerializer
from .models import Account, Transaction, PixKey 

class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to view their own account.
    """
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return the user's own account
        return Account.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_account(self, request):
        """
        Idempotent endpoint to create/retrieve user account.
        """
        try:
            account = BankingService.create_account(request.user)
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def invest_limit(self, request):
        """
        Endpoint to convert Balance -> Credit Limit.
        """
        amount = request.data.get('amount')
        if not amount:
             return Response({"error": "Valor obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            BankingService.invest_collateral(request.user, amount)
            # Return updated account
            account = request.user.bank_account
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TransactionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for Transactions.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # User sees sent AND received transactions
        user = self.request.user
        if not hasattr(user, 'bank_account'):
            return Transaction.objects.none()
        account = user.bank_account
        return Transaction.objects.filter(
            Q(sender=account) | Q(receiver=account)
        ).order_by('-timestamp')

    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """
        Execute a transfer.
        """
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            try:
                BankingService.process_transfer(
                    sender_user=request.user,
                    receiver_account_number=serializer.validated_data['receiver_account'],
                    amount=serializer.validated_data['amount'],
                    description=serializer.validated_data.get('description', '')
                )
                return Response({"status": "success", "message": "Transferência realizada."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PixKeyViewSet(viewsets.ModelViewSet):
    """
    API to manage Pix Keys (CRUD).
    """
    serializer_class = PixKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'bank_account'):
            return PixKey.objects.none()
        return PixKey.objects.filter(account=user.bank_account)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Public endpoint to create a new user and bank account.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            # Auto-create account
            BankingService.create_account(user)
            
        return Response({
            'message': 'User created successfully', 
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
