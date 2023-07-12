from selenium import webdriver
#chrome options class is used to manipulate various properties of Chrome driver
from selenium.webdriver.chrome.options import Options
#waits till the content loads
from selenium.webdriver.support.ui import WebDriverWait
#finds that content
from selenium.webdriver.support import expected_conditions as EC
#find the above condition/conntent by the xpath, id etc.
from selenium.webdriver.common.by import By

import asyncio, inspect

from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By

from datetime import datetime

import sched, time, pyotp, json

from jsonformatter import JsonFormatter

from collections import deque

#zerodha
from kiteconnect import KiteConnect
from time import sleep
import urllib.parse as urlparse

# importing inproject files
import credentials
import random
import heapq


# credentials
api_key = credentials.api_key
api_secret = credentials.api_secret
account_username = credentials.account_username
account_password = credentials.account_password
zerodha_totp_key = credentials.zerodha_totp_key
access_token_expiry_hour = credentials.access_token_expiry_hour

class KiteAPI:

    def __init__(self, api_key,api_secret, account_username, account_password,zerodha_totp_key,access_token):
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_username = account_username
        self.account_password = account_password
        self.zerodha_totp_key = zerodha_totp_key
        self.kite = KiteConnect(api_key=self.api_key)
        self.access_token_expiry_hour = access_token_expiry_hour
        self.previous_price = []
        self.trigger_data = {}
        self.new_stop_loss = 0
        self.stop_loss_dict = {}

    def login(self):
        print("login flow started --->")
        count = 0
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

            driver.get(self.kite.login_url())

            # identify login section
            form = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]')))

            # enter the ID
            driver.find_element("xpath", "//input[@type='text']").send_keys(account_username)

            # enter the password
            driver.find_element("xpath", "//input[@type='password']").send_keys(account_password)

            # submit
            # driver.find_element("xpath" ,"//input[@type='submit']").click()
            driver.find_element(By.CSS_SELECTOR, "#container > div > div > div > form > div.actions > button").click()

            # sleep for a second so that the page can submit and proceed to upcoming question (2fa)
            sleep(1)
            form = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[@class="login-form"]//form')))

            authkey = pyotp.TOTP(self.zerodha_totp_key)
            # identify login section for 2fa
            # enter the 2fa code
            print("authkey : -----> ", authkey.now())
            driver.find_element(By.CSS_SELECTOR,"#container > div.content > div > div > form > div.su-input-group.su-static-label.su-has-icon.twofa-value.digits > input[type=text]").send_keys(authkey.now())

            # submit
            driver.find_element(By.CSS_SELECTOR,"#container > div.content > div > div.login-form > form > div.actions > button").click()

            time.sleep(2)
            current_url = driver.current_url

            print("final url containing request token : - - >",current_url)

            driver.close()

            parsed = urlparse.urlparse(current_url)

            request_token = urlparse.parse_qs(parsed.query)['request_token'][0]

            self.access_token = self.kite.generate_session(request_token=request_token, api_secret=api_secret)['access_token']

            self.kite.set_access_token(self.access_token)

            print(f"ACCESS TOKEN {datetime.now()} ---> ",self.access_token)
            print("YOU ARE READY USE THIS API FUNCTIONS")
            return self.access_token
        except Exception as e:
            count +=1
            print(f"Retrying login funcation for : {count}")
            if count == 3:
                print("Tries exceeded check with kite api")
                raise Exception("Tries exceeded check with kite api")
                return
            else:
                self.login()

    #when exception occurs for token expiry,This function will be called
    def token_refersh(self,e,name_func):
        if "Invalid `api_key` or `access_token`" in str(e):
            print("Key is exprired, recalling login function")
            self.login()
            # Get the name of the last executed function
            print("Last function executed:", name_func)
            print(f"now, recalling {name_func} funcation")
            self.name_func
        else:
            raise Exception(
                "exception occurred contact developer @shivanand-masne\n Probaly some changes on kite server"
                , print(str(e)))


    def is_token_expired(self):
        # Get the current datetime
        now = datetime.datetime.now()

        # Add 12 hours to the current time to set the token expiry
        token_expiry = now + datetime.timedelta(hours=self.access_token_expiry_hour)

        # Print the token expiry time for debugging purposes
        print(f"Token expiry time: {token_expiry} The token will exprire in {token_expiry-now}")

        # Return True if the token has expired, else False
        return now >= token_expiry

#*****************************************************************
#           App core algorithms starts from here                 #
#*****************************************************************

    # This Function will Return Dictionary mapped with id : { "stop_loss","last_price"}

    def get_order_details_from_jason(self, curr):
        print("STARTED ! --> get_order_details_from_jason Executed \n")
        try:
            jason_data = self.kite.get_gtts()
            json_string = json.dumps(jason_data)
            json_string = json.loads(json_string)

            print(f"all gtt dumb -----------> {jason_data}\n")
            # Create a dictionary to store the extracted data, mapped by relation ID
            trigger_data = {}

            # Loop through each trigger object
            for trigger in range(len(json_string)):
                # Extract the relevant data
                status = json_string[trigger]['status']
                id = json_string[trigger]['id']

                if status != "triggered":
                    id = json_string[trigger]['id']
                    stop_loss = min(json_string[trigger]['condition']['trigger_values'])
                    exchange = json_string[trigger]['condition']['exchange']
                    tradingsymbol = json_string[trigger]['condition']['tradingsymbol']
                    type = json_string[trigger]['type']
                    trigger_values = json_string[trigger]['condition']['trigger_values']
                    last_price = json_string[trigger]['condition']['last_price']
                    orders = json_string[trigger]['orders']

                    # assiging actual stop loss to new stoploss
                    self.new_stop_loss  = stop_loss

                    # getting current price for stock with id and stock
                    current_price = self.kite.ltp(f'{exchange}:{tradingsymbol}')
                    current_price = current_price[f'{exchange}:{tradingsymbol}']['last_price']
                    print(f"current price for {id} --> {current_price} \n")

                    #checking and clearing unwanted data from the list
                    if len(self.previous_price) >= 2:
                        del(self.previous_price[:-2])

                    # Assign the current value to the previous value if it exists
                    self.previous_price.append(current_price)
                    print(f"previous price list --> {self.previous_price}\n")

                    #print(f"pervious stop_loss for {id} : {self.new_stop_loss}\n")
                    print("Triggering get gtt algorithm \n")


                    if current_price > self.previous_price[-2]:
                        print("price increased so calculating new stop loss by margin of 5% \n")

                        # muliple by 0.05 for 5% margin or make it dynamic by replacing with variable
                        self.new_stop_loss = (current_price - current_price * 0.05)

                        #checking if id is present in dict, if true then update the stop_loss with maximum so far
                        if id in self.stop_loss_dict:
                            if self.new_stop_loss > self.stop_loss_dict[id]:
                                self.stop_loss_dict[id] = self.new_stop_loss
                        else:
                            self.stop_loss_dict[id] = self.new_stop_loss

                        print("stop_loss and mAximum ID DICT : - ", self.stop_loss_dict)

                        print(f"updated stop_loss for {id} : {self.stop_loss_dict[id]}\n")

                        print(f" trigger values  ---> {trigger_values}\n")

                        min_index = trigger_values.index(min(trigger_values))

                        #updating trigger values, with max stop loss of id
                        trigger_values[min_index] = self.stop_loss_dict[id]

                        print(f" trigger values after update ---> {trigger_values}\n")

                        print(f"modifying the gtt with updated stop_loss value for {id} \n")

                        self.kite.modify_gtt(id,type,tradingsymbol,exchange,trigger_values,last_price,orders)

                        print(f"gtt modified for {id}\n")

                    else:
                        print("there no profit, so not changing stop_loss value \n")
                        #print(f"updated stop_loss for {id} : {pervious_max_stop_loss}\n")
                        #min_index = trigger_values.index(min(trigger_values))
                        #trigger_values[min_index] = self.new_stop_loss

                else:
                    # if you want to delete triggered gtts
                    print(f"This id was already triggered, nothing can be done : {id}, so deleting this {id}\n")
                    #self.delete_gtt(id)
                    # delete_gtt(relation_id)
            return None
        except Exception as e:
            print(str(e))



if __name__ == "__main__":
    app=KiteAPI(api_key,api_secret,account_username,account_password,zerodha_totp_key,access_token_expiry_hour)

    # timer for 12hrs
    app.login()

    #app.get_gtts()
    while True:
        app.get_order_details_from_jason(random.randint(100, 200))

        sleep(3)







