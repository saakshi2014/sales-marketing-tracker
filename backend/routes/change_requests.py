"""
change_requests.py — Lead Contact Change Request API
Employee requests a change to email/phone/linkedinUrl.
M1 Manager approves or rejects. Only on approval does
the lead data actually update.
"""

from flask import Blueprint, request, jsonify, session
from firebase_config import get_firestore_client
from firebase_admin import firestore
import uuid
from datetime import datetime, timezone

change_requests_bp = Blueprint('change_requests', __name__)


def require_auth():
    if 'uid' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    return None


# ── ROUTE 1: Employee submits a change request ─────────────────────────────────
@change_requests_bp.route(
    '/api/leads/<lead_id>/change-request', methods=['POST'])
def submit_change_request(lead_id):
    """
    Employee submits a request to change email, phone, or linkedinUrl.
    Name and company CANNOT be requested for change.
    M1 Manager will receive a notification and must approve.

    Request body:
    {
        "requestedChanges": {
            "email":       "newemail@example.com",
            "phone":       "9876543210",
            "linkedinUrl": "https://linkedin.com/in/newprofile"
        },
        "reason": "Customer called and gave updated contact"
    }
    """
    auth_error = require_auth()
    if auth_error:
        return auth_error

    uid  = session['uid']
    role = session['role']

    if role != 'employee':
        return jsonify({
            "error": "Only employees can submit change requests"
        }), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    requested_changes = data.get('requestedChanges', {})
    reason            = data.get('reason', '').strip()

    if not requested_changes:
        return jsonify({"error": "No changes requested"}), 400
    if not reason:
        return jsonify({"error": "Reason for change is required"}), 400

    # Block name and company change requests
    blocked_fields = [f for f in requested_changes
                      if f in ['name', 'company']]
    if blocked_fields:
        return jsonify({
            "error": f"Cannot request changes to: "
                     f"{', '.join(blocked_fields)}. "
                     f"These are identity fields."
        }), 403

    # Validate allowed fields only
    allowed = {'email', 'phone', 'linkedinUrl'}
    invalid = set(requested_changes.keys()) - allowed
    if invalid:
        return jsonify({
            "error": f"Invalid fields: {invalid}. "
                     f"Only email, phone, and linkedinUrl can be changed."
        }), 400

    try:
        db = get_firestore_client()

        # Verify lead exists and belongs to employee
        lead_doc = db.collection('leads').document(lead_id).get()
        if not lead_doc.exists:
            return jsonify({"error": "Lead not found"}), 404

        lead_data = lead_doc.to_dict()
        if lead_data.get('employeeUid') != uid:
            return jsonify({
                "error": "You can only request changes to your own leads"
            }), 403

        # Check if there is already a pending request for this lead
        existing = db.collection('change_requests')\
                     .where('leadId', '==', lead_id)\
                     .where('status', '==', 'pending').get()
        if list(existing):
            return jsonify({
                "error": "A pending change request already exists "
                         "for this lead. Please wait for M1 approval."
            }), 409

        # Get M1 Manager for this employee's team
        user_doc = db.collection('users').document(uid).get()
        team_id  = user_doc.to_dict().get('teamId', '')
        team_doc = db.collection('teams').document(team_id).get()

        if not team_doc.exists:
            return jsonify({"error": "Team not found"}), 404

        m1_uid = team_doc.to_dict().get('m1ManagerUid', '')
        if not m1_uid:
            return jsonify({"error": "M1 Manager not found"}), 404

        # Get employee and lead info for display
        emp_data   = user_doc.to_dict()
        emp_name   = emp_data.get('displayName',
                     emp_data.get('email', 'Employee'))
        lead_name  = lead_data.get('name', 'Unknown Lead')

        # Build current vs requested comparison
        current_values = {}
        for field in requested_changes:
            current_values[field] = lead_data.get(field, '')

        # Create the change request document
        request_id = str(uuid.uuid4())

        change_request = {
            "requestId":        request_id,
            "leadId":           lead_id,
            "leadName":         lead_name,
            "employeeUid":      uid,
            "employeeName":     emp_name,
            "m1ManagerUid":     m1_uid,
            "teamId":           team_id,
            "requestedChanges": requested_changes,
            "currentValues":    current_values,
            "reason":           reason,
            "status":           "pending",
            "createdAt":        firestore.SERVER_TIMESTAMP,
            "reviewedAt":       None,
            "reviewedBy":       None,
            "reviewNote":       None,
        }

        db.collection('change_requests')\
          .document(request_id).set(change_request)

        # Send notification to M1 Manager
        notif_id = str(uuid.uuid4())
        db.collection('notifications').document(notif_id).set({
            "notifId":      notif_id,
            "recipientUid": m1_uid,
            "message":      f"{emp_name} has requested contact "
                            f"details change for lead '{lead_name}'. "
                            f"Reason: {reason}",
            "type":         "change_request_pending",
            "relatedId":    request_id,
            "isRead":       False,
            "createdAt":    firestore.SERVER_TIMESTAMP,
        })

        return jsonify({
            "message":   "Change request submitted successfully. "
                         "Awaiting M1 Manager approval.",
            "requestId": request_id,
            "status":    "pending"
        }), 201

    except Exception as e:
        print(f"Error submitting change request: {e}")
        return jsonify({"error": str(e)}), 500


# ── ROUTE 2: Get change requests (M1 sees pending, employee sees own) ──────────
@change_requests_bp.route('/api/change-requests', methods=['GET'])
def get_change_requests():
    """
    M1 Manager: sees all pending requests for their team.
    Employee: sees their own requests.
    """
    auth_error = require_auth()
    if auth_error:
        return auth_error

    uid  = session['uid']
    role = session['role']

    try:
        db = get_firestore_client()

        if role == 'm1_manager':
            requests_ref = db.collection('change_requests')\
                             .where('m1ManagerUid', '==', uid).get()
        elif role == 'm2_manager':
            requests_ref = db.collection('change_requests').get()
        else:
            requests_ref = db.collection('change_requests')\
                             .where('employeeUid', '==', uid).get()

        status_filter = request.args.get('status', '')
        requests_list = []

        for doc in requests_ref:
            r = doc.to_dict()

            if status_filter and r.get('status') != status_filter:
                continue

            created_at = r.get('createdAt')
            if hasattr(created_at, 'strftime'):
                created_str = created_at.strftime('%d %b %Y %H:%M')
            else:
                created_str = 'Recently'

            reviewed_at = r.get('reviewedAt')
            reviewed_str = ''
            if reviewed_at and hasattr(reviewed_at, 'strftime'):
                reviewed_str = reviewed_at.strftime('%d %b %Y %H:%M')

            requests_list.append({
                "requestId":        r.get('requestId'),
                "leadId":           r.get('leadId'),
                "leadName":         r.get('leadName', ''),
                "employeeName":     r.get('employeeName', ''),
                "requestedChanges": r.get('requestedChanges', {}),
                "currentValues":    r.get('currentValues', {}),
                "reason":           r.get('reason', ''),
                "status":           r.get('status', 'pending'),
                "createdAt":        created_str,
                "reviewedAt":       reviewed_str,
                "reviewNote":       r.get('reviewNote', ''),
            })

        # Sort newest first
        requests_list.sort(
            key=lambda x: x['createdAt'], reverse=True)

        pending_count = sum(
            1 for r in requests_list if r['status'] == 'pending')

        return jsonify({
            "requests":     requests_list,
            "total":        len(requests_list),
            "pendingCount": pending_count,
        })

    except Exception as e:
        print(f"Error fetching change requests: {e}")
        return jsonify({"error": str(e)}), 500


# ── ROUTE 3: M1 approves a change request ─────────────────────────────────────
@change_requests_bp.route(
    '/api/change-requests/<request_id>/approve', methods=['PATCH'])
def approve_change_request(request_id):
    """
    M1 Manager approves a change request.
    The lead contact details are updated immediately on approval.
    Employee receives a notification.

    Request body: { "reviewNote": "Confirmed with customer" }
    """
    auth_error = require_auth()
    if auth_error:
        return auth_error

    uid  = session['uid']
    role = session['role']

    if role not in ['m1_manager', 'm2_manager']:
        return jsonify({"error": "Only managers can approve requests"}), 403

    data        = request.get_json() or {}
    review_note = data.get('reviewNote', 'Approved by manager').strip()

    try:
        db      = get_firestore_client()
        req_ref = db.collection('change_requests').document(request_id)
        req_doc = req_ref.get()

        if not req_doc.exists:
            return jsonify({"error": "Change request not found"}), 404

        req_data = req_doc.to_dict()

        if req_data.get('status') != 'pending':
            return jsonify({
                "error": f"This request is already "
                         f"{req_data.get('status')}. "
                         f"Cannot approve again."
            }), 409

        # Verify M1 is reviewing their own team's request
        if role == 'm1_manager' and \
           req_data.get('m1ManagerUid') != uid:
            return jsonify({
                "error": "You can only approve requests from your team"
            }), 403

        lead_id           = req_data.get('leadId')
        requested_changes = req_data.get('requestedChanges', {})
        employee_uid      = req_data.get('employeeUid')
        lead_name         = req_data.get('leadName', '')

        # ── Apply the approved changes to the lead ─────────────────────────────
        update_data = {**requested_changes}
        update_data['updatedAt'] = firestore.SERVER_TIMESTAMP

        db.collection('leads').document(lead_id).update(update_data)

        # ── Write audit log ────────────────────────────────────────────────────
        lead_doc    = db.collection('leads').document(lead_id).get()
        lead_stage  = lead_doc.to_dict().get('currentStage', '') \
                      if lead_doc.exists else ''
        current_vals = req_data.get('currentValues', {})

        changes_summary = '; '.join([
            f"{field}: '{current_vals.get(field, '')}' "
            f"→ '{value}'"
            for field, value in requested_changes.items()
        ])

        log_id = str(uuid.uuid4())
        db.collection('audit_logs').document(log_id).set({
            "logId":        log_id,
            "leadId":       lead_id,
            "employeeUid":  employee_uid,
            "fromStage":    lead_stage,
            "toStage":      lead_stage,
            "changedAt":    firestore.SERVER_TIMESTAMP,
            "notes":        f"Contact update APPROVED by M1 Manager. "
                            f"Changes: {changes_summary}. "
                            f"Reason: {req_data.get('reason', '')}. "
                            f"Review note: {review_note}",
            "changeType":   "contact_update_approved",
        })

        # ── Mark request as approved ───────────────────────────────────────────
        req_ref.update({
            "status":     "approved",
            "reviewedAt": firestore.SERVER_TIMESTAMP,
            "reviewedBy": uid,
            "reviewNote": review_note,
        })

        # ── Notify employee ────────────────────────────────────────────────────
        notif_id = str(uuid.uuid4())
        db.collection('notifications').document(notif_id).set({
            "notifId":      notif_id,
            "recipientUid": employee_uid,
            "message":      f"✅ Your contact change request for "
                            f"'{lead_name}' has been APPROVED. "
                            f"Details have been updated.",
            "type":         "change_request_approved",
            "relatedId":    request_id,
            "isRead":       False,
            "createdAt":    firestore.SERVER_TIMESTAMP,
        })

        return jsonify({
            "message":   "Change request approved. "
                         "Lead details updated successfully.",
            "requestId": request_id,
            "leadId":    lead_id,
            "changes":   requested_changes
        })

    except Exception as e:
        print(f"Error approving change request: {e}")
        return jsonify({"error": str(e)}), 500


# ── ROUTE 4: M1 rejects a change request ──────────────────────────────────────
@change_requests_bp.route(
    '/api/change-requests/<request_id>/reject', methods=['PATCH'])
def reject_change_request(request_id):
    """
    M1 Manager rejects a change request.
    Lead details remain unchanged.
    Employee receives a notification with the rejection reason.

    Request body: { "reviewNote": "Cannot verify this information" }
    """
    auth_error = require_auth()
    if auth_error:
        return auth_error

    uid  = session['uid']
    role = session['role']

    if role not in ['m1_manager', 'm2_manager']:
        return jsonify({"error": "Only managers can reject requests"}), 403

    data        = request.get_json() or {}
    review_note = data.get('reviewNote', '').strip()

    if not review_note:
        return jsonify({
            "error": "Please provide a reason for rejection"
        }), 400

    try:
        db      = get_firestore_client()
        req_ref = db.collection('change_requests').document(request_id)
        req_doc = req_ref.get()

        if not req_doc.exists:
            return jsonify({"error": "Change request not found"}), 404

        req_data = req_doc.to_dict()

        if req_data.get('status') != 'pending':
            return jsonify({
                "error": f"This request is already "
                         f"{req_data.get('status')}."
            }), 409

        if role == 'm1_manager' and \
           req_data.get('m1ManagerUid') != uid:
            return jsonify({
                "error": "You can only reject requests from your team"
            }), 403

        employee_uid = req_data.get('employeeUid')
        lead_name    = req_data.get('leadName', '')

        # Mark as rejected
        req_ref.update({
            "status":     "rejected",
            "reviewedAt": firestore.SERVER_TIMESTAMP,
            "reviewedBy": uid,
            "reviewNote": review_note,
        })

        # Notify employee
        notif_id = str(uuid.uuid4())
        db.collection('notifications').document(notif_id).set({
            "notifId":      notif_id,
            "recipientUid": employee_uid,
            "message":      f"❌ Your contact change request for "
                            f"'{lead_name}' was REJECTED. "
                            f"Reason: {review_note}",
            "type":         "change_request_rejected",
            "relatedId":    request_id,
            "isRead":       False,
            "createdAt":    firestore.SERVER_TIMESTAMP,
        })

        return jsonify({
            "message":   "Change request rejected.",
            "requestId": request_id,
        })

    except Exception as e:
        print(f"Error rejecting change request: {e}")
        return jsonify({"error": str(e)}), 500