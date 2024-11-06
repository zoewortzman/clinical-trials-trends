import os
import csv
import requests
import pg8000
from io import StringIO
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    
    def scrape_clinical_trials():
        base_url = "https://clinicaltrials.gov/api/v2"
        endpoint = "/studies"
        url = base_url + endpoint + "?format=csv&pageSize=50&sort=StartDate"
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: HTTP Status Code: {response.status_code}")
            return
        csv_data = StringIO(response.text)  
        reader = csv.DictReader(csv_data)

        db_host = 'aws-0-us-west-1.pooler.supabase.com'
        db_name = 'postgres'
        db_user = 'user'
        db_password = 'pw'
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
        INSERT INTO clinical_trials (study_title, conditions, interventions, age, gender, start_date, locations)
        VALUES ( %s, %s, %s, %s, %s, %s, %s)
        """

        for row in reader:
            study_title = row['Study Title']
            conditions = row['Conditions']
            age = row['Age']
            gender = row['Sex']
            interventions = row['Interventions']
            start_date = row['Start Date']
            locations = row['Locations']
            cursor.execute(insert_query, (study_title, conditions,interventions,age, gender, start_date,locations,))
        conn.commit()
        cursor.close()
        conn.close()
    def scrape_eu_ct():
        url = "https://www.clinicaltrialsregister.eu/ctr-search/search?query=&dateFrom=2022-01-01&dateTo=2024-11-05"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        table_rows = soup.find_all("table", class_="result")


        full_titles = []
        for td in soup.find_all('td'):
            label = td.find('span', class_='label')
            if label and 'Full Title:' in label.text:
                full_title = td.text.strip().replace('Full Title:', '').strip()
                full_titles.append(full_title)

        ages = []
        for td in soup.find_all('td'):
            label = td.find('span', class_='label')
            if label and 'Age:' in label.text:
                age = td.text.strip().replace('Age:', '').strip()
                ages.append(age)

        genders = []
        for td in soup.find_all('td'):
            label = td.find('span', class_='label')
            if label and 'Gender:' in label.text:
                gender = td.text.strip().replace('Gender:', '').strip()
                genders.append(gender)

        conditions = []
        for td in soup.find_all('td'):
            label = td.find('span', class_='label')
            if label and 'Medical condition:' in label.text:
                condition = td.text.strip().replace('Medical condition:', '').strip()
                conditions.append(condition)

        csv_header = ['Study Title', 'Conditions', 'Age', 'Gender']

        csv_rows = []
        for i in range(len(conditions)):
            row = {
                'Conditions': conditions[i],
                'Age': ages[i],
                'Gender': genders[i],
                'Study Title': full_titles[i]
            }
            csv_rows.append(row)

        output = StringIO()
        csv_writer = csv.DictWriter(output, fieldnames=csv_header)
        csv_writer.writeheader()
        csv_writer.writerows(csv_rows) 
        csv_data = output.getvalue()
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        db_host = 'aws-0-us-west-1.pooler.supabase.com'
        db_name = 'postgres'
        db_user = 'user'
        db_password = 'pw'
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
        INSERT INTO clinical_trials (study_title, conditions, age, gender)
        VALUES (%s, %s, %s, %s)
        """

        for row in reader:
            study_title = row['Study Title']
            conditions = row['Conditions']
            age = row['Age']
            gender = row['Gender']
            cursor.execute(insert_query, (study_title, conditions, age, gender,))
        conn.commit()
        cursor.close()
        conn.close()
    scrape_clinical_trials()
    scrape_eu_ct()

    return {
        'statusCode': 200,
        'body': 'Data inserted successfully into PostgreSQL (Supabase)'
    }

