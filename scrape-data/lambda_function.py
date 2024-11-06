import os
import csv
import requests
import pg8000
from io import StringIO
from bs4 import BeautifulSoup

def lambda_handler():
    # scrapes data from US clinical trials
    def scrape_clinical_trials():
        base_url = "https://clinicaltrials.gov/api/v2"
        endpoint = "/studies"
        # takes sample of 50 most recent clincial trials
        url = base_url + endpoint + "?format=csv&pageSize=50&sort=StartDate"
        max_retries = 3
        delay_between_retries = 5  # seconds
        # pulls data from clinical trials API
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: HTTP Status Code: {response.status_code}")
            return
        
        csv_data = StringIO(response.text)  
        reader = csv.DictReader(csv_data)
        output_file_path = 'scrape-data/output/clinical_trials_us.csv'

        with open(output_file_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["study_title", "study_identifier", "conditions", "sponsor"])
            writer.writeheader()

            for row in reader:
                filtered_row = {
                    "study_title": row["Study Title"],
                    "study_identifier": row["NCT Number"], 
                    "conditions": row["Conditions"],
                    "sponsor": row["Sponsor"]
                }
                writer.writerow(filtered_row)

    def scrape_eu_ct():
        full_titles = []
        study_identifier = []
        conditions = []
        sponsors = []
        for i in range(1, 4):
            url = f'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&page={i}'

        # scrapes all data in table using Beautiful Soup
            try:
            # Send the request and handle potential network issues
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

        # finds all study titles in table
        
                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'Full Title:' in label.text:
                        full_title = td.text.strip().replace('Full Title:', '').strip()
                        full_titles.append(full_title)

                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'EudraCT Number:' in label.text:
                        number = td.text.strip().replace('EudraCT Number:', '').strip()
                        study_identifier.append(number)

                # finds all study medical conditions in table
                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'Medical condition:' in label.text:
                        condition = td.text.strip().replace('Medical condition:', '').strip()
                        conditions.append(condition)

                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'Sponsor Name:' in label.text:
                        sponsor = td.text.strip().replace('Sponsor Name:', '').strip()
                        sponsors.append(sponsor)

            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch data from {url}: {e}")
                continue

            except Exception as e:
                print(f"An error occurred while processing the page: {e}")
                continue

        output_file_path = 'scrape-data/output/clinical_trials_eu.csv'

        with open(output_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["study_title", "study_identifier", "conditions", "sponsor"])
            for title, eudra, condition, sponsor in zip(full_titles, study_identifier, conditions, sponsors):
                writer.writerow([title, eudra, condition, sponsor])

    def raw_tables():
        db_host = 'aws-0-us-west-1.pooler.supabase.com'
        db_name = 'postgres'
        db_user = 'postgres.kbjyfacfzxiudtrisvmc'
        db_password = '87!RLg2Cy#AKk3U'
        db_port = '5432' 

        try:
            # Connect to the database
            conn = pg8000.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)
            cursor = conn.cursor()

            # Create schema if it doesn't exist
            cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            
            # SQL template for creating tables
            create_table_sql = """
                CREATE TABLE IF NOT EXISTS raw.{table_name} (
                    "study_title" TEXT,
                    "study_identifier" TEXT,
                    "conditions" TEXT,
                    "sponsor" TEXT, 
                    "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """

            for table in ["us", "eu"]:
                # Drop table if it exists and create a new one
                cursor.execute(f"DROP TABLE IF EXISTS raw.{table};")
                cursor.execute(create_table_sql.format(table_name=table))
                
                # Insert CSV data
                with open(f'scrape-data/output/clinical_trials_{table}.csv', newline='') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        cursor.execute(f"""
                            INSERT INTO raw.{table} ("study_title", "study_identifier", "conditions", "sponsor")
                            VALUES (%s, %s, %s, %s);
                        """, (row["study_title"], row["study_identifier"], row["conditions"], row["sponsor"]))

            # Commit the transaction
            conn.commit()
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            cursor.close()
            conn.close()

    def transform_and_combine_trials():
        db_host = 'aws-0-us-west-1.pooler.supabase.com'
        db_name = 'postgres'
        db_user = 'postgres.kbjyfacfzxiudtrisvmc'
        db_password = '87!RLg2Cy#AKk3U'
        db_port = '5432'

        try:
            # Connect to the database
            conn = pg8000.connect(user=db_user, password=db_password, host=db_host, port=db_port, database=db_name)
            cursor = conn.cursor()
            print("Connected to the database.")

            cursor.execute("CREATE SCHEMA IF NOT EXISTS transformed;")

            create_combined_table_sql = """
                CREATE TABLE IF NOT EXISTS transformed.combined_trials (
                    "study_title" TEXT,
                    "study_identifier" TEXT,
                    "conditions" TEXT,
                    "sponsor" TEXT,
                    "source" TEXT,
                    "created_at" TIMESTAMP
                );
            """
            cursor.execute(create_combined_table_sql)
            for table, source in [("us", "ClinicalTrials.gov"), ("eu", "EudraCT")]:
                cursor.execute(f"""
                    INSERT INTO transformed.combined_trials (
                        "study_title", "study_identifier", "conditions", "sponsor", "created_at", "source"
                    )
                    SELECT "study_title", "study_identifier", "conditions", "sponsor", "created_at", %s
                    FROM raw.{table};
                """, (source,))
                print(f"Data from raw.{table} added to combined_trials with source '{source}'.")
            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            cursor.close()
            conn.close()

    
    
    #scrape_clinical_trials()
    #scrape_eu_ct()
    raw_tables()
    transform_and_combine_trials()

lambda_handler()
