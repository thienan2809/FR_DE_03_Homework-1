from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Define ETL functions
def extract(**kwargs):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Start the browser and load the page
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.topuniversities.com/university-rankings/world-university-rankings/2023")
    driver.maximize_window()

    # Extract the required data
    ranks = [rank.text for rank in driver.find_elements("xpath", '//*[@class="rank-no"]')]
    universities = [uni.text for uni in driver.find_elements("xpath", '//*[@class="univ-names-text"]/a')]
    addresses = [addr.text for addr in driver.find_elements("xpath", '//div[@class="location"]')]
    scores = [score.text for score in driver.find_elements("xpath", '//span[@class="rank-score di-inline"]')]

    driver.quit()
    extracted_data = [
        {"Rank": ranks[i], "University": universities[i], "Address": addresses[i], "Overall Score": scores[i]}
        for i in range(len(ranks))
    ]
    kwargs['ti'].xcom_push(key='extracted_data', value=extracted_data)

def transform(**kwargs):
    ti = kwargs['ti']
    extracted_data = ti.xcom_pull(key='extracted_data', task_ids='extract')
    df_data = pd.DataFrame(extracted_data)
    kwargs['ti'].xcom_push(key='transformed_data', value=df_data.to_dict(orient='records'))

def load(**kwargs):
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(key='transformed_data', task_ids='transform')
    df_data = pd.DataFrame(transformed_data)
    df_data.to_csv('/tmp/university_ranking_result.csv', index=False)

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'university_ranking_etl',
    default_args=default_args,
    description='A simple ETL process for university rankings',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    task_extract = PythonOperator(
        task_id='extract',
        python_callable=extract,
        provide_context=True
    )

    task_transform = PythonOperator(
        task_id='transform',
        python_callable=transform,
        provide_context=True,
    )

    task_load = PythonOperator(
        task_id='load',
        python_callable=load,
        provide_context=True,
    )

    task_extract >> task_transform >> task_load
