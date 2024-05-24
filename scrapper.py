from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import csv

def init_scrapper():
    driver = webdriver.Chrome()
    driver.get('https://www.portalinmobiliario.com')
    return driver

def close_scrapper(driver):
    driver.quit()
    
def find_properties(driver, propertyType, location):
    time.sleep(5)
    search_box = driver.find_element(By.CLASS_NAME, 'andes-form-control__field')
    search_box.send_keys(location)

    time.sleep(5)
    first_option = driver.find_element(By.CSS_SELECTOR, ".andes-list.faceted-search-desktop-searchbox__list.andes-list--default.andes-list--selectable [tabindex='0']")
    first_option.click()

    time.sleep(5)

    search_button = driver.find_element(By.CLASS_NAME, 'andes-button.faceted-search-desktop__elem-actions.andes-button--large.andes-button--loud')
    search_button.click()

    time.sleep(2)

    current_url = driver.current_url
    modified_url = current_url.replace("venta", "arriendo")
    
    if propertyType != 'departamento':
        modified_url = current_url.replace("departamento", propertyType)
        
    driver.get(modified_url)
    time.sleep(5)
    
    return driver.page_source

def get_properties_info(html, zone):
    soup = BeautifulSoup(html, 'html.parser')

    with open('properties_info.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Link', 'Price', 'Currency', 'Attributes', 'Zone'])

        ol = soup.find('ol', class_='ui-search-layout ui-search-layout--grid')
        if ol:
            for listing in ol.find_all('li', class_='ui-search-layout__item'):

                title = listing.find('div', class_='ui-search-item__title-label-grid').get_text().split(" Id:")[0]
                link = listing.find('a', class_='ui-search-result__image ui-search-link').get('href')
                price_info = listing.find('span', class_='andes-money-amount ui-search-price__part ui-search-price__part--medium andes-money-amount--cents-superscript').get('aria-label')
                
                currency, price = price_info.split(' ')[0], ' '.join(price_info.split(' ')[1:])
                
                attributes_text = ', '.join([li.get_text() for li in listing.select('ul.ui-search-card-attributes.ui-search-item__group__element.ui-search-item__attributes-grid li')])
                writer.writerow([title, link, price, currency, attributes_text, zone])
        else:
            print("No se encontraron resultados para esta búsqueda.")


if __name__ == '__main__':
    driver = init_scrapper()
    html = find_properties(driver, 'departamento', "Santiago")
    get_properties_info(html, "Santiago")
    close_scrapper(driver)