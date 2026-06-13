"""
seed_new_teams.py — Adds 2 new teams with M1 managers and employees
Run from project root: python backend/seed_new_teams.py

Creates:
- team_002: Sales Team Beta
- team_003: Sales Team Gamma
Each with their own M1 Manager and Employee
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase_config import initialize_firebase, get_firestore_client
from firebase_admin import firestore

# ── PASTE YOUR UIDs HERE ───────────────────────────────────────────────────────

# Existing UIDs (from your original setup)
M2_MANAGER_UID   = "vnpNDxrwePVKE8GqFrhqKESbizI2"
M1_MANAGER_1_UID = "APm9grZhkPUNSexOJpfzY8eZeUz2"
EMPLOYEE_1_UID   = "DXsAbjuiEgTHmZBEdGw7u8zaOxF2"

# New UIDs (just copied from Firebase Auth Console)
M1_MANAGER_2_UID = "QTTNKFRYzKP8pQXtvrBexws7klJ3"
EMPLOYEE_2_UID   = "U6fhP42tzAgzQVgrgfo5coFt3In1"

M1_MANAGER_3_UID = "PYWhJU2Vf9MRVPT0SwDZdWujnpC2"
EMPLOYEE_3_UID   = "fKVxTQmGVdhE1aCVkA1LkbgSMhG3"

# ──────────────────────────────────────────────────────────────────────────────


def check_uids():
    """Verify all UIDs are filled in before running."""
    uid_map = {
        "M2_MANAGER_UID":   M2_MANAGER_UID,
        "M1_MANAGER_1_UID": M1_MANAGER_1_UID,
        "EMPLOYEE_1_UID":   EMPLOYEE_1_UID,
        "M1_MANAGER_2_UID": M1_MANAGER_2_UID,
        "EMPLOYEE_2_UID":   EMPLOYEE_2_UID,
        "M1_MANAGER_3_UID": M1_MANAGER_3_UID,
        "EMPLOYEE_3_UID":   EMPLOYEE_3_UID,
    }
    for label, uid in uid_map.items():
        if "PASTE_" in uid:
            print(f"\n❌ ERROR: Replace {label} with the real UID")
            return False
    return True


def seed_new_users(db):
    """Add Firestore user documents for all new users."""
    print("\n── Step 1: Seeding New Users ──────────────────────")

    new_users = [
        {
            "uid":         M1_MANAGER_2_UID,
            "email":       "m1manager2@test.com",
            "displayName": "M1 Manager Beta",
            "role":        "m1_manager",
            "teamId":      "team_002",
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP,
        },
        {
            "uid":         EMPLOYEE_2_UID,
            "email":       "employee2@test.com",
            "displayName": "Employee Beta",
            "role":        "employee",
            "teamId":      "team_002",
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP,
        },
        {
            "uid":         M1_MANAGER_3_UID,
            "email":       "m1manager3@test.com",
            "displayName": "M1 Manager Gamma",
            "role":        "m1_manager",
            "teamId":      "team_003",
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP,
        },
        {
            "uid":         EMPLOYEE_3_UID,
            "email":       "employee3@test.com",
            "displayName": "Employee Gamma",
            "role":        "employee",
            "teamId":      "team_003",
            "isActive":    True,
            "createdAt":   firestore.SERVER_TIMESTAMP,
        },
    ]

    for user in new_users:
        existing = db.collection('users').document(user['uid']).get()
        if existing.exists:
            print(f"⚠️  User already exists: {user['email']} — skipping")
            continue
        db.collection('users').document(user['uid']).set(user)
        print(f"✅ Created user: {user['email']} | role: {user['role']}")

    # Also update existing Employee 1 and M1 Manager 1 with correct teamId
    print("\n── Updating existing users with teamId ──────────────")
    db.collection('users').document(EMPLOYEE_1_UID).update({
        "teamId": "team_001"
    })
    print("✅ Updated Employee 1 teamId → team_001")

    db.collection('users').document(M1_MANAGER_1_UID).update({
        "teamId": "team_001"
    })
    print("✅ Updated M1 Manager 1 teamId → team_001")

    db.collection('users').document(M2_MANAGER_UID).update({
        "teamId": "team_001"
    })
    print("✅ Updated M2 Manager teamId → team_001")


def seed_new_teams(db):
    """Create team_002 and team_003 with members subcollections."""
    print("\n── Step 2: Creating New Teams ─────────────────────")

    teams = [
        {
            "teamId":       "team_002",
            "teamName":     "Sales Team Beta",
            "m1ManagerUid": M1_MANAGER_2_UID,
            "m2ManagerUid": M2_MANAGER_UID,
            "isActive":     True,
            "createdAt":    firestore.SERVER_TIMESTAMP,
            "createdBy":    M2_MANAGER_UID,
            "members": [
                {
                    "uid":       EMPLOYEE_2_UID,
                    "email":     "employee2@test.com",
                    "displayName": "Employee Beta",
                    "role":      "employee",
                    "joinedAt":  firestore.SERVER_TIMESTAMP,
                },
                {
                    "uid":       M1_MANAGER_2_UID,
                    "email":     "m1manager2@test.com",
                    "displayName": "M1 Manager Beta",
                    "role":      "m1_manager",
                    "joinedAt":  firestore.SERVER_TIMESTAMP,
                },
            ]
        },
        {
            "teamId":       "team_003",
            "teamName":     "Sales Team Gamma",
            "m1ManagerUid": M1_MANAGER_3_UID,
            "m2ManagerUid": M2_MANAGER_UID,
            "isActive":     True,
            "createdAt":    firestore.SERVER_TIMESTAMP,
            "createdBy":    M2_MANAGER_UID,
            "members": [
                {
                    "uid":       EMPLOYEE_3_UID,
                    "email":     "employee3@test.com",
                    "displayName": "Employee Gamma",
                    "role":      "employee",
                    "joinedAt":  firestore.SERVER_TIMESTAMP,
                },
                {
                    "uid":       M1_MANAGER_3_UID,
                    "email":     "m1manager3@test.com",
                    "displayName": "M1 Manager Gamma",
                    "role":      "m1_manager",
                    "joinedAt":  firestore.SERVER_TIMESTAMP,
                },
            ]
        },
    ]

    for team in teams:
        team_id = team['teamId']
        members = team.pop('members')

        # Check if team already exists
        existing = db.collection('teams').document(team_id).get()
        if existing.exists:
            print(f"⚠️  Team already exists: {team['teamName']} — skipping")
            team['members'] = members
            continue

        # Create team document
        db.collection('teams').document(team_id).set(team)
        print(f"✅ Created team: {team['teamName']} (ID: {team_id})")

        # Add members subcollection
        for member in members:
            db.collection('teams').document(team_id)\
              .collection('members').document(member['uid']).set(member)
            print(f"   ✅ Added member: {member['email']} as {member['role']}")


def seed_demo_leads_for_new_teams(db):
    """Add a few demo leads for the new teams so dashboards look populated."""
    print("\n── Step 3: Adding Demo Leads for New Teams ─────────")

    import uuid

    demo_leads = [
        # Team 002 leads
        {
            "employeeUid":  EMPLOYEE_2_UID,
            "teamId":       "team_002",
            "name":         "Aditya Sharma",
            "company":      "BrightTech Solutions",
            "email":        "aditya@brighttech.com",
            "phone":        "+91 9876500201",
            "linkedinUrl":  "https://linkedin.com/in/adityasharma",
            "currentStage": "stage_7",
            "isArchived":   False,
        },
        {
            "employeeUid":  EMPLOYEE_2_UID,
            "teamId":       "team_002",
            "name":         "Kavitha Menon",
            "company":      "InfoNova Pvt Ltd",
            "email":        "kavitha@infonova.com",
            "phone":        "+91 9876500202",
            "linkedinUrl":  "https://linkedin.com/in/kavithamenon",
            "currentStage": "stage_4",
            "isArchived":   False,
        },
        {
            "employeeUid":  EMPLOYEE_2_UID,
            "teamId":       "team_002",
            "name":         "Suresh Babu",
            "company":      "CoreStack Systems",
            "email":        "suresh@corestack.in",
            "phone":        "+91 9876500203",
            "linkedinUrl":  "https://linkedin.com/in/sureshbabu",
            "currentStage": "stage_6_1",
            "isArchived":   False,
        },
        # Team 003 leads
        {
            "employeeUid":  EMPLOYEE_3_UID,
            "teamId":       "team_003",
            "name":         "Divya Krishnan",
            "company":      "NexaData Analytics",
            "email":        "divya@nexadata.com",
            "phone":        "+91 9876500301",
            "linkedinUrl":  "https://linkedin.com/in/divyakrishnan",
            "currentStage": "stage_8",
            "isArchived":   False,
        },
        {
            "employeeUid":  EMPLOYEE_3_UID,
            "teamId":       "team_003",
            "name":         "Rajan Pillai",
            "company":      "SwiftServe Tech",
            "email":        "rajan@swiftserve.io",
            "phone":        "+91 9876500302",
            "linkedinUrl":  "https://linkedin.com/in/rajanpillai",
            "currentStage": "stage_2_1",
            "isArchived":   False,
        },
        {
            "employeeUid":  EMPLOYEE_3_UID,
            "teamId":       "team_003",
            "name":         "Meghna Das",
            "company":      "Pinnacle Soft",
            "email":        "meghna@pinnaclesoft.com",
            "phone":        "+91 9876500303",
            "linkedinUrl":  "https://linkedin.com/in/meghnadass",
            "currentStage": "stage_3",
            "isArchived":   False,
        },
    ]

    for lead_data in demo_leads:
        lead_id = str(uuid.uuid4())
        lead    = {
            "leadId":      lead_id,
            "createdAt":   firestore.SERVER_TIMESTAMP,
            "updatedAt":   firestore.SERVER_TIMESTAMP,
            **lead_data
        }
        db.collection('leads').document(lead_id).set(lead)

        # Audit log
        import uuid as _uuid
        log_id = str(_uuid.uuid4())
        db.collection('audit_logs').document(log_id).set({
            "logId":       log_id,
            "leadId":      lead_id,
            "employeeUid": lead_data['employeeUid'],
            "fromStage":   None,
            "toStage":     lead_data['currentStage'],
            "changedAt":   firestore.SERVER_TIMESTAMP,
            "notes":       "Demo lead for new team"
        })
        print(f"✅ Lead: {lead_data['name']} | {lead_data['teamId']}")

    print(f"\n✅ {len(demo_leads)} demo leads created")


def main():
    print("\n" + "=" * 55)
    print("   ADDING 2 NEW TEAMS TO SALES TRACKING SYSTEM")
    print("=" * 55)

    if not check_uids():
        print("\n❌ Please fill in all UIDs and run again.")
        return

    initialize_firebase()
    db = get_firestore_client()

    seed_new_users(db)
    seed_new_teams(db)
    seed_demo_leads_for_new_teams(db)

    print("\n" + "=" * 55)
    print("   ✅ ALL DONE — 3 TEAMS NOW ACTIVE")
    print("=" * 55)
    print("\nTeam Summary:")
    print("  team_001 — Sales Team Alpha   → m1manager@test.com")
    print("  team_002 — Sales Team Beta    → m1manager2@test.com")
    print("  team_003 — Sales Team Gamma   → m1manager3@test.com")
    print("\nLogin credentials:")
    print("  m1manager2@test.com  | Test@1234")
    print("  employee2@test.com   | Test@1234")
    print("  m1manager3@test.com  | Test@1234")
    print("  employee3@test.com   | Test@1234")
    print("=" * 55)


if __name__ == '__main__':
    main()