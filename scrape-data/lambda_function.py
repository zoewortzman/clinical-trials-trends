import os
import csv
import requests
import pg8000
from io import StringIO

def lambda_handler(event, context):
    base_url = "https://clinicaltrials.gov/api/v2"
    endpoint = "/studies"
    url = base_url + endpoint + "?format=csv&pageSize=100&sort=StartDate"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: HTTP Status Code: {response.status_code}")
        return
    csv_data = StringIO(response.text)  
    reader = csv.DictReader(csv_data)

    db_host = 'aws-0-us-west-1.pooler.supabase.com'
    db_name = 'postgres'
    db_user = 'user_name'
    db_password = 'password'
    db_port = '6543'

    conn = pg8000.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password,
        port=db_port
    )
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO clinical_trials (nct_number, study_title, study_url, conditions, interventions, age, start_date, completion_date, locations)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for row in reader:
        nct_number = row['NCT Number']
        study_title = row['Study Title']
        study_url = row['Study URL']
        conditions = row['Conditions']
        interventions = row['Interventions']
        age = row['Age']
        start_date = row['Start Date']
        completion_date = row['Completion Date']
        locations = row['Locations']
        cursor.execute(insert_query, (nct_number, study_title, study_url, conditions,interventions,age,start_date,completion_date,locations,))
    conn.commit()
    cursor.close()
    conn.close()
        
    # Return success response
    return {
        'statusCode': 200,
        'body': 'Data inserted successfully into PostgreSQL (Supabase)'
    }

