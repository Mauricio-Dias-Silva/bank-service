import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from fintech.models import Account

User = get_user_model()

def fix_admin():
    try:
        user = User.objects.get(username='admin')
        if hasattr(user, 'bank_account'):
            print(f"Deleting broken account for {user.username}...")
            user.bank_account.delete()
            print("Account deleted. It will be recreated correctly on next login.")
        else:
            print("Admin has no account to delete.")
            
    except User.DoesNotExist:
        print("Admin user not found.")

if __name__ == '__main__':
    fix_admin()
