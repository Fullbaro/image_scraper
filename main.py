import os
import cv2
import time
import urllib
import numpy as np
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


class Scraper:

    def __init__(self, prompt, amount):
        self.timeout = 5
        self.len = 0
        self.prompt = prompt
        self.amount = amount

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--start-maximized')

        self.driver = webdriver.Chrome('./assets/chromedriver', chrome_options=options)

    def start(self):
        print("Starting up")
        self.search()
        print("Searcing for images")
        links = self.find_images()
        self.show(links)

    def search(self):
        self.driver.get("https://images.google.com/")

        self.get_element_clikable(By.XPATH, '//*[@id="L2AGLb"]/div').click()

        element = self.get_element(By.XPATH, '//*[@id="APjFqb"]')
        self.type_slow(element, self.prompt+Keys.ENTER)

    def find_images(self):
        try:
            links=[]
            element = self.get_element(By.XPATH, '//*[@id="islrg"]/div[1]')
            elements = self.get_elements_inside(By.TAG_NAME, "img", element)
            for element in elements:
                link = element.get_attribute("src")
                w = int(element.get_attribute("width"))
                alt = element.get_attribute("alt")
                if link != None and w > 100:
                    links.append([link, alt])

            print(f"Found {len(links)} images in total")

            if len(links) >= self.amount:
                return links[:self.amount]
            else:
                self.scroll_to_bottom()
                if self.is_no_more(len(links)):
                    print("No more relevant images")
                    return links
                else:
                    return self.find_images()
        except:
            print("Still loading...")
            return self.find_images()

    def is_no_more(self, len):
        if len == self.len:
            return True
        else:
            self.len = len
            return False

    def show(self, links):
        try:
            for link, alt in links:
                url_response = urllib.request.urlopen(link)
                img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
                img = cv2.cvtColor(cv2.imdecode(img_array, -1), cv2.COLOR_BGR2RGB)

                fig, ax = plt.subplots()
                ax.imshow(img)
                plt.connect('key_press_event', self.save)
                plt.show()

        except Exception as ex:
            print(f"Unable to open image: {ex}")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Loading more images...")

    def save(self, event):
        k = event.key
        if k != 'escape':
            os.makedirs(f"./assets/images/{k}", exist_ok=True)
            plt.savefig(f'./assets/images/{k}/{round(time.time() * 1000)}.png')
        plt.close()

    def get_elements_inside(self, by, value, element):
        element = WebDriverWait(element, self.timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        time.sleep(0.1)
        return element

    def get_elements(self, by, value):
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
        time.sleep(0.1)
        return element

    def get_element(self, by, value):
        try:
            element = WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((by, value))
            )
            time.sleep(0.1)
        except TimeoutException as ex:
            print(f"The element can not be found: {value}")
            return None
        return element

    def get_element_clikable(self, by, value):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((by, value))
            )
            time.sleep(0.1)
        except TimeoutException as ex:
            print(f"The element can not be found: {value}")
            return None
        return element

    def type_slow(self, element, value, delay=0.3):
        value = str(value)
        for character in value:
            element.send_keys(character)
            time.sleep(delay)



Scraper("pokemon charaters", 10).start()