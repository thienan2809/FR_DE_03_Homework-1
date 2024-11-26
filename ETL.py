from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def extract():
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

def transform(extracted_data):
    df_data = pd.DataFrame(extracted_data)
    return df_data


def load(data):
    data.to_csv('university_ranking_result.csv', index = False)

def main():
    extracted_data = extract()
    df_data = transform(extracted_data)
    load(df_data)
    print("Data extraction, transformation and loading completed successfully! \n")

if __name__ == "__main__":
    main()