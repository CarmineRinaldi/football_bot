# check_db.py
from db import get_all_users

users = get_all_users()
print("Utenti nel DB:", users)
