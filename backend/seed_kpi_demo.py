"""
seed_kpi_demo.py — Seeds leads and audit logs spread across
LAST MONTH and THIS WEEK so KPI toggle shows clearly different values.

Run from project root:
    python backend/seed_kpi_demo.py

This creates:
- 8 leads from LAST MONTH with full stage progressions
- 4 leads from THIS WEEK with stage progressions
So when guide toggles between Monthly/Weekly they see different KPIs.
"""

import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase_config import initialize_firebase, get_firestore_client
from firebase_admin import firestore
from datetime import datetime, timezone, timedelta

# ── PASTE YOUR UIDs HERE ───────────────────────────────────────────────────────
EMPLOYEE_UID   = "DXsAbjuiEgTHmZBEdGw7u8zaOxF2"
EMPLOYEE_2_UID = "U6fhP42tzAgzQVgrgfo5coFt3In1"
EMPLOYEE_3_UID = "fKVxTQmGVdhE1aCVkA1LkbgSMhG3"
TEAM_1_ID      = "team_001"
TEAM_2_ID      = "team_002"
TEAM_3_ID      = "team_003"
# ──────────────────────────────────────────────────────────────────────────────


def get_last_month_date(days_ago):
    """Returns a datetime from last month."""
    now = datetime.now(timezone.utc)
    # Go back to last month
    if now.month == 1:
        last_month = now.replace(year=now.year-1, month=12, day=1)
    else:
        last_month = now.replace(month=now.month-1, day=1)
    return last_month + timedelta(days=days_ago)


def get_this_week_date(days_ago):
    """Returns a datetime from this week."""
    now = datetime.now(timezone.utc)
    return now - timedelta(days=days_ago)


def create_lead_with_history(db, lead_data, stage_history):
    """
    Creates a lead and writes audit log entries with
    specific timestamps so KPI calculation picks them up.
    """
    lead_id = str(uuid.uuid4())

    # Create lead document
    lead = {
        "leadId":       lead_id,
        "employeeUid":  lead_data['employeeUid'],
        "teamId":       lead_data['teamId'],
        "name":         lead_data['name'],
        "company":      lead_data['company'],
        "email":        lead_data['email'],
        "phone":        lead_data['phone'],
        "linkedinUrl":  lead_data.get('linkedinUrl', ''),
        "currentStage": stage_history[-1]['stage'],
        "isArchived":   stage_history[-1]['stage'] == 'stage_6_2',
        "createdAt":    stage_history[0]['date'],
        "updatedAt":    stage_history[-1]['date'],
    }
    db.collection('leads').document(lead_id).set(lead)

    # Write audit log for each stage transition
    prev_stage = None
    for entry in stage_history:
        log_id = str(uuid.uuid4())
        db.collection('audit_logs').document(log_id).set({
            "logId":       log_id,
            "leadId":      lead_id,
            "employeeUid": lead_data['employeeUid'],
            "fromStage":   prev_stage,
            "toStage":     entry['stage'],
            "changedAt":   entry['date'],
            "notes":       entry.get('notes', 'KPI demo data')
        })
        prev_stage = entry['stage']

    return lead_id


def seed_last_month_leads(db):
    """
    Creates 8 leads from LAST MONTH.
    Stage progressions designed to show:
    - outreachCount: 8
    - connectionRate: ~75% (6/8)
    - messageCount: 6
    - replyRate: ~67% (4/6)
    - meetingConvRate: ~75% (3/4)
    """
    print("\n── Seeding LAST MONTH Leads (Team Alpha) ───────────")

    last_month_leads = [
        # Lead 1: Full journey → Meeting Completed
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Anand Kumar",
                "company":     "TechBridge Solutions",
                "email":       "anand@techbridge.com",
                "phone":       "+91 9876541001",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(25)},
                {"stage": "stage_2",   "date": get_last_month_date(23)},
                {"stage": "stage_2_1", "date": get_last_month_date(21)},
                {"stage": "stage_3",   "date": get_last_month_date(19)},
                {"stage": "stage_4",   "date": get_last_month_date(17)},
                {"stage": "stage_6_1", "date": get_last_month_date(15)},
                {"stage": "stage_7",   "date": get_last_month_date(10)},
                {"stage": "stage_8",   "date": get_last_month_date(5)},
            ]
        },
        # Lead 2: Meeting Scheduled
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Pooja Bhat",
                "company":     "InnoSphere Pvt Ltd",
                "email":       "pooja@innosphere.com",
                "phone":       "+91 9876541002",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(24)},
                {"stage": "stage_2",   "date": get_last_month_date(22)},
                {"stage": "stage_2_1", "date": get_last_month_date(20)},
                {"stage": "stage_3",   "date": get_last_month_date(18)},
                {"stage": "stage_4",   "date": get_last_month_date(16)},
                {"stage": "stage_7",   "date": get_last_month_date(8)},
            ]
        },
        # Lead 3: Interested
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Rahul Shenoy",
                "company":     "DataCore Systems",
                "email":       "rahul@datacore.in",
                "phone":       "+91 9876541003",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(23)},
                {"stage": "stage_2",   "date": get_last_month_date(21)},
                {"stage": "stage_2_1", "date": get_last_month_date(19)},
                {"stage": "stage_3",   "date": get_last_month_date(17)},
                {"stage": "stage_4",   "date": get_last_month_date(15)},
                {"stage": "stage_6_1", "date": get_last_month_date(12)},
            ]
        },
        # Lead 4: Meeting Completed
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Sneha Kamath",
                "company":     "CloudVision Tech",
                "email":       "sneha@cloudvision.com",
                "phone":       "+91 9876541004",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(22)},
                {"stage": "stage_2",   "date": get_last_month_date(20)},
                {"stage": "stage_2_1", "date": get_last_month_date(18)},
                {"stage": "stage_3",   "date": get_last_month_date(16)},
                {"stage": "stage_4",   "date": get_last_month_date(14)},
                {"stage": "stage_7",   "date": get_last_month_date(9)},
                {"stage": "stage_8",   "date": get_last_month_date(4)},
            ]
        },
        # Lead 5: No reply (sent connection + message, no reply)
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Vivek Rao",
                "company":     "PrimeServe Ltd",
                "email":       "vivek@primeserve.com",
                "phone":       "+91 9876541005",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(21)},
                {"stage": "stage_2",   "date": get_last_month_date(19)},
                {"stage": "stage_2_1", "date": get_last_month_date(17)},
                {"stage": "stage_3",   "date": get_last_month_date(15)},
                {"stage": "stage_3_1", "date": get_last_month_date(13)},
            ]
        },
        # Lead 6: Connection not accepted
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Asha Nair",
                "company":     "WebTrend Analytics",
                "email":       "asha@webtrend.io",
                "phone":       "+91 9876541006",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(20)},
                {"stage": "stage_2",   "date": get_last_month_date(18)},
                {"stage": "stage_2_2", "date": get_last_month_date(16)},
            ]
        },
        # Lead 7: Connected, message sent, got reply
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Kiran Mallya",
                "company":     "NextEdge Software",
                "email":       "kiran@nextedge.co.in",
                "phone":       "+91 9876541007",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(19)},
                {"stage": "stage_2",   "date": get_last_month_date(17)},
                {"stage": "stage_2_1", "date": get_last_month_date(15)},
                {"stage": "stage_3",   "date": get_last_month_date(13)},
                {"stage": "stage_4",   "date": get_last_month_date(11)},
                {"stage": "stage_6_3", "date": get_last_month_date(8)},
            ]
        },
        # Lead 8: Connection not accepted
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Deepa Shetty",
                "company":     "FutureSoft Udupi",
                "email":       "deepa@futuresoft.in",
                "phone":       "+91 9876541008",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_last_month_date(18)},
                {"stage": "stage_2",   "date": get_last_month_date(16)},
                {"stage": "stage_2_2", "date": get_last_month_date(14)},
            ]
        },
    ]

    for item in last_month_leads:
        lead_id = create_lead_with_history(
            db, item['data'], item['history'])
        print(f"✅ LAST MONTH lead: {item['data']['name']} "
              f"→ Stage: {item['history'][-1]['stage']}")

    print(f"\n📊 Last Month KPIs (Employee Alpha):")
    print(f"   Outreach Count:       8  (8 leads sent to stage_2)")
    print(f"   Connection Rate:      75% (6 out of 8 connected)")
    print(f"   Message Count:        5  (5 leads reached stage_3)")
    print(f"   Reply Rate:           80% (4 out of 5 replied)")
    print(f"   Meeting Conv Rate:    75% (3 meetings from 4 replies)")


def seed_this_week_leads(db):
    """
    Creates 4 leads from THIS WEEK.
    Stage progressions designed to show:
    - outreachCount: 4
    - connectionRate: 50% (2/4)
    - messageCount: 2
    - replyRate: 50% (1/2)
    - meetingConvRate: 100% (1/1)

    VISIBLY DIFFERENT from last month so toggle is obvious.
    """
    print("\n── Seeding THIS WEEK Leads (Team Alpha) ────────────")

    this_week_leads = [
        # Lead 1: Full journey this week
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Arun Hegde",
                "company":     "QuickServe Tech",
                "email":       "arun@quickserve.com",
                "phone":       "+91 9876542001",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_this_week_date(5)},
                {"stage": "stage_2",   "date": get_this_week_date(4)},
                {"stage": "stage_2_1", "date": get_this_week_date(3)},
                {"stage": "stage_3",   "date": get_this_week_date(2)},
                {"stage": "stage_4",   "date": get_this_week_date(1)},
                {"stage": "stage_7",   "date": get_this_week_date(0)},
            ]
        },
        # Lead 2: Connected, no message yet
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Preethi Suvarna",
                "company":     "Mangalore Digital",
                "email":       "preethi@mangaloredigital.com",
                "phone":       "+91 9876542002",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_this_week_date(4)},
                {"stage": "stage_2",   "date": get_this_week_date(3)},
                {"stage": "stage_2_1", "date": get_this_week_date(2)},
            ]
        },
        # Lead 3: Request sent, not accepted
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Sunil D'Souza",
                "company":     "Coast IT Services",
                "email":       "sunil@coastit.in",
                "phone":       "+91 9876542003",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_this_week_date(3)},
                {"stage": "stage_2",   "date": get_this_week_date(2)},
                {"stage": "stage_2_2", "date": get_this_week_date(1)},
            ]
        },
        # Lead 4: Just qualified
        {
            "data": {
                "employeeUid": EMPLOYEE_UID,
                "teamId":      TEAM_1_ID,
                "name":        "Nisha Alva",
                "company":     "Udupi Soft Labs",
                "email":       "nisha@udupilabs.com",
                "phone":       "+91 9876542004",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_this_week_date(1)},
                {"stage": "stage_2",   "date": get_this_week_date(0)},
            ]
        },
    ]

    for item in this_week_leads:
        lead_id = create_lead_with_history(
            db, item['data'], item['history'])
        print(f"✅ THIS WEEK lead: {item['data']['name']} "
              f"→ Stage: {item['history'][-1]['stage']}")

    print(f"\n📊 This Week KPIs (Employee Alpha):")
    print(f"   Outreach Count:       4  (4 leads sent to stage_2)")
    print(f"   Connection Rate:      50% (2 out of 4 connected)")
    print(f"   Message Count:        1  (1 lead reached stage_3)")
    print(f"   Reply Rate:           100% (1 out of 1 replied)")
    print(f"   Meeting Conv Rate:    100% (1 meeting from 1 reply)")


def seed_team_beta_week_data(db):
    """Seed some this-week data for Team Beta employee too."""
    print("\n── Seeding THIS WEEK Leads (Team Beta) ─────────────")

    team_beta_leads = [
        {
            "data": {
                "employeeUid": EMPLOYEE_2_UID,
                "teamId":      TEAM_2_ID,
                "name":        "Roshan Fernandes",
                "company":     "Konkani Tech Hub",
                "email":       "roshan@konkanitechhub.com",
                "phone":       "+91 9876543001",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_this_week_date(3)},
                {"stage": "stage_2",   "date": get_this_week_date(2)},
                {"stage": "stage_2_1", "date": get_this_week_date(1)},
                {"stage": "stage_3",   "date": get_this_week_date(0)},
            ]
        },
        {
            "data": {
                "employeeUid": EMPLOYEE_2_UID,
                "teamId":      TEAM_2_ID,
                "name":        "Lavanya Prabhu",
                "company":     "Udupi Webworks",
                "email":       "lavanya@udupiweb.in",
                "phone":       "+91 9876543002",
            },
            "history": [
                {"stage": "stage_1_1", "date": get_this_week_date(2)},
                {"stage": "stage_2",   "date": get_this_week_date(1)},
            ]
        },
    ]

    for item in team_beta_leads:
        create_lead_with_history(db, item['data'], item['history'])
        print(f"✅ Team Beta lead: {item['data']['name']}")


def main():
    print("\n" + "=" * 55)
    print("   KPI DEMO DATA SEEDER")
    print("   Seeding leads across LAST MONTH and THIS WEEK")
    print("=" * 55)

    for uid, label in [
        (EMPLOYEE_UID,   "EMPLOYEE_UID"),
        (EMPLOYEE_2_UID, "EMPLOYEE_2_UID"),
        (EMPLOYEE_3_UID, "EMPLOYEE_3_UID"),
    ]:
        if "PASTE_" in uid:
            print(f"\n❌ ERROR: Replace {label} with real UID")
            return

    initialize_firebase()
    db = get_firestore_client()

    seed_last_month_leads(db)
    seed_this_week_leads(db)
    seed_team_beta_week_data(db)

    print("\n" + "=" * 55)
    print("   ✅ KPI DEMO DATA SEEDED SUCCESSFULLY")
    print("=" * 55)
    print("""
WHAT YOUR GUIDE WILL SEE:

Employee Alpha — MY KPIs Tab:
┌─────────────────────────┬────────────┬───────────┐
│ KPI                     │ This Month │ This Week │
├─────────────────────────┼────────────┼───────────┤
│ Outreach Count          │     8      │     4     │
│ Connection Rate         │    75%     │    50%    │
│ Message Count           │     5      │     1     │
│ Reply Rate              │    80%     │   100%    │
│ Meeting Conv Rate       │    75%     │   100%    │
└─────────────────────────┴────────────┴───────────┘

Toggle This Month → This Week shows CLEARLY different numbers!
""")


if __name__ == '__main__':
    main()