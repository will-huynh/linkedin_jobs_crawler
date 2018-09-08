# linkedin_jobs_crawler

The linkedin_jobs_crawler is a Python web crawler script made to investigate crawling techniques using the website [LinkedIn](https://www.linkedin.com). In this case, the crawler searches for job postings (entries) containing a job poster and filters data relating to company name, job position, and job page link.

The crawler can be modified to run in a headless browser; it does not by default to leave use of login information to the user.

## Installation:
### Required Packages/Software:
The following is required to use this script:
* [Python](https://www.python.org/) 3.6 or greater
* [Selenium](https://www.seleniumhq.org/)
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Chromedriver 2.41](http://chromedriver.chromium.org/) for browser automation
* [Google Chrome](https://www.google.com/chrome/) or [Chromium](https://www.chromium.org/)

### Installing The Script:
1. Clone the repository to your machine using git:
>git clone https://github.com/will-huynh/linkedin_jobs_crawler.git

2. Go to the cloned directory on your local machine and check for the latest version using git:
>Navigate to the cloned linkedin_jobs_crawler folder

>git branch master

>git pull

3. Download [Chromedriver 2.41](http://chromedriver.chromium.org/) and place the chromedriver executable file in the linkedin_jobs_crawler folder (the same directory as the script).

## Using the crawler:
Use of the crawler is enabled by the command line. The crawler takes a query (job position), search location, and output file name with the .csv extension. The crawler then outputs scraped results to /<script_dir>/output/<csv_file>.

First, navigate to the script directory. The crawler is then run with a terminal command using three required arguments that must be passed to the crawler, specified by the following command and tags:
>python3 linkedin_jobs_crawler.py

>-k or --keyword "<query>"

>-l or --location "<query geolocation>"
  
>-o or --output "<csv_filename>"

An example command would be:
>python3 -k "engineer" -l "Vancouver, Canada" -o "output.csv"
