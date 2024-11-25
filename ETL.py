from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

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

def transform(driver):
    ranks = driver.find_elements("xpath", '//*[@class="rank-no"]')
    universities = driver.find_elements("xpath", '//*[@class="univ-names-text"]/a')
    address = driver.find_elements("xpath", '//div[@class="location"]')
    overall_scores = driver.find_elements("xpath", '//span[@class="rank-score di-inline"]')

    df = pd.DataFrame(columns = ['Rank', 'University', 'Address', 'Overall Score'])
    df_data = []

    for i in range(len(ranks)):
        temp_data = {'Rank': i + 1, 
                    'University': universities[i].text,
                    'Address': address[i].text,
                    'Overall Score': overall_scores[i].text
                    }
        df_data.append(temp_data)
    
    return df_data


def load(data):
    df_data = pd.DataFrame(data)
    df_data.to_csv('university_ranking_result.csv', index = False)

def main():
    driver = extract()
    df_data = transform(driver)
    load(df_data)
    print("Data extraction, transformation and loading completed successfully! \n")

if __name__ == "__main__":
    main()