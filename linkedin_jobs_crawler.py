from selenium import webdriver
import logging
import csv
from collections import deque
from bs4 import BeautifulSoup
from time import sleep
from random import uniform, randint
import argparse
import os
import sys

class LinkedInJobsCrawler(object):

    def __init__(self, start_url, output_file): #add arguments

        #Configuration options for webdriver
        chrome_options = webdriver.ChromeOptions() #define container for webdriver options
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--window-size=1280x1696')
        # chrome_options.add_argument('--hide-scrollbars')
        # chrome_options.add_argument('--enable-logging')
        # chrome_options.add_argument('--log-level=0')
        # chrome_options.add_argument('--v=99')
        # chrome_options.add_argument('--single-process')
        # chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')

        #Crawler-specific configuration
        self.script_directory = "/home/will/linkedin_jobs_crawler" #os.path.dirname(sys.argv[0]) path to running script directory
        self.output_filepath = self.script_directory + "/output"
        self.chromedriver_path = sys.argv[0]
        os.environ['PATH'] += ':'+self.chromedriver_path

        #Configuration options for LinkedIn Jobs Search (to account for changes in class/attribute names)
        self.job_entry_class = 'job-card-search--clickable' #class of clickable job entry within menu
        self.job_poster_class = "jobs-poster" #class of job poster profile
        self.company_name_class = "jobs-details-top-card__company-url" #class containing company name text
        self.job_position_class = "jobs-details-top-card__job-title" #class containing job title
        self.pagination_prefix = "&start=" #prefix for pagination part of url
        self.pagination_increment = 25 #entries per page part of url (defined by LinkedIn where a page starts after 25th entry)

        #Initialize browser
        self.browser = webdriver.Chrome(chrome_options=chrome_options)

        #Get user arguments (from command line)
        self.start_url = start_url
        self.output_file = self.output_filepath + '/' + output_file

        #Initialize crawler with the following attributes
        self.url_queue = deque([self.start_url])
        self.crawled_urls = []
        self.job_entry_queue = deque([])

    def load_page(self, url): #changes
        try:
            self.browser.get(url)
        except Exception as e:
            logging.exception(e)
            print("Invalid url. Specific error: {}".format(e))
            return

    def get_job_entries(self, url):
        try:
            job_entries = self.browser.find_elements_by_class_name(self.job_entry_class) #find appropriate menu options on page
        except Exception as e:
            logging.exception(e)
            print("Cannot find job entries on page. Specific error: {}".format(e))
            raise
        self.job_entry_queue.extend(job_entries)


    def get_soup(self):
        html = self.browser.page_source
        if html is not None:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        else:
            return

    def get_data(self, soup):
        company_name = soup.find("a", class_=self.company_name_class).contents
        company_name = company_name[0].strip()
        job_position = soup.find("h1", class_=self.job_position_class).contents
        job_position = job_position[0].strip()
        return (company_name, job_position)

    def output_to_csv(self, company_name, job_position, url):
        if os.path.exists(self.output_filepath) is not True:
            os.makedirs(self.output_filepath)
        if os.path.exists(self.output_file):
            active_file = open(self.output_file, 'a')
        else:
            active_file = open(self.output_file, 'w')
        writer = csv.writer(active_file)
        writer.writerow([company_name, job_position, url])

    def run_crawler(self):
        page_num = 0
        while len(self.url_queue):
            current_url = self.url_queue.popleft()
            print('Queue url is {}.'.format(current_url))
            self.crawled_urls.append(current_url) #Check for overall page url may be unnecessary
            self.load_page(current_url)
            print('Current url is {}.'.format(self.browser.current_url))
            self.get_job_entries(current_url)
            if len(self.job_entry_queue) == 0: #if the list is empty, break the loop and stop execution
                print("All job entries have been crawled for this query.")
                break
            print(self.job_entry_queue)
            while len(self.job_entry_queue):
                job_entry = self.job_entry_queue.popleft()
                sleep(uniform(1.5, 3.0)) #random delay to avoid timeouts
                job_entry.click()
                print('Clicked job entry: {}'.format(job_entry))
                current_url = self.browser.current_url
                print('Current url of job-data page: {}'.format(current_url))
                soup = self.get_soup()
                if soup is not None and current_url not in self.crawled_urls and self.browser.find_elements_by_class_name(self.job_poster_class):
                    self.crawled_urls.append(current_url)
                    company_name, job_position = self.get_data(soup)
                    print('Job poster found. Retrieved data from page (HTML soup).')
                    self.output_to_csv(job_position, company_name, current_url)
            page_num += 1
            print('Go to page: {}'.format(page_num))
            self.url_queue.append(self.start_url + self.pagination_prefix + "{}".format(str(self.pagination_increment*page_num)))
            if randint (1, 3) == 1:
                print("Next page loading delayed to avoid excessive requests and timeouts")
                sleep(uniform(10.0, 20.0))

#Main method including argument parser -- still in progress
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start_url', type=str)
    parser.add_argument('-o', '--output_file', type=lambda s:file_choices(("csv"),s))
    args = parser.parse_args()
    crawler_process = LinkedInJobsCrawler(args.start_url, args.output_file)
    crawler_process.run_crawler()
