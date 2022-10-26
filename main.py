import json, requests
from sys import api_version
import bs4

from selenium import webdriver

# Get json data form leetcode
API_ENDPOINT = "https://leetcode.com/api/problems/algorithms/"
# Used when locating a problem with selenium
BASE_ENDPOINT = "https://leetcode.com/problems/"

# Main key for json object
PROBLEM_KEY = 'stat_status_pairs'


DRIVER_PATH = r'/usr/bin/safaridriver'
JSON_DATA_PATH = r'./assets/leetcode_data.json'

# start a safari window
driver = webdriver.Safari(executable_path=DRIVER_PATH)

def main():
    response = requests.get(API_ENDPOINT)
    data_json = response.json()    
    
    with open(JSON_DATA_PATH, 'w', encoding='utf-8') as file:
        json.dump(data_json, file, ensure_ascii=False, indent=4)
        print("Dumped API contents into",file.name)
    
    for problem_data in data_json[PROBLEM_KEY]:


    


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
