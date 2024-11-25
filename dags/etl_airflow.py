from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Define ETL functions
def extract():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')

    # you need to install the driver version that is compatible with your browser version, here is 124.0.6367.60
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.topuniversities.com/university-rankings/world-university-rankings/2023")
    driver.maximize_window()

    return driver

def transform(**kwargs):
    ti = kwargs['ti']
    driver = ti.xcom_pull(task_ids='extract')
    
    ranks = driver.find_elements("xpath", '//*[@class="rank-no"]')
    universities = driver.find_elements("xpath", '//*[@class="univ-names-text"]/a')
    address = driver.find_elements("xpath", '//div[@class="location"]')
    overall_scores = driver.find_elements("xpath", '//span[@class="rank-score di-inline"]')

    df = pd.DataFrame(columns=['Rank', 'University', 'Address', 'Overall Score'])

    result = []
    for i in range(len(ranks)):
        temp_data = {
            'Rank': i + 1,
            'University': universities[i].text,
            'Address': address[i].text,
            'Overall Score': overall_scores[i].text
        }
        result.append(temp_data)

    df_data = pd.DataFrame(result)
    return df_data

def load(**kwargs):
    ti = kwargs['ti']
    df_data = ti.xcom_pull(task_ids='transform')
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
