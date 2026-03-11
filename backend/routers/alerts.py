"""
Alerts API router
Endpoints:
- GET /api/alerts - Get all critical/high risk alerts
- POST /api/alerts/{student_id}/assign - Assign counsellor to student
- POST /api/identity/reveal - Decrypt identity (with access logging)
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import os
from backend.db import get_db

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AssignmentRequest(BaseModel):
    counsellor_id: str
    notes: str = ""


class RevealRequest(BaseModel):
    student_id: str
    admin_id: str
    reason: str


@router.get("")
async def get_alerts(
    db = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all students with critical or high risk levels.
    Returns enriched data with recommendations.
    """
    
    # Find latest critical/high risk predictions
    pipeline = [
        {
            '$match': {
                'risk_level': {'$in': ['critical', 'high']}
            }
        },
        {
            '$sort': {'pred_date': -1}
        },
        {
            '$group': {
                '_id': '$student_id',
                'latest': {'$first': '$$ROOT'}
            }
        },
        {
            '$replaceRoot': {'newRoot': '$latest'}
        },
        {
            '$lookup': {
                'from': 'behavioral_logs',
                'let': {'student_id': '$student_id'},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$student_id', '$$student_id']}}},
                    {'$sort': {'date': -1}},
                    {'$limit': 1}
                ],
                'as': 'latest_behavior'
            }
        },
        {
            '$unwind': {'path': '$latest_behavior', 'preserveNullAndEmptyArrays': True}
        },
        {
            '$sort': {'anomaly_score': -1}
        }
    ]
    
    alerts = []
    async for doc in db.risk_predictions.aggregate(pipeline):
        doc['_id'] = str(doc['_id'])
        doc['pred_date'] = doc['pred_date'].isoformat()
        
        if 'latest_behavior' in doc:
            doc['latest_behavior']['_id'] = str(doc['latest_behavior']['_id'])
            doc['latest_behavior']['date'] = doc['latest_behavior']['date'].isoformat()
        
        # Add AI-generated recommendation
        doc['recommendation'] = generate_recommendation(doc)
        
        alerts.append(doc)
    
    return alerts


@router.post("/{student_id}/assign")
async def assign_counsellor(
    student_id: str,
    assignment: AssignmentRequest,
    db = Depends(get_db)
):
    """
    Assign a counsellor to a student alert.
    Updates the risk_predictions document with assignment info.
    """
    
    # Check if student exists in risk predictions
    latest_risk = await db.risk_predictions.find_one(
        {'student_id': student_id},
        sort=[('pred_date', -1)]
    )
    
    if not latest_risk:
        raise HTTPException(status_code=404, detail=f"No risk prediction found for {student_id}")
    
    # Update with assignment
    result = await db.risk_predictions.update_one(
        {'_id': latest_risk['_id']},
        {
            '$set': {
                'assigned_to': assignment.counsellor_id,
                'assignment_date': datetime.now(),
                'assignment_notes': assignment.notes,
                'status': 'assigned'
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to assign counsellor")
    
    return {
        'success': True,
        'student_id': student_id,
        'assigned_to': assignment.counsellor_id,
        'timestamp': datetime.now().isoformat()
    }


@router.post("/snooze/{student_id}")
async def snooze_alert(
    student_id: str,
    duration_hours: int = 24,
    db = Depends(get_db)
):
    """Snooze an alert for a specified duration (default 24 hours)."""
    
    snooze_until = datetime.now().timestamp() + (duration_hours * 3600)
    
    result = await db.risk_predictions.update_one(
        {'student_id': student_id},
        {
            '$set': {
                'snoozed_until': snooze_until,
                'status': 'snoozed'
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    return {
        'success': True,
        'student_id': student_id,
        'snoozed_until': datetime.fromtimestamp(snooze_until).isoformat()
    }


@router.post("/identity/reveal")
async def reveal_identity(
    request: RevealRequest,
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Decrypt and reveal student identity from identity_vault.
    
    CRITICAL: This operation is logged in access_log for audit trail.
    In production, this would:
    1. Verify admin has proper authorization
    2. Decrypt AES-256-GCM encrypted fields
    3. Log access with reason for FERPA compliance
    """
    
    # Get identity vault entry
    identity = await db.identity_vault.find_one({'student_id': request.student_id})
    
    if not identity:
        raise HTTPException(status_code=404, detail=f"Identity not found for {request.student_id}")
    
    # Log access (critical for audit trail)
    access_entry = {
        'admin_id': request.admin_id,
        'accessed_at': datetime.now(),
        'reason': request.reason,
        'ip_address': 'TODO: capture from request'
    }
    
    await db.identity_vault.update_one(
        {'student_id': request.student_id},
        {'$push': {'access_log': access_entry}}
    )
    
    # In production: decrypt using COUNSELLOR_KEY
    # For now, return mock encrypted format
    # Real implementation would use cryptography.fernet or AES-GCM
    
    return {
        'student_id': request.student_id,
        'name': identity['encrypted_name'],  # In prod: decrypt(encrypted_name)
        'email': identity['encrypted_email'],  # In prod: decrypt(encrypted_email)
        'access_logged': True,
        'accessed_by': request.admin_id,
        'accessed_at': access_entry['accessed_at'].isoformat(),
        'warning': '⚠️ This access has been logged for FERPA compliance'
    }


def generate_recommendation(risk_doc: Dict) -> str:
    """Generate AI-style recommendation text for counsellor."""
    
    risk_level = risk_doc['risk_level']
    sleep = risk_doc['sleep_score']
    isolation = risk_doc['isolation_score']
    drift = risk_doc['drift_score']
    
    recommendations = []
    
    if risk_level == 'critical':
        recommendations.append("🚨 IMMEDIATE ACTION RECOMMENDED:")
    else:
        recommendations.append("⚠️ EARLY INTERVENTION SUGGESTED:")
    
    # Sleep concerns
    if sleep > 0.8:
        recommendations.append(f"Sleep disruption is severe (score: {sleep:.2f}). Consider immediate wellness check and sleep hygiene counseling.")
    elif sleep > 0.6:
        recommendations.append(f"Sleep patterns showing concern (score: {sleep:.2f}). Schedule routine check-in within 3-5 days.")
    
    # Isolation concerns
    if isolation > 0.8:
        recommendations.append(f"Social isolation patterns detected (score: {isolation:.2f}). Encourage participation in campus activities or peer support groups.")
    elif isolation > 0.6:
        recommendations.append(f"Reduced social engagement (score: {isolation:.2f}). Consider connecting with student organizations.")
    
    # Academic drift
    if drift > 0.8:
        recommendations.append(f"Significant academic engagement decline (score: {drift:.2f}). Recommend meeting with academic advisor and review course load.")
    elif drift > 0.6:
        recommendations.append(f"Academic submission patterns irregular (score: {drift:.2f}). Proactive check-in suggested.")
    
    # Priority actions
    if risk_level == 'critical':
        recommendations.append("\n📋 PRIORITY: Contact within 24 hours. Consider in-person meeting.")
    else:
        recommendations.append("\n📋 Suggested follow-up within 3-5 business days via email or phone.")
    
    return " ".join(recommendations)


@router.get("/analytics")
async def get_analytics(db = Depends(get_db)) -> Dict[str, Any]:
    """Get analytics on alert distribution and model performance."""
    
    # Count by risk level
    pipeline = [
        {
            '$sort': {'pred_date': -1}
        },
        {
            '$group': {
                '_id': '$student_id',
                'latest': {'$first': '$$ROOT'}
            }
        },
        {
            '$replaceRoot': {'newRoot': '$latest'}
        },
        {
            '$group': {
                '_id': '$risk_level',
                'count': {'$sum': 1},
                'avg_anomaly': {'$avg': '$anomaly_score'}
            }
        }
    ]
    
    risk_counts = {}
    async for doc in db.risk_predictions.aggregate(pipeline):
        risk_counts[doc['_id']] = {
            'count': doc['count'],
            'avg_anomaly_score': round(doc['avg_anomaly'], 3)
        }
    
    # Total students
    total_students = await db.students.count_documents({})
    
    return {
        'total_students': total_students,
        'risk_distribution': risk_counts,
        'model_version': os.environ.get('MODEL_VERSION', 'v1.0'),
        'last_updated': datetime.now().isoformat()
    }
