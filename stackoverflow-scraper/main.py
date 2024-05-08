import errno
import math
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import csv
import fcntl
import os 

ARRAY_SIZE = os.environ.get('AWS_BATCH_JOB_ARRAY_SIZE', 1000)
ARRAY_INDEX = os.environ.get('AWS_BATCH_JOB_ARRAY_INDEX',2)

URL = "https://stackoverflow.com/collectives/aws?tab=questions&postfilter=subcommunityquestionpagefilter&subtab=newest&pagesize=50"

def find_key_in_dict(dictionary, strings):
    for string in strings:
        if string in dictionary:
            return dictionary.get(string)
    return None
 
def scrapeSearch(url):
   shape = (1, 7) 
   data = np.zeros(shape)
   
   response = requests.get(url)
   html_content = response.content
   soup = BeautifulSoup(html_content, 'html.parser')
   results = soup.find(id="questions")
   questions = results.find_all("div", id=lambda x: x and x.startswith('question-summary'))
   for question in questions:
      user_card = question.find("div", class_="s-user-card--info")
      user_name = user_card.find("a", class_="flex--item").text.strip() if  user_card.find("a", class_="flex--item") else None
      user_link  = user_card.find("a", class_="flex--item")["href"].strip() if  user_card.find("a", class_="flex--item") else None
      title = question.find("h3", class_="s-post-summary--content-title")
      question_url = title.find("a", class_="s-link")["href"]
      stats = question.find_all("div", class_=lambda x: x and x.startswith('s-post-summary--stats-item'))
      stats_data_extracted = {}
      for stat in stats:
         unit = stat.find("span", class_="s-post-summary--stats-item-unit")
         number = stat.find("span", class_="s-post-summary--stats-item-number")
         if number and unit: 
            stats_data_extracted[unit.text] = number.text.strip()
            
      new_data = np.array([[ title.text.strip(), question_url.strip(), user_name, user_link, find_key_in_dict(stats_data_extracted, ["votes", "vote"]) ,find_key_in_dict(stats_data_extracted, ["answers", "answer"]), find_key_in_dict(stats_data_extracted, ["views", "view"]) ]])
      data = np.append(data, new_data, axis=0)
   return data

def get_total_pages(url):
   response = requests.get(url)
   html_content = response.content
   soup = BeautifulSoup(html_content, 'html.parser')
   total_pages = soup.find_all("a", class_="s-pagination--item js-pagination-item")
   return int(total_pages[-2].text)

def create_paginated_urls(url, offset, limit):
   print(offset, limit)
   urls = []
   for i in range(max(offset, 1), offset+limit):
      urls.append(f'{URL}&page={i}')
   return urls

def append_array_to_csv(data, csv_file, max_attempts=5, retry_delay=1):
    lockfile = csv_file + ".lock"
    attempts = 0
    
    while attempts < max_attempts:
        try:
            # Acquire advisory lock
            with open(lockfile, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                
                # Append data to CSV file
                with open(csv_file, "a+", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(data)
                
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
                
            # Successful write, exit retry loop
            break
        except IOError as e:
            if e.errno in [errno.EAGAIN, errno.EWOULDBLOCK]:
                # File is locked, retry after delay
                attempts += 1
                time.sleep(retry_delay)
            else:
                # Other IO error occurred, raise it
                raise
    else:
        # Max attempts reached, raise an exception
        raise IOError("Failed to append to CSV file after {} attempts".format(max_attempts))

if __name__ == "__main__":
   start_time = time.time()
   TOTAL_PAGES = get_total_pages(URL)
   PAGES_PER_NODE = math.floor( TOTAL_PAGES / ARRAY_SIZE)
   REMAINDER = TOTAL_PAGES % ARRAY_SIZE

   page_urls = create_paginated_urls(URL, ARRAY_INDEX*PAGES_PER_NODE, PAGES_PER_NODE + 1  if ARRAY_INDEX <= REMAINDER else PAGES_PER_NODE)
   print("PAGES_PER_NODE", PAGES_PER_NODE)
   print("TOTAL_PAGES", TOTAL_PAGES)
   print("REMAINDER", REMAINDER)
   print("page_urls", page_urls)

   shape = (1, 7) 
   data = np.zeros(shape)
   for idx, paginated_url in enumerate(page_urls): 
      questions_arr = scrapeSearch(paginated_url)
      data = np.append(data, questions_arr, axis=0)
      #print("scraped batch: ", questions_arr)
   #headers = ["question_title", 'question_url', 'username', "user_profile_url", "votes", "answers", "views"]
   #data_with_headers = np.vstack([headers, data[2:]])
   csv_file = "/input/csv/data.csv"
   append_array_to_csv(data[2:], csv_file)
   print("operation took --- %s seconds ---" % (time.time() - start_time))    
