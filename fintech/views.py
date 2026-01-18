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
            return redirect('dashboard:fintech:bank_dashboard')
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
        return redirect('dashboard:fintech:bank_dashboard')
        
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
        return redirect('dashboard:fintech:iot_dashboard')
    return redirect('dashboard:fintech:iot_dashboard')

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
            
    return redirect('dashboard:fintech:iot_dashboard')
