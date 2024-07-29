import time
from urllib.request import urlopen #It is used for openning urls. For module installation please install urllib3 module.
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Define Chrome options and initialize the driver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # ı want to hide all interaction process
    driver = webdriver.Chrome( options=options)
    return driver


# Function to scrape the main URL for href elements
def start_scratching(main_url):
    driver = init_driver()
    driver.get(main_url)
    time.sleep(2)
    section_elements = driver.find_element(By.XPATH, '//ul[contains(@class, "nav") and contains(@class, "nav-list")]')
    a_elements = section_elements.find_elements(By.TAG_NAME, "a")
    href_elem = [elem.get_attribute("href") for elem in a_elements]
    driver.quit()
    return href_elem[1:]  # Exclude the first element if not needed because it is land page.


# Function to get all relevant hrefs based on genre and page number
def href_list(genre_name, href_elem, page_num=1):
    driver = init_driver()
    hrefs = []
    for elem in href_elem:
        if genre_name.lower() in elem.lower():
            if page_num == 1:
                driver.get(elem)
                time.sleep(2)
                ol_elements = driver.find_elements(By.XPATH, "//ol/li//a")
                hrefs.extend([elem.get_attribute("href") for elem in ol_elements])
            else:
                for i in range(1, page_num + 1): #Pagination process
                    pg = f"{elem[:-10]}page-{i}.html" #I needed to delete last 10 characters to add page numbers
                    driver.get(pg)
                    time.sleep(2)
                    ol_elements = driver.find_elements(By.XPATH, "//ol/li//a")
                    hrefs.extend([elem.get_attribute("href") for elem in ol_elements])
    driver.quit()
    return hrefs


# Function to create a DataFrame from the book links
def book_dataframe(hrefs):
    Name_list = []
    Desc_list = []
    Price_exc_list = []
    Price_wth_list = []
    Tax_list = []
    Nbr_list = []

    driver = init_driver()
    for link in hrefs:
        driver.get(link)
        time.sleep(4)
        Soup = BeautifulSoup(urlopen(link), "html.parser")

        Name = Soup.find("h1").text
        Description = Soup.find_all("p")[3].text
        table = Soup.find("table")
        Price_exc_tax = table.find_all("td")[2].text
        Price_wth_tax = table.find_all("td")[3].text
        Tax = table.find_all("td")[4].text
        Nmbr_views = table.find_all("td")[6].text

        Name_list.append(Name)
        Desc_list.append(Description)
        Price_exc_list.append(Price_exc_tax)
        Price_wth_list.append(Price_wth_tax)
        Tax_list.append(Tax)
        Nbr_list.append(Nmbr_views)

    driver.quit()

    Dicty = {"Book_Name": Name_list, "Price with tax": Price_wth_list, "Price excluded tax": Price_exc_list,
             "Tax": Tax_list, "Number of views": Nbr_list, "Description": Desc_list}
    return pd.DataFrame(data=Dicty)


# Main function to run the scraping process
def book_scraping(main_url, genre_name, page_num=1):
    href_elem = start_scratching(main_url)
    hrefs = href_list(genre_name, href_elem, page_num)
    df = book_dataframe(hrefs)
    return df


# Usage example
main_url = "https://books.toscrape.com/"
genre_name = "Nonfiction"
page_num = 6
df = book_scraping(main_url, genre_name, page_num)
