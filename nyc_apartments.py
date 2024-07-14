# NYC Apartment Listings Data Scraper
# Developed by: Alex Bow
# Contact: alexbow315@gmail.com
# Date: July 2024

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

PATH = '/Users/alexbow/Documents/chromedriver'

chrome_options = Options()
#chrome_options.add_argument("--headless")  

service = Service(PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get('https://www.apartments.com/new-york-ny/')

building_names = []
addresses = []
apt_types = []
prices = []
descriptions = []
available_units = []

try:
    def get_buildings():
        #store all potential apartment buildings
        all_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'mortar-wrapper'))
        )

        buildings_list = []
        #filter elements to find actual apartment buildings
        for element in all_elements:
            try:
                title = element.find_element(By.CLASS_NAME, 'property-title')
                address = element.find_element(By.CLASS_NAME, 'property-address')
                buildings_list.append(element)
            except Exception as e:
                continue
        return buildings_list
    
    buildings = get_buildings()
    print(f"Filtered to {len(buildings)} apartment buildings")

    #loop through buildings
    for index in range(len(buildings)):
        try:
            #refetch
            buildings = get_buildings()
            if index >= len(buildings):
                print(f"Index {index} is out of range for buildings list")
                continue

            building = buildings[index]
            print(f"Processing building {index + 1}/{len(buildings)}")

            building.find_element(By.CLASS_NAME, 'property-title').click()

            #wait for the new page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'pricingGridItem'))
            )

            #giving more time for elements to load
            time.sleep(7)

            try:
                #find all floors
                floors = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'pricingGridItem') and contains(@class, 'multiFamily') and contains(@class, 'hasUnitGrid')]"))
                )
                #loop through each floor and scrape the required data
                for floor in floors:
                    try:
                        title = driver.find_element(By.ID, 'propertyNameRow').text
                        address = driver.find_element(By.ID, 'propertyAddressRow').text
                        apt_type = floor.find_element(By.CLASS_NAME, 'modelName').text
                        price_range = floor.find_element(By.CLASS_NAME, 'rentLabel').text
                        description = floor.find_element(By.CLASS_NAME, 'detailsTextWrapper').text
                        units = floor.find_elements(By.CLASS_NAME, 'unitContainer')
                        num_units = len(units)

                        if apt_type and price_range and description:
                            print(f"Building: {title}")
                            print(f"Address: {address}")
                            print(f"Apartment Type: {apt_type}")
                            print(f"Price Range: {price_range}")
                            print(f"Description: {description}")
                            print(f"Available Units: {num_units}\n")
                            building_names.append(title)
                            addresses.append(address)
                            apt_types.append(apt_type)
                            prices.append(price_range)
                            descriptions.append(description)
                            available_units.append(num_units)
                    except Exception as e:
                        print(f"Error scraping floor data: {e}")
                
            except Exception as e:
                print(f"Error fetching floors: {e}")

            #navigate back to main page
            driver.back()

            #wait for the main page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'mortar-wrapper'))
            )
            
        except Exception as e:
            print(f"Error processing building: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

#add data to data frame
data = {
    'Building Name': building_names,
    'Address': addresses,
    'Apartment Type': apt_types,
    'Price Range': prices,
    'Description': descriptions,
    'Available Units': available_units
}

df = pd.DataFrame(data)

#export DataFrame to Excel
output_file = '/Users/alexbow/Documents/apartments_data.xlsx'
df.to_excel(output_file, index=False)
print(f"Data saved to {output_file}")

