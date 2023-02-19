from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import analyzer


class Lighthouse():
    '''Interaction with Lighthouse Shopfloor Online web interface'''

    def __init__(self) -> None:
            # Initalise Web Driver
        self.driver = webdriver.Chrome(executable_path="./WebDriver/bin/chromedriver.exe")


    def scroll_to_top(self):
        self.driver.find_element(by=By.TAG_NAME, value='body').send_keys(Keys.CONTROL + Keys.HOME)

    def wait_til_present(self, xpath):
        is_present = False
        while not is_present:
            if len(self.driver.find_elements(by=By.XPATH, value=xpath)) > 0:
                is_present = True
                return is_present
    
    def wait_til_enabled(self, xpath):
        attempt_counter = 0
        while attempt_counter < 100:
            if not self.driver.find_element(by=By.XPATH, value=xpath).get_attribute("disabled") == "true":
                return True
            else:
                attempt_counter += 1
    
    def login(self, url, username, password):
        '''Log into lighthouse with user credentials'''
           # Navigate to the URL
        self.driver.get(url)

        self.driver.implicitly_wait(2)

            # Get all the elements required to login
        login_username = self.driver.find_element(by=By.CSS_SELECTOR, value=".input-username")
        login_password = self.driver.find_element(by=By.CSS_SELECTOR, value=".input-password")
        login_button = self.driver.find_element(by=By.CSS_SELECTOR, value=".button-login")

            # Type in the USERNAME and PASSWORD, then login
        login_username.send_keys(username)
        login_password.send_keys(password)
        login_button.click()
    

    def get_lpm_product_codes(self):
        '''Get LPM Product Specification Codes'''

        self.driver.implicitly_wait(4)

            # Highlight the LPM Quality Controls row
        lpm_quality_controls_row = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[7]")
        lpm_quality_controls_row.click()

            # Open the Specifications section for LPM Quality Controls
        specifications_button = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div/button[7]")
        specifications_button.click()

            # Wait for show all button to be enabled and click it.
        show_all_xpath = "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[2]/div/div[1]/div/div/div[1]/div[3]/div/button"
        if self.wait_til_present(show_all_xpath) and self.wait_til_enabled(show_all_xpath):
            show_all_specifications = self.driver.find_element(by=By.XPATH, value=show_all_xpath)
            self.driver.implicitly_wait(5)
            show_all_specifications.click()
        else:
            raise ValueError

        self.driver.implicitly_wait(4)

            # Wait until the new element has appeared
        WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[2]/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[112]")))
        print("Gathering Product Codes...")

        scrolling = 0
        product_codes = []

            # Find all grid cell elements on the page
        product_specification = self.driver.find_elements(by=By.CSS_SELECTOR, value=".grid-cell")

            # For grid cells, check if they are a product code
        for value in product_specification:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", product_specification[scrolling])
            tag = value.get_attribute("data-column")
            if tag == "product":
                value.click()
                analyze = analyzer.Analyze()
                print(value.text)
                decoded_product = analyze.decode_lpm_product_codes(value.text)
                if decoded_product == None:
                    continue
                else:
                    specs = analyze.get_lpm_specification_values(decoded_product)
                    self.enter_lpm_values(specs)
            scrolling += 1
        print("Gathered All Product Codes!")
        return product_codes


    def enter_lpm_values(self, product):
        # self.scroll_to_top()
        specification_limits_button = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[2]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div/button[6]")
        specification_limits_button.click()

            # Wait for Specifications table heading to appear
        WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[2]/div/div/div/div/div[1]")))
        self.driver.implicitly_wait(4)

            # Enter the board thickness values
        self.enter_board_thickness(product['board_thickness']['lsl'], product['board_thickness']['norm'], product['board_thickness']['usl'])


            

    def click_edit(self):
        '''Opens the edit box and waits until it has finished loading'''
        WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div/button[2]")))
        edit_button = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div/button[2]")
        edit_button.click()
        WebDriverWait(self.driver, 25).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]")))
        self.driver.implicitly_wait(4)


    def enter_edit_box(self, units, usl, norm, lsl, dec):
        '''Fills in the Edit Box with the input values and presses ok'''
        units_input = self.driver.find_element(by=By.ID, value="Units")
        usl_input = self.driver.find_element(by=By.ID, value="USL")
        norm_input = self.driver.find_element(by=By.ID, value="NOM")
        lsl_input = self.driver.find_element(by=By.ID, value="LSL")
        dec_input = self.driver.find_element(by=By.ID, value="DecPlaces")
        comments = self.driver.find_element(by=By.ID, value="Comments")

        units_input.clear()
        units_input.send_keys(str(units))
        self.driver.implicitly_wait(2)

        usl_input.clear()
        usl_input.send_keys(str(usl))
        self.driver.implicitly_wait(2)
        
        norm_input.clear()
        norm_input.send_keys(str(norm))
        self.driver.implicitly_wait(2)

        lsl_input.clear()
        lsl_input.send_keys(str(lsl))
        self.driver.implicitly_wait(2)

        dec_input.clear()
        dec_input.send_keys(str(dec))

        self.driver.implicitly_wait(2)
        comments.send_keys("N/A")

        self.driver.implicitly_wait(4)

        ok_button = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/div/div[2]/div[2]/form/div[3]/div/span[1]/button")
        ok_button.click()

        self.driver.implicitly_wait(20)


    def enter_board_thickness(self, thickness_lsl, thickness_norm, thickness_usl):
        '''Enters the board thickness for left, center, and right'''
        thickness_units = "mm"
        thickness_dec = "1"
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

        thickness_left_row = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[2]/td[3]")
        thickness_left_row.click()
        self.click_edit()
        self.enter_edit_box(thickness_units, thickness_usl, thickness_norm, thickness_lsl, thickness_dec)

        WebDriverWait(self.driver, 25, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[3]/td[3]")))
        self.driver.implicitly_wait(5)
        thickness_middle_row = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[3]/td[3]")
        thickness_middle_row.click()
        self.click_edit()
        self.enter_edit_box(thickness_units, thickness_usl, thickness_norm, thickness_lsl, thickness_dec)

        WebDriverWait(self.driver, 25, ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[3]/td[3]")))
        self.driver.implicitly_wait(5)
        thickness_right_row = self.driver.find_element(by=By.XPATH, value="/html/body/div[2]/div[2]/div/div[2]/div/div/div/div/section[3]/div/div[2]/div/div/div/div/div[2]/table/tbody/tr[4]/td[3]")
        thickness_right_row.click()
        self.click_edit()
        self.enter_edit_box(thickness_units, thickness_usl, thickness_norm, thickness_lsl, thickness_dec)