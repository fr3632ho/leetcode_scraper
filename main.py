import json, requests, time, re
from sys import api_version
import bs4

from selenium import webdriver
from selenium.webdriver.common.by import By

# Get json data form leetcode
API_ENDPOINT = "https://leetcode.com/api/problems/algorithms/"

# Used when locating a problem with selenium
LEETCODE_ENDPOINT = "https://leetcode.com/problems/"
NEETCODE_ENDPOINT = "https://neetcode.io/practice/"


# Main key for json object
PROBLEM_KEY = 'stat_status_pairs'
PROBLEM_STAT_KEY = 'stat'
PROBLEM_TITLE_SLUG_KEY = 'question__title_slug'
PROBLEM_TITLE_KEY = 'question__title'
PROBLEM_DIFFICULTY_KEY = 'difficulty'
PROBLEM_TOTAL_ACS_KEY = "total_acs"
PROBLEM_TOTAL_SUBMITTED_KEY = "total_submitted"
PROBLEM_ID_KEY = 'question_id'
stat_keys = [PROBLEM_TITLE_SLUG_KEY, \
             PROBLEM_TITLE_KEY, \
             PROBLEM_ID_KEY, \
             PROBLEM_TOTAL_ACS_KEY, \
             PROBLEM_TOTAL_SUBMITTED_KEY]


DRIVER_PATH = r'/usr/bin/safaridriver'
JSON_DATA_PATH = r'./assets/leetcode_data.json'
JSON_WANTED_PATH = r'./assets/wanted_problems.json'

# start a safari window
driver = webdriver.Safari(executable_path=DRIVER_PATH)

def create_problem_dictionary(problem_data) -> dict:
    # need diff, title, title_slug, total_acs, total_sub, question_id
    stat = problem_data[PROBLEM_STAT_KEY]
    obj = {k:stat[k] for k in stat}
    obj[PROBLEM_DIFFICULTY_KEY] = problem_data[PROBLEM_DIFFICULTY_KEY]
    return obj

def select_all_button():
    driver.find_element(by = By.PARTIAL_LINK_TEXT, value = 'NeetCode All').click()


'''
Fetch the wanted problems from neetcode.io and 
write these to file 'wanted_problems'.
'''
def fetch_wanted_problems() -> dict:    
    # load neetcode    
    driver.get(NEETCODE_ENDPOINT)    
    time.sleep(2)
    select_all_button()

    # containers = driver.find_elements(by = By.CLASS_NAME, value = 'ng-star-inserted')        
    # for elem in containers:    
    #     names = elem.find_elements(by = By.CLASS_NAME, value=r'ng-tns-c25-55')                
    #     print(names)

    # return dict()        
    hrefs = driver.find_elements(by = By.XPATH,value="//a[@href]")
    filtered_problems = []
    pattern = re.compile('(\/*[0-9a-z\-]*\/?)$')          
    for element in hrefs:
        reference = element.get_attribute('href')
        if reference.startswith(LEETCODE_ENDPOINT):  
            problem_name = pattern.search(reference).group(1)[1:-1]            
            filtered_problems.append(problem_name)  
    
    # Write to file
    wanted = dict()
    wanted['problems'] = filtered_problems
    with open(JSON_WANTED_PATH, 'w', encoding='utf-8') as file:    
        print("Dumping {} Leetcode problems found on neetcode.io to file".format(len(filtered_problems)), file.name)    
        json.dump(wanted, file, ensure_ascii=False, indent=4)    
    return wanted

def fetch_leetcode_data() -> dict:
    # Write to file and save data from leetcode
    response = requests.get(API_ENDPOINT)
    data_json = response.json() 
    with open(JSON_DATA_PATH, 'w', encoding='utf-8') as file:
        json.dump(data_json, file, ensure_ascii=False, indent=4)
        print("Dumped API contents into",file.name)
    return data_json

def main():           
    wanted = set(fetch_wanted_problems()['problems'])    
    data_json = fetch_leetcode_data()

    filtered_problems = []
    for problem_data in data_json[PROBLEM_KEY]:
        # Need to filter the data to only take problems that we want
        # Done by filtering on 'question__title_slug in wanted'        
        if problem_data[PROBLEM_STAT_KEY][PROBLEM_TITLE_SLUG_KEY] in wanted:
            filtered_problems.append(create_problem_dictionary(problem_data))
    
    # TODO we need to download the description of each problem to one page
    # 

if __name__ == "__main__":
    try:
        main()
    finally:        
        driver.quit()
