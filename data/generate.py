"""
Generate synthetic student behavioral data with risk archetypes.
Creates 200 fake students with 60 days of behavioral logs each.
All names are pseudonymised using SHA-256 + salt.
"""

import os
import json
import hashlib
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

# Load salt from environment
SALT = os.environ.get('AURA_SALT', 'default_salt_for_dev')

def pseudonymise(name):
    """Convert real name to pseudonymised student ID using SHA-256."""
    hash_bytes = hashlib.sha256(f'{SALT}{name}'.encode()).digest()
    return 'STU#' + hash_bytes.hex()[:8].upper()


# Risk archetype definitions - behavioral parameter ranges
ARCHETYPES = {
    'critical': {
        'login_hour_mean': (2, 4),           # Late night logins 2-4 AM
        'login_hour_std': (0.5, 1.2),        # Consistent pattern
        'dorm_ratio': (0.9, 1.0),            # Almost always in dorm
        'social_zone_visits': (0, 1),        # Rarely visits social areas
        'wifi_zones_count': (1, 2),          # Very limited movement
        'submission_lead_hrs': (0, 0.1),     # Last-second submissions
        'lms_sessions': (1, 3),              # Low engagement
    },
    'high': {
        'login_hour_mean': (1, 3),
        'login_hour_std': (0.8, 1.5),
        'dorm_ratio': (0.7, 0.9),
        'social_zone_visits': (0, 2),
        'wifi_zones_count': (1, 3),
        'submission_lead_hrs': (0, 0.5),
        'lms_sessions': (2, 5),
    },
    'medium': {
        'login_hour_mean': (0, 1),
        'login_hour_std': (1.0, 2.0),
        'dorm_ratio': (0.5, 0.7),
        'social_zone_visits': (1, 3),
        'wifi_zones_count': (2, 4),
        'submission_lead_hrs': (0.5, 2.0),
        'lms_sessions': (3, 6),
    },
    'low': {
        'login_hour_mean': (-1, 0.5),        # Normal hours (offset adjusted)
        'login_hour_std': (2.0, 3.5),
        'dorm_ratio': (0.2, 0.5),
        'social_zone_visits': (3, 8),
        'wifi_zones_count': (4, 8),
        'submission_lead_hrs': (2.0, 24.0),
        'lms_sessions': (5, 12),
    }
}

# Distribution: 10% critical, 15% high, 25% medium, 50% low
ARCHETYPE_WEIGHTS = {
    'critical': 0.10,
    'high': 0.15,
    'medium': 0.25,
    'low': 0.50
}


def assign_risk_archetype():
    """Randomly assign a risk archetype based on distribution."""
    rand = random.random()
    cumsum = 0
    for archetype, weight in ARCHETYPE_WEIGHTS.items():
        cumsum += weight
        if rand < cumsum:
            return archetype
    return 'low'


def generate_behavioral_log(archetype, date, student_id):
    """Generate one day of behavioral data matching the archetype."""
    params = ARCHETYPES[archetype]
    
    # Add some day-to-day variation (±15%) and trend over time
    day_variation = lambda base: base * random.uniform(0.85, 1.15)
    
    # Generate login hour mean with adjustment for normal scale (12 = noon)
    login_base = random.uniform(*params['login_hour_mean'])
    login_hour_mean = max(0, min(23, 12 + login_base + random.gauss(0, 2)))
    
    log = {
        'student_id': student_id,
        'date': date.isoformat(),
        'login_hour_mean': round(login_hour_mean, 2),
        'login_hour_std': round(day_variation(random.uniform(*params['login_hour_std'])), 2),
        'dorm_ratio': round(max(0, min(1, day_variation(random.uniform(*params['dorm_ratio'])))), 3),
        'social_zone_visits': int(day_variation(random.randint(*params['social_zone_visits']))),
        'wifi_zones_count': int(day_variation(random.randint(*params['wifi_zones_count']))),
        'submission_lead_hrs': round(day_variation(random.uniform(*params['submission_lead_hrs'])), 2),
        'lms_sessions': int(day_variation(random.randint(*params['lms_sessions']))),
    }
    
    return log


def generate_student_data():
    """Generate complete dataset of 200 students with 60 days of logs each."""
    students = []
    behavioral_logs = []
    identity_vault = []
    
    start_date = datetime.now() - timedelta(days=60)
    
    print(f"🔐 Using salt: {SALT[:8]}...{SALT[-4:]}")
    print(f"📊 Generating data for 200 students over 60 days...")
    
    archetype_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    for i in range(200):
        # Generate fake identity
        name = fake.name()
        email = fake.email()
        
        # Pseudonymise
        student_id = pseudonymise(name)
        
        # Assign risk archetype
        archetype = assign_risk_archetype()
        archetype_counts[archetype] += 1
        
        # Store in identity vault (encrypted in production)
        identity_vault.append({
            'student_id': student_id,
            'encrypted_name': name,  # In production: AES-256-GCM
            'encrypted_email': email,  # In production: AES-256-GCM
            'access_log': []
        })
        
        # Generate 60 days of behavioral logs
        for day in range(60):
            date = start_date + timedelta(days=day)
            log = generate_behavioral_log(archetype, date, student_id)
            behavioral_logs.append(log)
        
        students.append({
            'student_id': student_id,
            'archetype': archetype,  # Ground truth for training
            'created_at': start_date.isoformat()
        })
        
        if (i + 1) % 50 == 0:
            print(f"   Generated {i + 1}/200 students...")
    
    print(f"\n✅ Generation complete!")
    print(f"   Critical: {archetype_counts['critical']} ({archetype_counts['critical']/2}%)")
    print(f"   High:     {archetype_counts['high']} ({archetype_counts['high']/2}%)")
    print(f"   Medium:   {archetype_counts['medium']} ({archetype_counts['medium']/2}%)")
    print(f"   Low:      {archetype_counts['low']} ({archetype_counts['low']/2}%)")
    print(f"   Total behavioral logs: {len(behavioral_logs)}")
    
    return {
        'students': students,
        'behavioral_logs': behavioral_logs,
        'identity_vault': identity_vault
    }


def save_to_json(data, output_path='data/generated_data.json'):
    """Save generated data to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Saved to: {output_path}")
    print(f"   File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    print("=" * 60)
    print("AURA - Synthetic Student Data Generator")
    print("Privacy-first behavioral metadata (no PII)")
    print("=" * 60)
    
    data = generate_student_data()
    save_to_json(data)
    
    print("\n✨ Ready for MongoDB seeding with: python data/seed_mongo.py")
