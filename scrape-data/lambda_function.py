import csv
import requests
import pg8000
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime
import time

def lambda_handler():
    # Function to scrape data from US clinical trials
    def scrape_clinical_trials():
        base_url = "https://clinicaltrials.gov/api/v2"
        endpoint = "/studies"
        # URL to pull 50 most recent clinical trials
        url = base_url + endpoint + "?format=csv&pageSize=50&sort=StartDate"
        max_retries = 3
        delay_between_retries = 5  # seconds
        
        # Retry logic
        for attempt in range(max_retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    # Process CSV data if successful
                    csv_data = StringIO(response.text)
                    reader = csv.DictReader(csv_data)
                    output_file_path = 'scrape-data/output/clinical_trials_us.csv'
                    now = datetime.now()
                    archive_path = f'scrape-data/archives/clinical_trials_us_{now}.csv'
                    
                    with open(output_file_path, mode='w', newline='') as file1, open(archive_path, mode='w', newline='') as file2:
                        # Create CSV writers for both files
                        writer1 = csv.DictWriter(file1, fieldnames=["study_title", "study_identifier", "conditions", "sponsor"])
                        writer2 = csv.DictWriter(file2, fieldnames=["study_title", "study_identifier", "conditions", "sponsor"])
                        
                        # Write the header for both files
                        writer1.writeheader()
                        writer2.writeheader()
                        
                        # Iterate through each row in the reader (input CSV data)
                        for row in reader:
                            # Filter and prepare the data
                            filtered_row = {
                                "study_title": row["Study Title"],
                                "study_identifier": row["NCT Number"], 
                                "conditions": row["Conditions"],
                                "sponsor": row["Sponsor"]
                            }
                            # Write the filtered row to both files
                            writer1.writerow(filtered_row)
                            writer2.writerow(filtered_row)

                    return  # Exit the function after successful request
                else:
                    print(f"Error: HTTP Status Code: {response.status_code}")
            except requests.RequestException as e:
                print(f"Request failed: {e}")
            
            # If the request failed, wait and retry
            print(f"Retrying... (Attempt {attempt + 1} of {max_retries})")
            time.sleep(delay_between_retries)

    # Function to scrape data from EU clinical trials
    def scrape_eu_ct():
        full_titles = []
        study_identifier = []
        conditions = []
        sponsors = []
        for i in range(1, 4):
            url = f'https://www.clinicaltrialsregister.eu/ctr-search/search?query=&page={i}'

            # Scrapes all data in table using Beautiful Soup
            try:
                # Send the request and handle potential network issues
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                # Finds all study titles in table
                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'Full Title:' in label.text:
                        full_title = td.text.strip().replace('Full Title:', '').strip()
                        full_titles.append(full_title)

                # Finds all study identifiers
                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'EudraCT Number:' in label.text:
                        number = td.text.strip().replace('EudraCT Number:', '').strip()
                        study_identifier.append(number)

                # Finds all study medical conditions in table
                for td in soup.find_all('td'):
                    label = td.find('span', class_='label')
                    if label and 'Medical condition:' in label.text:
                        condition = td.text.strip().replace('Medical condition:', '').strip()
                        conditions.append(condition)
                
                # Finds all study sponsors in table
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
        now = datetime.now()
        archive_path = f'scrape-data/archives/clinical_trials_eu_{now}.csv'

        # Open both output files in write mode
        with open(output_file_path, mode='w', newline='') as file1, open(archive_path, mode='w', newline='') as file2:
            # Create CSV writers for both files
            writer1 = csv.writer(file1)
            writer2 = csv.writer(file2)
            
            # Write the header for both files
            writer1.writerow(["study_title", "study_identifier", "conditions", "sponsor"])
            writer2.writerow(["study_title", "study_identifier", "conditions", "sponsor"])
            
            # Iterate through the data and write rows to both files
            for title, eudra, condition, sponsor in zip(full_titles, study_identifier, conditions, sponsors):
                row = [title, eudra, condition, sponsor]
                writer1.writerow(row)
                writer2.writerow(row)

    # Function to insert data from CSV to database
    def raw_tables():
        db_host = 'aws-0-us-west-1.pooler.supabase.com'
        db_name = 'postgres'
        db_user = 'user'
        db_password = 'pw'
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

    # Function to transform and combine data from US and EU clinical trials
    def transform_and_combine_trials():
        db_host = 'aws-0-us-west-1.pooler.supabase.com'
        db_name = 'postgres'
        db_user = 'user'
        db_password = 'pw'
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
            # inserts all combined data into sql table named "combined_trials" with the schema "transformed"
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

    # scrapes us clincial trials
    scrape_clinical_trials()
    # scrapes eu clinical trials
    scrape_eu_ct()
    # creates us and eu tables in raw schema
    raw_tables()
    # creates combined table with all clinical trials in transformed scema 
    transform_and_combine_trials()

# Start the process
lambda_handler()
