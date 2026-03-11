"""
Seed MongoDB with synthetic student data.
Loads generated JSON and creates indexes for optimal query performance.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/aura_db')
DB_NAME = 'aura_db'


async def seed_database():
    """Load synthetic data into MongoDB and create indexes."""
    print("=" * 60)
    print("AURA - MongoDB Seeding")
    print("=" * 60)
    
    # Connect to MongoDB
    print(f"\n🔌 Connecting to MongoDB: {MONGO_URI}")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    # Load generated data
    data_path = '/data/generated_data.json' if os.path.exists('/data/generated_data.json') else 'data/generated_data.json'
    
    if not os.path.exists(data_path):
        print(f"\n❌ Data file not found: {data_path}")
        print("   Run: python data/generate.py first")
        sys.exit(1)
    
    print(f"\n📂 Loading data from: {data_path}")
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    print(f"   Students: {len(data['students'])}")
    print(f"   Behavioral logs: {len(data['behavioral_logs'])}")
    print(f"   Identity vault: {len(data['identity_vault'])}")
    
    # Clear existing collections
    print("\n🗑️  Clearing existing collections...")
    await db.behavioral_logs.delete_many({})
    await db.students.delete_many({})
    await db.identity_vault.delete_many({})
    await db.risk_predictions.delete_many({})
    
    # Insert behavioral logs
    print("\n📥 Inserting behavioral_logs...")
    if data['behavioral_logs']:
        # Convert date strings to datetime objects
        for log in data['behavioral_logs']:
            log['date'] = datetime.fromisoformat(log['date'])
        
        result = await db.behavioral_logs.insert_many(data['behavioral_logs'])
        print(f"   Inserted {len(result.inserted_ids)} documents")
    
    # Insert students (with archetype for training ground truth)
    print("\n📥 Inserting students...")
    if data['students']:
        for student in data['students']:
            student['created_at'] = datetime.fromisoformat(student['created_at'])
        
        result = await db.students.insert_many(data['students'])
        print(f"   Inserted {len(result.inserted_ids)} documents")
    
    # Insert identity vault
    print("\n📥 Inserting identity_vault...")
    if data['identity_vault']:
        result = await db.identity_vault.insert_many(data['identity_vault'])
        print(f"   Inserted {len(result.inserted_ids)} documents")
    
    # Create indexes for optimal performance
    print("\n🔍 Creating indexes...")
    
    # behavioral_logs indexes
    await db.behavioral_logs.create_index([('student_id', 1), ('date', -1)])
    print("   ✓ behavioral_logs: (student_id, date)")
    
    await db.behavioral_logs.create_index([('date', -1)])
    print("   ✓ behavioral_logs: (date)")
    
    # risk_predictions indexes
    await db.risk_predictions.create_index([('risk_level', 1), ('pred_date', -1)])
    print("   ✓ risk_predictions: (risk_level, pred_date)")
    
    await db.risk_predictions.create_index([('student_id', 1), ('pred_date', -1)])
    print("   ✓ risk_predictions: (student_id, pred_date)")
    
    # identity_vault index
    await db.identity_vault.create_index('student_id', unique=True)
    print("   ✓ identity_vault: (student_id) UNIQUE")
    
    # students index
    await db.students.create_index('student_id', unique=True)
    print("   ✓ students: (student_id) UNIQUE")
    
    # Create TTL index for data retention (90 days)
    await db.behavioral_logs.create_index('date', expireAfterSeconds=90*24*60*60)
    print("   ✓ behavioral_logs: TTL index (90 days)")
    
    # Verify data
    print("\n📊 Verification:")
    counts = {
        'behavioral_logs': await db.behavioral_logs.count_documents({}),
        'students': await db.students.count_documents({}),
        'identity_vault': await db.identity_vault.count_documents({}),
        'risk_predictions': await db.risk_predictions.count_documents({})
    }
    
    for collection, count in counts.items():
        print(f"   {collection}: {count} documents")
    
    # Show sample archetype distribution
    print("\n📈 Risk Archetype Distribution:")
    pipeline = [
        {'$group': {'_id': '$archetype', 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    async for doc in db.students.aggregate(pipeline):
        print(f"   {doc['_id']}: {doc['count']} students")
    
    print("\n✅ Seeding complete!")
    print("\n💡 Next steps:")
    print("   1. Train model: python models/train.py")
    print("   2. Start API: uvicorn backend.main:app --reload")
    print("   3. Open dashboard: http://localhost:3000")
    
    client.close()


if __name__ == '__main__':
    asyncio.run(seed_database())
