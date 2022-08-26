import os, logging

from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class LeadBot():
    TIMEOUT = 60
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        # Setup webhook trigger types and drapdown values
        self.trigger_type_mapper = {
            "Lead Created": 1,
            "Lead Edited": 2,
            "Lead Status Changed": 3,
            "Contact Added": 6,
            "Contact Edited":7, # TODO: Merto you should handle this in DATA-API as well.,
            "Opportunity Created": 10
        }

        # Setup logger
        level    = logging.INFO
        format   = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        handlers = [logging.FileHandler('app.log'), logging.StreamHandler()]
        logging.basicConfig(handlers=handlers, level=level, format=format)
        self.logger = logging.getLogger(self.__class__.__name__)

       
        # Chrome options
        chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_setting_values.automatic_downloads': 1}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('window-size=1920x1080') 
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')        
        chrome_options.add_argument('log-level=3') # hate the connection logs

        # Create chrome driver by using ChromeDriverManager as cached engine
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)

    def __del__(self):
        self.logger.info("(!) Destructor --> Graceful shutdown")
        self.driver.quit()

    def __login(self):
        self.driver.get(os.environ["base_page_url"])
       
        # Enter username
        self.__enter_keys(xpath = "//*[@id='UserName']", keys_to_be_sent=os.environ["lead_user_name"])
        
        #Enter pass
        self.__enter_keys(xpath = "//*[@id='Password']", keys_to_be_sent=os.environ["lead_password"])
        
        # Click login
        self.__click_button(by='XPATH', locator="/html/body/div[1]/div/form/div[4]/input")


    def __create_webhook_connection(self, trigger_type_name: str, dropdown_value: int):
        """
            Simply creates webhook conection for each desired trigger type
        """
        # Create wh connection button
        self.__click_button(by='XPATH', locator="//*[@id='page-wrapper']/div[3]/div/div/div/div[1]/div/a")
        
        # Create and send webhook conection title
        title = "{}_{}_{}".format(
                                os.environ["org_identifier"],
                                trigger_type_name, 
                                datetime.now().strftime('%Y-%d-%m_%H:%M:%S'))
        self.__enter_keys(xpath="//*[@id='Title']", keys_to_be_sent = title)

        # Enter webhook url
        self.__enter_keys(xpath = "//*[@id='Url']", keys_to_be_sent = self.webhook_url)

        # Select dropdown item
        trigger_elem = Select(self.driver.find_element_by_xpath("//*[@id='EventType']"))
        trigger_elem.select_by_value(str(dropdown_value))

        # Save webhook conection.
        self.__click_button(by="XPATH", locator="//*[@id='page-wrapper']/div[3]/form/div[2]/div[2]/div/input")

# - - - - HELPERS - - - - - - - - - - - - - - - - 

    def __click_button(self, by: str, locator: str):
        timeout = 60

        if by == "XPATH":
            button = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))
        elif by == "CLASS":
            #TODO: It could be useful for exception handling scenario.
            pass
        else:
            raise Exception
        self.driver.execute_script('arguments[0].click()', button)
        
    
    def __enter_keys(self, xpath: str, keys_to_be_sent: str):
        place_holder = WebDriverWait(self.driver, LeadBot.TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        place_holder.send_keys(keys_to_be_sent)


# - - - - MAIN HANDLER - - - - - - - - - - - - - - - - 
    def update_webhook(self):
        self.__login()
        self.logger.info("(+) Successfully logged in")
        
        for trigger_type_name, dropdown_value in self.trigger_type_mapper.items():
            self.__create_webhook_connection(trigger_type_name, dropdown_value)
            self.logger.info(f"(+) {trigger_type_name} is added")

from dotenv import load_dotenv
load_dotenv()

def main():
    lb = LeadBot(webhook_url='http://3.74.173.122:8000/lead_webhook_handler?clientId=aliawadlaw')
    lb.update_webhook()

if __name__ == '__main__':
    main()