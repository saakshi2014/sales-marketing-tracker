"""
stages.py — Pipeline Stages API Routes
Provides the list of active pipeline stages to the frontend.
"""

from flask import Blueprint, jsonify, session
from firebase_config import get_firestore_client

stages_bp = Blueprint('stages', __name__)


@stages_bp.route('/api/stages', methods=['GET'])
def get_stages():
    """
    Returns all active pipeline stages ordered by stageOrder.
    Used by the Add Lead form and stage-change dropdown.
    Any logged-in user can access this.
    """
    if 'uid' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        db = get_firestore_client()

        # Fetch all stages then filter and sort in Python
        # This avoids needing a composite Firestore index
        all_stages = db.collection('pipeline_stages').get()

        stages = sorted(
            [s for s in all_stages if s.to_dict().get('isActive', True)],
            key=lambda x: x.to_dict().get('stageOrder', 0)
        )

        stages_list = []
        for stage in stages:
            data = stage.to_dict()
            stages_list.append({
                "stageId":     data.get('stageId'),
                "stageNumber": data.get('stageNumber'),
                "stageName":   data.get('stageName'),
                "description": data.get('description'),
                "stageOrder":  data.get('stageOrder'),
                "isArchived":  data.get('isArchived', False),
            })

        return jsonify({
            "stages": stages_list,
            "total":  len(stages_list)
        })

    except Exception as e:
        print(f"Error fetching stages: {e}")
        return jsonify({"error": str(e)}), 500
