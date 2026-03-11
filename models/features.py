"""
Feature Engineering for AURA ML Model
Extracts meaningful features from behavioral_logs for risk prediction.

Features generated:
- rolling_sleep_7d: 7-day rolling mean of login hours
- rolling_sleep_14d: 14-day rolling mean  
- isolation_streak: Consecutive days with dorm_ratio > 0.85
- submission_drift: Change in submission lead time vs baseline
- social_drop: Percentage decline in social zone visits
- personal_z_scores: Normalized features vs student's own baseline
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aura_db')


async def load_behavioral_data():
    """Load all behavioral logs from MongoDB."""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client['aura_db']
    
    print("📥 Loading behavioral logs from MongoDB...")
    logs = []
    async for log in db.behavioral_logs.find():
        logs.append(log)
    
    client.close()
    
    df = pd.DataFrame(logs)
    if '_id' in df.columns:
        df = df.drop('_id', axis=1)
    
    print(f"   Loaded {len(df)} behavioral log records")
    return df


def compute_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rolling window statistics per student."""
    print("🔄 Computing rolling window features...")
    
    # Sort by student and date
    df = df.sort_values(['student_id', 'date'])
    
    # Rolling windows for sleep patterns
    df['rolling_sleep_7d'] = df.groupby('student_id')['login_hour_mean'].transform(
        lambda x: x.rolling(window=7, min_periods=3).mean()
    )
    
    df['rolling_sleep_14d'] = df.groupby('student_id')['login_hour_mean'].transform(
        lambda x: x.rolling(window=14, min_periods=7).mean()
    )
    
    # Rolling dorm ratio
    df['rolling_dorm_7d'] = df.groupby('student_id')['dorm_ratio'].transform(
        lambda x: x.rolling(window=7, min_periods=3).mean()
    )
    
    # Rolling social engagement
    df['rolling_social_7d'] = df.groupby('student_id')['social_zone_visits'].transform(
        lambda x: x.rolling(window=7, min_periods=3).mean()
    )
    
    print(f"   ✓ Rolling features computed")
    return df


def compute_isolation_streak(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate consecutive days with high dorm ratio (isolation indicator)."""
    print("🏠 Computing isolation streak...")
    
    df = df.sort_values(['student_id', 'date'])
    
    # Mark days with high dorm ratio (> 0.85)
    df['high_dorm_day'] = (df['dorm_ratio'] > 0.85).astype(int)
    
    # Calculate streak
    df['isolation_streak'] = 0
    
    for student_id in df['student_id'].unique():
        mask = df['student_id'] == student_id
        student_data = df[mask]['high_dorm_day'].values
        
        streak = 0
        streaks = []
        for val in student_data:
            if val == 1:
                streak += 1
            else:
                streak = 0
            streaks.append(streak)
        
        df.loc[mask, 'isolation_streak'] = streaks
    
    print(f"   ✓ Isolation streaks computed")
    return df


def compute_submission_drift(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate drift in submission lead time vs personal baseline."""
    print("📚 Computing submission drift...")
    
    df = df.sort_values(['student_id', 'date'])
    
    # Calculate 30-day baseline per student
    df['baseline_submission'] = df.groupby('student_id')['submission_lead_hrs'].transform(
        lambda x: x.rolling(window=30, min_periods=10).mean()
    )
    
    # Drift = current - baseline (negative = getting worse)
    df['submission_drift'] = df['submission_lead_hrs'] - df['baseline_submission']
    
    # Normalized drift score (0-1, where 1 = significant negative drift)
    df['drift_magnitude'] = np.abs(df['submission_drift'])
    max_drift = df['drift_magnitude'].quantile(0.95)
    df['submission_drift_score'] = np.clip(df['drift_magnitude'] / max_drift, 0, 1)
    
    # Higher score for negative drift (getting worse)
    df.loc[df['submission_drift'] < 0, 'submission_drift_score'] *= 1.5
    df['submission_drift_score'] = np.clip(df['submission_drift_score'], 0, 1)
    
    print(f"   ✓ Submission drift computed")
    return df


def compute_social_drop(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate percentage drop in social engagement."""
    print("👥 Computing social drop...")
    
    df = df.sort_values(['student_id', 'date'])
    
    # 30-day baseline social visits
    df['baseline_social'] = df.groupby('student_id')['social_zone_visits'].transform(
        lambda x: x.rolling(window=30, min_periods=10).mean()
    )
    
    # Current vs baseline (7-day avg)
    df['current_social'] = df.groupby('student_id')['social_zone_visits'].transform(
        lambda x: x.rolling(window=7, min_periods=3).mean()
    )
    
    # Percentage drop (0-1, where 1 = complete drop)
    df['social_drop'] = 0.0
    mask = df['baseline_social'] > 0
    df.loc[mask, 'social_drop'] = np.clip(
        1 - (df.loc[mask, 'current_social'] / df.loc[mask, 'baseline_social']),
        0, 1
    )
    
    print(f"   ✓ Social drop computed")
    return df


def compute_personal_z_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize features vs each student's personal baseline."""
    print("📊 Computing personalized Z-scores...")
    
    features_to_normalize = [
        'login_hour_mean', 'login_hour_std', 'dorm_ratio',
        'social_zone_visits', 'wifi_zones_count', 'submission_lead_hrs'
    ]
    
    for feature in features_to_normalize:
        # Calculate per-student mean and std
        student_means = df.groupby('student_id')[feature].transform('mean')
        student_stds = df.groupby('student_id')[feature].transform('std')
        
        # Z-score
        df[f'{feature}_zscore'] = 0.0
        mask = student_stds > 0
        df.loc[mask, f'{feature}_zscore'] = (
            (df.loc[mask, feature] - student_means[mask]) / student_stds[mask]
        )
    
    print(f"   ✓ Z-scores computed for {len(features_to_normalize)} features")
    return df


def extract_final_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract final feature set for model training."""
    print("🎯 Extracting final feature set...")
    
    # Remove rows with NaN from rolling windows (initial periods)
    df = df.dropna(subset=['rolling_sleep_7d', 'rolling_dorm_7d'])
    
    feature_columns = [
        # Original behavioral metrics
        'login_hour_mean', 'login_hour_std', 'dorm_ratio',
        'social_zone_visits', 'wifi_zones_count', 'submission_lead_hrs', 'lms_sessions',
        
        # Rolling features
        'rolling_sleep_7d', 'rolling_sleep_14d', 'rolling_dorm_7d', 'rolling_social_7d',
        
        # Derived features
        'isolation_streak', 'submission_drift_score', 'social_drop',
        
        # Personalized Z-scores
        'login_hour_mean_zscore', 'dorm_ratio_zscore', 'social_zone_visits_zscore',
        'submission_lead_hrs_zscore'
    ]
    
    # Keep metadata
    metadata_columns = ['student_id', 'date']
    
    final_df = df[metadata_columns + feature_columns].copy()
    
    print(f"   ✓ Final dataset: {len(final_df)} rows × {len(feature_columns)} features")
    print(f"   Features: {', '.join(feature_columns[:5])}...")
    
    return final_df


async def engineer_features():
    """Main pipeline for feature engineering."""
    print("=" * 60)
    print("AURA - Feature Engineering Pipeline")
    print("=" * 60)
    
    # Load data
    df = await load_behavioral_data()
    
    if df.empty:
        print("❌ No behavioral data found. Run: python data/seed_mongo.py")
        return None
    
    # Apply transformations
    df = compute_rolling_features(df)
    df = compute_isolation_streak(df)
    df = compute_submission_drift(df)
    df = compute_social_drop(df)
    df = compute_personal_z_scores(df)
    
    # Extract final features
    final_df = extract_final_features(df)
    
    # Save to CSV for model training
    output_path = 'models/features.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df.to_csv(output_path, index=False)
    
    print(f"\n💾 Features saved to: {output_path}")
    print(f"   Size: {os.path.getsize(output_path) / 1024:.2f} KB")
    print("\n✨ Ready for model training: python models/train.py")
    
    return final_df


if __name__ == '__main__':
    asyncio.run(engineer_features())
