import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def force_reset():
    username = 'admin'
    password = 'admin'
    email = 'admin@jetbank.com'

    # Delete if exists
    try:
        u = User.objects.get(username=username)
        print(f"Deleting existing user: {username}")
        u.delete()
    except User.DoesNotExist:
        pass

    # Create fresh
    print(f"Creating fresh superuser: {username}")
    User.objects.create_superuser(username, email, password)
    print("Success! Password is: 'admin'")

if __name__ == '__main__':
    force_reset()
