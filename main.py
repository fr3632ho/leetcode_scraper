import json, requests, time, re, textwrap, pdfkit

from PyPDF2 import PdfFileMerger
from collections import defaultdict
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
HTML_TEST_PATH = r'./assets/test.html'
PDF_OUT_PATH = r'./assets/pdfs/pdf_'

# start a safari window
driver = webdriver.Safari(executable_path=DRIVER_PATH)

def create_problem_dictionary(problem_data) -> dict:
    # need diff, title, title_slug, total_acs, total_sub, question_id
    stat = problem_data[PROBLEM_STAT_KEY]
    obj = {k:stat[k] for k in stat if k in stat_keys}
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
    time.sleep(1)
    containers = driver.find_elements(by = By.CSS_SELECTOR, value = 'app-pattern-table.ng-star-inserted')        
    wanted = dict()
    for elem in containers:    
        button = elem.find_element(by = By.TAG_NAME, value="button")        
       
        hrefs = elem.find_elements(by = By.XPATH, value = ".//a[@href]")
        filtered_problems = []
        pattern = re.compile('(\/*[0-9a-z\-]*\/?)$')           
        for element in hrefs:
            reference = element.get_attribute('href')            
            if reference.startswith(LEETCODE_ENDPOINT):  
                problem_name = pattern.search(reference).group(1)[1:-1]            
                filtered_problems.append(problem_name)  

        pattern = re.compile('(^[^(]*)')
        key = pattern.search(button.text).group(1)
        wanted[key] = filtered_problems
             
    # Write to file    
    with open(JSON_WANTED_PATH, 'w', encoding='utf-8') as file:    
        print("Dumping {} Leetcode problems found on neetcode.io to file".format(305), file.name)    
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

def generate_header(item) -> str:
    level = item[PROBLEM_DIFFICULTY_KEY]['level']
    if level == 3:
        level = '<p style="color: red"> Hard </p>'
    elif level == 2:
        level = '<p style="color: orange"> Medium </p>'
    else:
        level = '<p style="color: green"> Easy </p>'
    problem_title = '<head> <strong> {} </strong> {}  </head>\n'.format(item[PROBLEM_TITLE_KEY], level)                  
    return problem_title

'''
Return a file path to the created pdf
'''
def download_single_leetcode_html(item : dict) -> str:
    driver.get(LEETCODE_ENDPOINT + item[PROBLEM_TITLE_SLUG_KEY])        
    element = driver.find_element(by = By.CSS_SELECTOR, value = "div.description__24sA")
    element = element.find_element(by = By.XPATH, value = ".//div[contains(@class, 'content__u3I1 question-content__JfgR')]")        
    
    text = textwrap.fill(element.get_attribute('innerHTML'), 80)
    # insert title of problem and difficulty
    problem_title = generate_header(item)
    match_end = re.search('<div>', text).span()[1]                
    text = text[:match_end] + problem_title + text[match_end:]

    with open(HTML_TEST_PATH, 'w') as file:
        file.write(text)            
        file.close()

    pdfkit.from_file(HTML_TEST_PATH, PDF_OUT_PATH)

    return text
     

def load_neetcode_data() -> dict:
    with open(JSON_WANTED_PATH, 'r') as file:
        return json.load(file)

def load_leetcode_data() -> dict:
    with open(JSON_DATA_PATH, 'r') as file:
        return json.load(file)    


def create_group_pdf(group_name : str, problems : list) -> str:
    # first create a title for the grouped pdf
    # loop through all problems and create a pdf for each and every problem
    # merge all pdfs into one 
    # return the path to said pdf
    return None

def create_pdf(problems : dict) -> None:

    for group_name, data in problems.items():
        create_group_pdf(group_name, data)

def main():           
    wanted = load_neetcode_data()    
    wanted_problems = {item:k for k,sublist in wanted.items() for item in sublist}    
    data_json = load_leetcode_data()
    
    filtered_problems = defaultdict(list)
    for problem_data in data_json[PROBLEM_KEY]:
        # Need to filter the data to only take problems that we want
        # Done by filtering on 'question__title_slug in wanted'    
        key = problem_data[PROBLEM_STAT_KEY][PROBLEM_TITLE_SLUG_KEY]
        if key in wanted_problems.keys():
            filtered_problems[key].append(create_problem_dictionary(problem_data))        

    create_pdf(filtered_problems)    

if __name__ == "__main__":
    try:
        main()
    finally:        
        driver.quit()
