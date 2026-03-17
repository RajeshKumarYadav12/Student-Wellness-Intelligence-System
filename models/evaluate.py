"""
Model Evaluation and Diagnostics
- Classification report
- Confusion matrix
- SHAP feature importance
- Model performance metrics
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import shap

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aura_db')
MODEL_VERSION = os.environ.get('MODEL_VERSION', 'v1.0')


def load_model():
    """Load trained model."""
    model_path = f'models/saved/aura_model_{MODEL_VERSION}.pkl'
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("   Run: python models/train.py first")
        sys.exit(1)
    
    print(f"📦 Loading model: {model_path}")
    model_data = joblib.load(model_path)
    
    print(f"   Version: {model_data['model_version']}")
    print(f"   Trained: {model_data['trained_at']}")
    
    return model_data


async def load_test_data():
    """Load test data with ground truth."""
    print("\n📥 Loading test data...")
    
    # Load features
    features_path = 'models/features.csv'
    features_df = pd.read_csv(features_path)
    
    # Load ground truth
    client = AsyncIOMotorClient(MONGO_URI)
    db = client['aura_db']
    
    students = []
    async for student in db.students.find():
        students.append({
            'student_id': student['student_id'],
            'archetype': student['archetype']
        })
    
    client.close()
    
    labels_df = pd.DataFrame(students)
    
    # Merge
    student_features = features_df.groupby('student_id').last().reset_index()
    merged = student_features.merge(labels_df, on='student_id', how='inner')
    
    print(f"   Test set: {len(merged)} students")
    
    return merged


def evaluate_model(model_data, df):
    """Evaluate model performance."""
    print("\n📊 Evaluating model performance...")
    
    # Prepare data
    feature_cols = model_data['feature_cols']
    X = df[feature_cols].values
    
    # True labels
    label_map = model_data['label_map']
    y_true = np.array([label_map[label] for label in df['archetype']])
    
    # Scale and predict
    X_scaled = model_data['scaler'].transform(X)
    y_pred = model_data['ensemble'].predict(X_scaled)
    
    # Reverse label map for display
    risk_levels = {v: k for k, v in label_map.items()}
    y_true_labels = [risk_levels[y] for y in y_true]
    y_pred_labels = [risk_levels[y] for y in y_pred]
    
    # Metrics
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='weighted')
    
    print(f"\n   Overall Accuracy: {accuracy:.3f}")
    print(f"   Weighted F1 Score: {f1:.3f}")
    
    # Classification report
    print("\n📋 Classification Report:")
    print(classification_report(
        y_true_labels, y_pred_labels,
        target_names=['critical', 'high', 'medium', 'low']
    ))
    
    return y_true, y_pred, y_true_labels, y_pred_labels


def plot_confusion_matrix(y_true_labels, y_pred_labels):
    """Plot and save confusion matrix."""
    print("\n📊 Generating confusion matrix...")
    
    cm = confusion_matrix(y_true_labels, y_pred_labels, labels=['critical', 'high', 'medium', 'low'])
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=['critical', 'high', 'medium', 'low'],
        yticklabels=['critical', 'high', 'medium', 'low']
    )
    plt.title('AURA Model - Confusion Matrix', fontsize=14, fontweight='bold')
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    
    output_path = 'models/confusion_matrix.png'
    plt.savefig(output_path, dpi=300)
    print(f"   ✓ Saved: {output_path}")
    plt.close()


def analyze_shap(model_data, X, feature_cols):
    """Generate SHAP feature importance analysis."""
    print("\n🔍 SHAP Feature Importance Analysis...")
    
    try:
        # Use a sample for SHAP (computationally expensive)
        sample_size = min(100, len(X))
        X_sample = X[:sample_size]
        
        X_scaled = model_data['scaler'].transform(X_sample)
        
        # Get XGBoost model from ensemble
        xgb_model = model_data['ensemble'].named_estimators_['xgb']
        
        # Create SHAP explainer
        explainer = shap.TreeExplainer(xgb_model)
        shap_values = explainer.shap_values(X_scaled)
        
        # Summary plot
        plt.figure(figsize=(12, 8))
        if isinstance(shap_values, list):
            # Multi-class: use class 3 (critical)
            shap.summary_plot(
                shap_values[3], X_scaled,
                feature_names=feature_cols,
                show=False
            )
        else:
            shap.summary_plot(
                shap_values, X_scaled,
                feature_names=feature_cols,
                show=False
            )
        
        plt.title('SHAP Feature Importance - Critical Risk Class', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        output_path = 'models/shap_summary.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✓ Saved: {output_path}")
        plt.close()
        
        # Feature importance ranking
        if isinstance(shap_values, list):
            mean_shap = np.abs(shap_values[3]).mean(axis=0)
        else:
            mean_shap = np.abs(shap_values).mean(axis=0)
        
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': mean_shap
        }).sort_values('importance', ascending=False)
        
        print("\n   Top 10 Most Important Features:")
        for i, row in feature_importance.head(10).iterrows():
            print(f"      {row['feature']}: {row['importance']:.4f}")
        
        # Save feature importance
        feature_importance.to_csv('models/feature_importance.csv', index=False)
        print(f"\n   ✓ Feature importance saved: models/feature_importance.csv")
        
    except Exception as e:
        print(f"   ⚠️ SHAP analysis failed: {e}")
        print("   (This is normal if SHAP is not installed)")


async def analyze_risk_distribution():
    """Analyze current risk distribution in database."""
    print("\n📈 Current Risk Distribution in Database...")
    
    async def _load():
        client = AsyncIOMotorClient(MONGO_URI)
        db = client['aura_db']
        
        predictions = []
        async for pred in db.risk_predictions.find():
            predictions.append(pred)
        
        client.close()
        return predictions
    
    predictions = await _load()
    
    if not predictions:
        print("   ⚠️ No predictions in database yet")
        return
    
    df = pd.DataFrame(predictions)
    
    print(f"   Total predictions: {len(df)}")
    print(f"\n   Risk level distribution:")
    for level, count in df['risk_level'].value_counts().items():
        pct = count / len(df) * 100
        print(f"      {level}: {count} ({pct:.1f}%)")
    
    print(f"\n   Score statistics:")
    print(f"      Anomaly score: μ={df['anomaly_score'].mean():.3f}, σ={df['anomaly_score'].std():.3f}")
    print(f"      Sleep score:   μ={df['sleep_score'].mean():.3f}, σ={df['sleep_score'].std():.3f}")
    print(f"      Isolation:     μ={df['isolation_score'].mean():.3f}, σ={df['isolation_score'].std():.3f}")
    print(f"      Drift:         μ={df['drift_score'].mean():.3f}, σ={df['drift_score'].std():.3f}")


async def main():
    """Main evaluation pipeline."""
    print("=" * 60)
    print("AURA - Model Evaluation")
    print("=" * 60)
    
    # Load model
    model_data = load_model()
    
    # Load test data
    df = await load_test_data()
    
    # Evaluate
    y_true, y_pred, y_true_labels, y_pred_labels = evaluate_model(model_data, df)
    
    # Confusion matrix
    plot_confusion_matrix(y_true_labels, y_pred_labels)
    
    # SHAP analysis
    feature_cols = model_data['feature_cols']
    X = df[feature_cols].values
    analyze_shap(model_data, X, feature_cols)
    
    # Risk distribution
    await analyze_risk_distribution()
    
    print("\n✅ Evaluation complete!")
    print("\n📁 Generated files:")
    print("   - models/confusion_matrix.png")
    print("   - models/shap_summary.png")
    print("   - models/feature_importance.csv")


if __name__ == '__main__':
    asyncio.run(main())
