import boto3
import os
import json
import pymysql
from botocore.exceptions import ClientError
import concurrent.futures

def get_db_credentials():
    secret_name = ""
    region_name = ""
    client = boto3.client("secretsmanager", region_name=region_name)
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        raise Exception("Error retrieving secret: " + str(e))

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
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Insert failed for {email}: {e}")

def lambda_handler(event, context):
    creds = get_db_credentials()
    host = os.environ['DB_HOST']
    user = creds['username']
    password = creds['password']

    users = [
        ("Nithin", "nithin@gmail.com"),
        ("Nani", "nani@gmail.com"),
        ("Lalitha", "lalitha@gmail.com"),
        ("Lucky", "lucky@gmail.com"),
        ("Niveditha", "nivi@gmail.com")
    ]

    try:
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

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(insert_user, host, user, password, name, email)
                for name, email in users
            ]
            for future in futures:
                future.result()

        return { "message": "Bulk insert successful" }

    except Exception as e:
        return { "error": str(e) }

