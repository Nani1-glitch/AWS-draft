import boto3
import os
import json
import pymysql
from botocore.exceptions import ClientError
import concurrent.futures

# Get credentials from AWS Secrets Manager
def get_db_credentials():
    secret_name = "prod/AppBeta/Mysql"
    region_name = "us-east-1"
    client = boto3.client("secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        raise Exception("Error retrieving secret: " + str(e))

# Thread-safe DB insert (creates new connection & cursor)
def insert_user(host, user, password, name, email):
    try:
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database='userdb',
            connect_timeout=5
        )
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s)",
                (name, email)
            )
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Insert failed for {email}: {e}")

# Lambda entrypoint
def lambda_handler(event, context):
    creds = get_db_credentials()
    host = os.environ['DB_HOST']
    user = creds['username']
    password = creds['password']

    # Sample users to insert
    names = [
        ("Alpha", "alpha@lunexa.ai"),
        ("Beta", "beta@lunexa.ai"),
        ("Gamma", "gamma@lunexa.ai"),
        ("Delta", "delta@lunexa.ai"),
        ("Omega", "omega@lunexa.ai")
    ]

    try:
        # Step 1: Delete existing matching emails
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database='userdb',
            connect_timeout=5
        )
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE email LIKE '%@lunexa.ai'")
            conn.commit()
        conn.close()

        # Step 2: Insert new users in parallel using thread pool
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(insert_user, host, user, password, name, email)
                for name, email in names
            ]
            for f in futures:
                f.result()

        return {"message": "Bulk insert successful"}
    
    except Exception as e:
        return {"error": str(e)}
