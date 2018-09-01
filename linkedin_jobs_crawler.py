from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import csv
from collections import deque
from bs4 import BeautifulSoup
from time import sleep
from random import uniform, randint
import argparse
import os
import sys
from inspect import getsourcefile
import platform

class LinkedInJobsCrawler(object):

    def __init__(self, keyword, location, output_file): #add arguments

        #Crawler configuration for file paths and types
        self.script_directory = os.path.dirname(os.path.abspath(getsourcefile(lambda:0))) #get directory of this script file
        self.output_filepath = self.script_directory + "/output"
        self.chromedriver_path = self.script_directory + '/chromedriver'
        self.supported_outputs = ['csv']

        #Configuration options for webdriver (left empty as a placeholder)
        chrome_options = webdriver.ChromeOptions() #define container for webdriver options
        self.login_timeout = 120 #Time in seconds to throw an exception if not logged in

        #Configuration options for LinkedIn Jobs Search (to account for changes in class/attribute names)
        self.job_entries_menu = "jobs-search-results" #class that contains job entries
        self.job_entry_class = "job-card-search--clickable" #class of clickable job entry within menu
        self.job_poster_class = "jobs-poster" #class of job poster profile
        self.company_name_class = "jobs-details-top-card__company-url" #class containing company name text
        self.job_position_class = "jobs-details-top-card__job-title" #class containing job title
        self.pagination_prefix = "&start=" #prefix for pagination part of urlstart_url
        self.pagination_increment = 25 #entries per page part of url (defined byprevent webdriver timeout exception site:stackoverflow.com LinkedIn where a page starts after 25th entry)

        #Initialize browser
        self.browser = webdriver.Chrome(executable_path=self.chromedriver_path, chrome_options=chrome_options)

        #Get user arguments (from command line)
        self.keyword = keyword
        self.location = location
        file_extension = output_file.split('.')[1]
        if file_extension not in self.supported_outputs:
            raise ValueError("Supported output files: {}".format(self.supported_output))
        self.output_file = self.output_filepath + '/' + output_file

        #Define crawler base and start urls
        self.base_url = 'https://www.linkedin.com' #linkedin homepage
        self.portal_url = self.base_url + '/feed' #page disploutput_file.split('.')[1]ayed after login
        self.start_url = '{0}/jobs/search/?keywords={1}&location={2}'.format(self.base_url, self.keyword, self.location) #start_url that contains job entries to be evaluated

        #Create queues containing urls and job entries to evaluate. Keep track of crawled urls
        self.url_queue = deque([self.start_url])
        self.crawled_urls = []
        self.job_entry_queue = deque([])

    def load_page(self, url):
        try:
            self.browser.get(url)
        except Exception as e:
            logging.exception(e)
            print("Invalid url. Specific error: {}".format(e))
            return

    def get_soup(self):
        html = self.browser.page_source
        if html is not None:
            soup = BeautifulSoup(html, 'lxml')
            return soup
        else:
            return

    def parse_content(self, soup):
        company_name = soup.find("a", class_=self.company_name_class).contents
        company_name = company_name[0].strip()
        job_position = soup.find("h1", class_=self.job_position_class).contents
        job_position = job_position[0].strip()
        return (company_name, job_position)

    def wait_for_login(self):
        self.load_page(self.base_url)
        print("Crawler waiting for user login. Log in to continue.")
        if self.browser.current_url is not self.portal_url:
            wait = WebDriverWait(self.browser, self.login_timeout)
            wait.until(EC.url_contains(self.portal_url))
        print("User is in home portal. Starting crawler.")

    def get_search_results_page(self):
        current_url = self.url_queue.popleft()
        print('Queue url is {}'.format(current_url))
        self.crawled_urls.append(current_url) #Check for overall page url may be unnecessary
        self.load_page(current_url)
        print('Loading queue url: {}'.format(self.browser.current_url))
        job_entries_menu = self.browser.find_element_by_class_name(self.job_entries_menu)
        job_entries_menu.send_keys(Keys.END)
        sleep(uniform(1.0, 1.5))
        return current_url

    def get_job_entries(self, url):
        try:
            job_entries = self.browser.find_elements_by_class_name(self.job_entry_class) #find appropriate menu options on page
        except Exception as e:
            print("Cannot find job entries on page. Specific error: {}".format(e))
            raise
        self.job_entry_queue.extend(job_entries)

    def load_entries(self):
        job_entry = self.job_entry_queue.popleft()
        sleep(uniform(1.5, 3.0)) #random delay to avoid timeouts
        job_entry.click()
        print('Clicked job entry: {}'.format(job_entry))
        current_url = self.browser.current_url
        print('Current url of job-data page: {}'.format(current_url))
        return current_url

    def output_to_csv(self, content_packets):
        if os.path.exists(self.output_filepath) is not True:
            os.makedirs(self.output_filepath)
        if os.path.exists(self.output_file):
            active_file = open(self.output_file, 'a')
        else:
            active_file = open(self.output_file, 'w')
        writer = csv.writer(active_file)
        for content_packet in content_packets:
            writer.writerow(content_packet)

    def check_for_completion(self, url):
        self.load_page(url)
        print("No job entries found; reloading page to check: {}".format(url))
        if len(self.job_entry_queue) == 0:
            print("All job entries have been crawled for this query.")
            self.browser.quit()

    def run_crawler(self):
        try:
            page_num = 0
            self.wait_for_login()
            while len(self.url_queue):
                current_url = self.get_search_results_page()
                self.get_job_entries(current_url)
                if len(self.job_entry_queue) == 0: #if the list is empty, check if all entries have been pulled
                    self.check_for_completion(current_url)
                print('Job entry elements: {}'.format(self.job_entry_queue))

                content_packets = []
                while len(self.job_entry_queue):
                    current_url = self.load_entries()
                    print('Test {}'.format(current_url))
                    soup = self.get_soup()
                    if soup is not None and current_url not in self.crawled_urls and self.browser.find_elements_by_class_name(self.job_poster_class):
                        company_name, job_position = self.parse_content(soup)
                        print('>>Job poster found. Parsed data from page (HTML soup).')
                        content_packets.append([company_name, job_position, current_url])
                    self.crawled_urls.append(current_url)
                self.output_to_csv(content_packets)

                page_num += 1
                print('Go to page: {}'.format(page_num + 1))
                self.url_queue.append(self.start_url + self.pagination_prefix + "{}".format(str(self.pagination_increment*page_num)))
                if randint (1, 3) == 1:
                    print("Next page loading delayed to avoid excessive requests and timeouts")
                    sleep(uniform(15.0, 20.0))
        finally:
            self.browser.quit() #Clean up after minor errors and exceptions (close webdriver and Chrome processes)


#Main method including argument parser
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', '--keyword', type=str)
    parser.add_argument('-l', '--location', type=str)
    parser.add_argument('-o', '--output_file', type=str)
    args = parser.parse_args()
    crawler_process = LinkedInJobsCrawler(args.keyword, args.location, args.output_file)
    crawler_process.run_crawler()

if __name__ == "__main__":
    main()
