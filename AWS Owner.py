import csv
import random
from faker import Faker

# Set output path
output_path = ""

# Initialize Faker
fake = Faker()

# Number of synthetic records
num_records = 750

# Generate one synthetic patient record
def generate_mediscan_data():
    return {
        "patient_id": fake.uuid4(),
        "name": fake.name(),
        "age": random.randint(18, 90),
        "heart_rate": random.randint(50, 120),     # bpm
        "bp_systolic": random.randint(90, 180),    # mmHg
        "bp_diastolic": random.randint(60, 120),   # mmHg
        "glucose": random.randint(70, 200),        # mg/dL
        "diagnosis_date": fake.date_this_year(),
        "country": fake.country()
    }

# Write to CSV
with open(output_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=[
        "patient_id", "name", "age", "heart_rate",
        "bp_systolic", "bp_diastolic", "glucose",
        "diagnosis_date", "country"
    ])
    writer.writeheader()
    for _ in range(num_records):
        writer.writerow(generate_mediscan_data())

print(f"File generated: {output_path}")
