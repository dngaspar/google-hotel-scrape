# Dependencies
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd  # To store data in dataframe
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import time

start = time.time()
ids = []
hotels = []
cities = []
check_in_dates = []
check_out_dates = []
re_attempt = []
# Open the CSV file with the open function
with open('final_data_reattempt_1.csv', newline='') as csvfile: # read the file that stored failed attempt
    # Read the CSV file using the csv.reader module
    reader = csv.reader(csvfile)

    # Loop through each row in the CSV file
    for row in reader:
        # Access the first column of each row
        id_hotel = row[0]
        hotel = row[1]
        city = row[4]
        check_in_date = row[2]
        check_out_date = row[3]
        ids.append(id_hotel)
        cities.append(city)
        hotels.append(hotel)
        check_in_dates.append(check_in_date)
        check_out_dates.append(check_out_date)

# # Create list of ids, hotels, check-in, check-out
ids.pop(0)
hotels.pop(0)
cities.pop(0)
check_in_dates.pop(0)
check_out_dates.pop(0)

URL = 'https://www.google.com/travel/hotels'
final_data = []

for i in range(len(ids)):  # Delete -125 if you want to scrape in one run all the row in csv
    OTA_list = []  # Online Travel Agent
    price_list = []
    # setting the webdriver for chrome
    service = Service(executable_path="C:\Development\chromedriver.exe")  # Path for Chrome web driver
    options = Options()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL)
    actions = ActionChains(driver)
    wait = WebDriverWait(driver, 10)
    sleep(1)
    hotel_name = hotels[i]
    city = cities[i]
    try:
    # enter hotel name

        sleep(2)
        x_button = driver.find_element(By.CLASS_NAME, 'SS0SXe').find_element(By.TAG_NAME, 'button')
        actions.move_to_element(x_button).click().perform()
        search_bar = driver.find_elements(By.TAG_NAME, 'input')[1]
        search_bar.send_keys(hotel_name + " " + city)
        search_bar.send_keys(Keys.ENTER)

        sleep(2)
        try: # check the price option exist or not, if not, then back to previous page and enter the hotel name without city address
            price = driver.find_element(By.XPATH, '//*[@id="prices"]/span')
            price.click()
        except:
            driver.back()
            sleep(2)
            x_button = driver.find_element(By.CLASS_NAME, 'SS0SXe').find_element(By.TAG_NAME, 'button')
            actions.move_to_element(x_button).click().perform()
            search_bar = driver.find_elements(By.TAG_NAME, 'input')[1]
            search_bar.send_keys(hotel_name)
            search_bar.send_keys(Keys.ENTER)

        sleep(1)
        price = driver.find_element(By.XPATH, '//*[@id="prices"]/span')
        price.click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Change the currency
        sleep(1)
        currency = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="prices"]/div/c-wiz[2]/footer/div[1]/c-wiz/button')))
        currency.click()
        usd = driver.find_element(By.XPATH, '//*[@id="USD"]')
        usd.click()
        done_button = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/div[6]/div/div[2]/div[3]/div[2]/button')
        sleep(1)
        done_button.click()

        # Check-in date
        driver.execute_script("window.scrollTo(0, 0);")
        sleep(2)
        check_in = driver.find_element(By.XPATH,
                                       '//*[@id="prices"]/c-wiz/c-wiz/div/div/div/div/div/div/div/section/div[1]/div[1]/div[1]/div/div[2]/div[1]')

        actions.move_to_element(check_in).click().perform()
        date_check_in = driver.find_element(By.CSS_SELECTOR, f"div[aria-label='{check_in_dates[i]}']")
        print(check_in_dates[i])
        sleep(2)
        actions.move_to_element(date_check_in).click().perform()
        date_check_out = driver.find_element(By.CSS_SELECTOR, f"div[aria-label='{check_out_dates[i]}']")
        print(check_out_dates[i] )
        sleep(2)
        actions.move_to_element(date_check_out).click().perform()
        sleep(1)
        google_icon = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/a')
        # create an ActionChains instance and move the mouse to the desired location
        actions.move_to_element(google_icon).move_by_offset(0, 100)
        # perform the click action
        actions.click().perform()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        # scraping process
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        headers = soup.find_all('div', class_='vxYgIc')[3]
        try:
            not_available = soup.find_all('div', class_='l3Rulc')[1]  # Variable to check the availability of a hotel room
        except:
            not_available = False
        online_travel_agents = headers.find_all('div', class_='ADs2Tc')
        driver.execute_script("window.scrollTo(0, 0);")
        sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        if not_available:
            # create dictionary
            id_hotel = ids[i]
            check_outs = check_out_dates[i]
            check_ins = check_in_dates[i]
            data = {
                'ID': id_hotel,
                'Hotel': hotel_name,
                'Agents': 'Not Available',
                'Check_in': check_ins,
                'Check_out': check_outs,
                'Price': 'Not Available',
            }
            final_data.append(data)
            print(f'Row {i+1}: {hotel_name} is not available.')
        else:
            # Retrieve the Online agent travels and the prices
            for online in online_travel_agents:
                try:
                    agent_name = online.find('div', class_='t7H34 TFnGUc').find('span', class_='NiGhzc').get_text().replace('\n', " ")
                    OTA_list.append(agent_name)
                except:
                    name = None
                try:
                    price = online.find('div', class_='Einivf qOlGCc').find('span', class_='MW1oTb').get_text()
                    price_list.append(price)
                except:
                    price = None

            # create dictionary
            id_hotel = ids[i]
            hotel_title = hotels[i]
            check_outs = check_out_dates[i]
            check_ins = check_in_dates[i]
            for j in range(len(OTA_list)):
                data = {
                    'ID': id_hotel,
                    'Hotel': hotel_title,
                    'Agents': OTA_list[j],
                    'Check_in': check_ins,
                    'Check_out': check_outs,
                    'Price': price_list[j],
                }
                final_data.append(data)
            print(f"Row {i+1}: {hotel_name} successfully scraped.")
    except:
        id_hotel = ids[i]
        hotel_title = hotels[i]
        check_outs = check_out_dates[i]
        check_ins = check_in_dates[i]
        city = cities[i]
        data = {
            'ID':  id_hotel,
            'Hotel': hotel_title,
            'Check_in': check_ins,
            'Check_out': check_outs,
            'City': city,
        }
        re_attempt.append(data)
        print(f"I can't scrape row {i+1}: {hotel_name} due to unable to locate element. I will re-attempt in the next scraping")
    driver.close()


#  create csv file
df = pd.DataFrame(final_data)
df.to_csv('final_data_reattempt_success_1.csv', index=False)
print("Data created successfully for failed scraping")

end = time.time()
print(f"Completed in {(end - start)/60:.2f} minutes")
if len(re_attempt) > 0:
    #  create csv file
    df = pd.DataFrame(re_attempt)
    # create final data reattempt for the next scraping in case there are failed attempt
    df.to_csv('final_data_reattempt_2.csv', index=False)  # if some hotel failed to scraped then change the name of this csv file
    print("Some hotel failed to scrape")
else:
    print("All hotel successfully scraped")

