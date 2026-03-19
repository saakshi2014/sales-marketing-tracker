"""
auth.py — Authentication Routes
Handles: token verification, user profile creation, role fetching
"""

from flask import Blueprint, request, jsonify, session
from firebase_config import get_firestore_client, get_auth_client

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/verify', methods=['POST'])
def verify_token():
    data  = request.get_json()
    token = data.get('token') if data else None

    if not token:
        return jsonify({"error": "No token provided"}), 400

    try:
        auth_client   = get_auth_client()
        decoded_token = auth_client.verify_id_token(token)
        uid           = decoded_token['uid']

        db       = get_firestore_client()
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User profile not found. Contact admin."}), 404

        user_data = user_doc.to_dict()
        role      = user_data.get('role', 'employee')

        session['uid']   = uid
        session['role']  = role
        session['email'] = user_data.get('email', '')

        return jsonify({
            "uid":   uid,
            "role":  role,
            "email": user_data.get('email', ''),
            "name":  user_data.get('displayName', '')
        })

    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({"error": str(e)}), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"})


@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    if 'uid' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    return jsonify({
        "uid":   session.get('uid'),
        "role":  session.get('role'),
        "email": session.get('email')
    })

