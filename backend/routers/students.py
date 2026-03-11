"""
Students API router
Endpoints:
- GET /api/students - List all students with latest risk predictions
- GET /api/students/{student_id} - Get full risk breakdown + 7-day history
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from datetime import datetime, timedelta
from backend.db import get_db

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("")
async def list_students(
    risk_level: str = None,
    limit: int = 100,
    db = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    List all students with their latest risk predictions.
    
    Query params:
    - risk_level: Filter by risk level (critical, high, medium, low)
    - limit: Maximum number of results (default: 100)
    """
    
    # Aggregation pipeline to join students with latest risk predictions
    pipeline = [
        {
            '$lookup': {
                'from': 'risk_predictions',
                'let': {'student_id': '$student_id'},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$student_id', '$$student_id']}}},
                    {'$sort': {'pred_date': -1}},
                    {'$limit': 1}
                ],
                'as': 'latest_risk'
            }
        },
        {'$unwind': {'path': '$latest_risk', 'preserveNullAndEmptyArrays': True}},
        {
            '$project': {
                '_id': 0,
                'student_id': 1,
                'archetype': 1,
                'risk_level': {'$ifNull': ['$latest_risk.risk_level', 'unknown']},
                'anomaly_score': {'$ifNull': ['$latest_risk.anomaly_score', 0]},
                'sleep_score': {'$ifNull': ['$latest_risk.sleep_score', 0]},
                'isolation_score': {'$ifNull': ['$latest_risk.isolation_score', 0]},
                'drift_score': {'$ifNull': ['$latest_risk.drift_score', 0]},
                'pred_date': {'$ifNull': ['$latest_risk.pred_date', None]},
                'model_version': {'$ifNull': ['$latest_risk.model_version', 'N/A']}
            }
        }
    ]
    
    # Add risk level filter if specified
    if risk_level:
        pipeline.append({'$match': {'risk_level': risk_level}})
    
    # Add limit
    pipeline.append({'$limit': limit})
    
    students = []
    async for doc in db.students.aggregate(pipeline):
        # Convert datetime to ISO string
        if doc.get('pred_date'):
            doc['pred_date'] = doc['pred_date'].isoformat()
        students.append(doc)
    
    return students


@router.get("/{student_id}")
async def get_student_details(
    student_id: str,
    db = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed information for a specific student:
    - Latest risk prediction
    - 7-day behavioral history
    - Trend analysis
    """
    
    # Get latest risk prediction
    latest_risk = await db.risk_predictions.find_one(
        {'student_id': student_id},
        sort=[('pred_date', -1)]
    )
    
    if not latest_risk:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    
    # Get 7-day behavioral history
    seven_days_ago = datetime.now() - timedelta(days=7)
    behavioral_history = []
    
    cursor = db.behavioral_logs.find(
        {'student_id': student_id, 'date': {'$gte': seven_days_ago}}
    ).sort('date', -1).limit(7)
    
    async for log in cursor:
        log['_id'] = str(log['_id'])
        log['date'] = log['date'].isoformat()
        behavioral_history.append(log)
    
    # Get all risk predictions (for trend)
    risk_history = []
    cursor = db.risk_predictions.find(
        {'student_id': student_id}
    ).sort('pred_date', -1).limit(30)
    
    async for pred in cursor:
        pred['_id'] = str(pred['_id'])
        pred['pred_date'] = pred['pred_date'].isoformat()
        risk_history.append(pred)
    
    # Calculate trends
    trends = {
        'sleep_trend': 'stable',
        'isolation_trend': 'stable',
        'academic_trend': 'stable'
    }
    
    if len(behavioral_history) >= 2:
        # Simple trend: compare latest vs 7-day average
        latest = behavioral_history[0]
        avg_login = sum(log['login_hour_mean'] for log in behavioral_history) / len(behavioral_history)
        avg_dorm = sum(log['dorm_ratio'] for log in behavioral_history) / len(behavioral_history)
        avg_lead = sum(log['submission_lead_hrs'] for log in behavioral_history) / len(behavioral_history)
        
        if latest['login_hour_mean'] > avg_login + 1:
            trends['sleep_trend'] = 'concerning'
        elif latest['login_hour_mean'] < avg_login - 1:
            trends['sleep_trend'] = 'improving'
        
        if latest['dorm_ratio'] > avg_dorm + 0.1:
            trends['isolation_trend'] = 'concerning'
        elif latest['dorm_ratio'] < avg_dorm - 0.1:
            trends['isolation_trend'] = 'improving'
        
        if latest['submission_lead_hrs'] < avg_lead - 0.5:
            trends['academic_trend'] = 'concerning'
        elif latest['submission_lead_hrs'] > avg_lead + 0.5:
            trends['academic_trend'] = 'improving'
    
    # Prepare response
    latest_risk['_id'] = str(latest_risk['_id'])
    latest_risk['pred_date'] = latest_risk['pred_date'].isoformat()
    
    return {
        'student_id': student_id,
        'latest_risk': latest_risk,
        'behavioral_history': behavioral_history,
        'risk_history': risk_history,
        'trends': trends,
        'behavioral_signals': generate_behavioral_signals(latest_risk, behavioral_history)
    }


def generate_behavioral_signals(risk: Dict, history: List[Dict]) -> List[Dict[str, str]]:
    """Generate human-readable behavioral signals for counsellor dashboard."""
    signals = []
    
    if risk['sleep_score'] > 0.7:
        signals.append({
            'type': 'sleep',
            'severity': 'high' if risk['sleep_score'] > 0.85 else 'medium',
            'message': f"Sleep disruption detected - Login patterns indicate late-night activity (avg {history[0]['login_hour_mean']:.1f}:00)"
        })
    
    if risk['isolation_score'] > 0.7:
        signals.append({
            'type': 'isolation',
            'severity': 'high' if risk['isolation_score'] > 0.85 else 'medium',
            'message': f"Social isolation patterns - {history[0]['dorm_ratio']*100:.0f}% of time in dorm, {history[0]['social_zone_visits']} social visits"
        })
    
    if risk['drift_score'] > 0.7:
        signals.append({
            'type': 'academic',
            'severity': 'high' if risk['drift_score'] > 0.85 else 'medium',
            'message': f"Academic engagement decline - Submissions within {history[0]['submission_lead_hrs']:.1f}hrs of deadline"
        })
    
    if not signals:
        signals.append({
            'type': 'normal',
            'severity': 'low',
            'message': 'No significant behavioral changes detected'
        })
    
    return signals
