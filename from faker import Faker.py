import csv
from faker import Faker

fake = Faker()

file_path = "/Users/nithinrajulapati/Desktop/benchmark-users.csv"

with open(file_path, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "name", "email"])
    for i in range(1, 10001):
        writer.writerow([i, fake.name(), fake.email()])

print("CSV file created at:", file_path)
