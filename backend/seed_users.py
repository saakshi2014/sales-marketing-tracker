"""
seed_users.py — Seeds the 3 test users into Firestore
Run this ONCE to create user documents for your 3 test accounts.

How to run (from project root):
    python backend/seed_users.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from firebase_config import initialize_firebase, get_firestore_client
from firebase_admin import firestore

# ── PASTE YOUR 3 UIDs HERE ─────────────────────────────────────────────────────

EMPLOYEE_UID   = "DXsAbjuiEgTHmZBEdGw7u8zaOxF2"
M1_MANAGER_UID = "APm9grZhkPUNSexOJpfzY8eZeUz2"
M2_MANAGER_UID = "vnpNDxrwePVKE8GqFrhqKESbizI2"

# ──────────────────────────────────────────────────────────────────────────────


def seed_users():
    print("\n" + "=" * 52)
    print("   Seeding Users into Firestore")
    print("=" * 52)

    initialize_firebase()
    db = get_firestore_client()

    users = [
        {
            "uid":         EMPLOYEE_UID,
            "email":       "employee@test.com",
            "displayName": "Test Employee",
            "role":        "employee",
            "teamId":      "team_001",
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP
        },
        {
            "uid":         M1_MANAGER_UID,
            "email":       "m1manager@test.com",
            "displayName": "Test M1 Manager",
            "role":        "m1_manager",
            "teamId":      "team_001",
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP
        },
        {
            "uid":         M2_MANAGER_UID,
            "email":       "m2manager@test.com",
            "displayName": "Test M2 Manager",
            "role":        "m2_manager",
            "teamId":      None,
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP
        }
    ]

    for user in users:
        uid = user["uid"]

        if "PASTE_" in uid:
            print(f"\n❌ ERROR: Replace the UID placeholder for {user['email']}")
            print("   Open seed_users.py and paste the real UIDs")
            return

        # ── HIGHLANDER RULE CHECK FOR M2 MANAGER ──────────────────────
        if user["role"] == "m2_manager":

            existing_m2 = (
                db.collection('users')
                .where('role', '==', 'm2_manager')
                .get()
            )

            existing_m2_list = [
                d for d in existing_m2
                if d.id != M2_MANAGER_UID
            ]

            if existing_m2_list:
                print("\n⚠️  WARNING: Another M2 Manager already exists!")
                print("   Highlander Rule: Only ONE M2 Manager allowed.")
                print("   Skipping M2 creation.")
                continue

        db.collection('users').document(uid).set(user)

        print(f"✅ Created: {user['email']} | role: {user['role']}")

    print("\n✅ USER SEEDING PROCESS COMPLETED")
    print("=" * 52)


if __name__ == '__main__':
    seed_users()