import math
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import csv
import pandas as pd

TOTAL_NODES = 1000
NODE_INDEX = 500
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
      print("user_link", user_link)
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
   total_pages =    soup.find_all("a", class_="s-pagination--item js-pagination-item")
   return int(total_pages[-2].text)

def create_paginated_urls(url, offset, limit):
   print(offset, limit)
   urls = []
   for i in range(max(offset, 1), offset+limit):
      urls.append(f'{URL}&page={i}')
   return urls


if __name__ == "__main__":
   output_csv_file_name = "./outputs/data_with_headers"
   
   start_time = time.time()
   total_pages = get_total_pages(URL)
   PAGES_PER_NODE = math.ceil( total_pages / TOTAL_NODES)
   page_urls = create_paginated_urls("URL", NODE_INDEX*PAGES_PER_NODE, PAGES_PER_NODE)
   print("total_pages", page_urls)
   
   shape = (1, 7) 
   data = np.zeros(shape)
   for idx, paginated_url in enumerate(page_urls): 
      questions_arr = scrapeSearch(paginated_url)
      data = np.append(data, questions_arr, axis=0)
      #print("scraped batch: ", questions_arr)
   print("operation took --- %s seconds ---" % (time.time() - start_time))    
   print("shape", data.shape)
   headers = ["question_title", 'question_url', 'username', "user_profile_url", "votes", "answers", "views"]
   data_with_headers = np.vstack([headers, data[2:]])

   # Save array with headers to a CSV file
   #np.savetxt(f'{output_csv_file_name}.csv', data_with_headers, delimiter=',', fmt='%s',  quotechar='"')
   #data = np.genfromtxt(f'{output_csv_file_name}.csv', delimiter=',', names=True, dtype=None, encoding=None)
   with open('output.csv', 'w', newline='') as csvfile:
     # Create a CSV writer object
     writer = csv.writer(csvfile)
     
     # Write the headers
     writer.writerow(headers)
     
     # Write the data rows
     writer.writerows(data)
   df = pd.read_csv('output.csv')

   print(df) 