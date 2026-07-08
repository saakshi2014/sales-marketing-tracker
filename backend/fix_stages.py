"""
fix_stages.py — Reactivates stage_1_1 and cleans up bad custom stages
Run from project root: python backend/fix_stages.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from firebase_config import initialize_firebase, get_firestore_client

def fix_stages():
    print("\n" + "=" * 55)
    print("   FIXING PIPELINE STAGES")
    print("=" * 55)

    initialize_firebase()
    db = get_firestore_client()

    # ── 1. Reactivate stage_1_1 ───────────────────────────────────────────────
    stage_ref = db.collection('pipeline_stages').document('stage_1_1')
    stage_doc = stage_ref.get()

    if stage_doc.exists:
        current = stage_doc.to_dict()
        if not current.get('isActive', True):
            stage_ref.update({'isActive': True})
            print("✅ stage_1_1 — Qualified – Pending Outreach → REACTIVATED")
        else:
            print("✅ stage_1_1 is already active — no change needed")
    else:
        print("❌ stage_1_1 not found — re-seeding it")
        from firebase_admin import firestore as fs
        stage_ref.set({
            "stageId":     "stage_1_1",
            "stageNumber": "1.1",
            "stageName":   "Qualified – Pending Outreach",
            "description": "Lead identified and qualified. Outreach not started.",
            "stageOrder":  1,
            "isDefault":   True,
            "isActive":    True,
            "isArchived":  False,
            "createdBy":   None,
            "createdAt":   fs.SERVER_TIMESTAMP,
        })
        print("✅ stage_1_1 re-seeded successfully")

    # ── 2. List all stages and their current status ───────────────────────────
    print("\n── Current Stage Status ─────────────────────────────")
    all_stages = db.collection('pipeline_stages').get()
    stages = sorted(
        [s.to_dict() for s in all_stages],
        key=lambda x: x.get('stageOrder', 99)
    )

    for s in stages:
        status = "✅ Active  " if s.get('isActive') else "❌ Inactive"
        stype  = "DEFAULT" if s.get('isDefault') else "CUSTOM "
        print(f"  {status} | {stype} | "
              f"{s.get('stageNumber','?'):5s} | "
              f"{s.get('stageName','?')}")

    # ── 3. Fix custom stages with missing stageNumber ─────────────────────────
    print("\n── Fixing Custom Stages With Bad stageNumber ────────")
    for s in stages:
        if not s.get('isDefault') and not s.get('stageNumber'):
            stage_id = s.get('stageId', '')
            if stage_id:
                # Generate a proper stage number
                proper_num = f"C{stage_id[-4:].upper()}"
                db.collection('pipeline_stages').document(stage_id).update({
                    'stageNumber': proper_num
                })
                print(f"  Fixed: {stage_id} → stageNumber set to {proper_num}")

    # ── 4. Invalidate cache ───────────────────────────────────────────────────
    print("\n── Invalidating Stages Cache ────────────────────────")
    try:
        from routes.stages import invalidate_stages_cache
        invalidate_stages_cache()
        print("✅ Cache cleared")
    except Exception:
        print("ℹ️  Cache will auto-clear in 5 minutes")

    print("\n" + "=" * 55)
    print("   ✅ STAGE FIX COMPLETE")
    print("=" * 55)
    print("\nRestart Flask and check:")
    print("  1. Stage change dropdown shows stage 1.1")
    print("  2. M1 Stage Distribution shows all stages")
    print("  3. New leads default to stage 1.1 correctly")

if __name__ == '__main__':
    fix_stages()