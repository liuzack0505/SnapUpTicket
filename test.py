from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unicodedata
import time
import re
import undetected_chromedriver as uc

gmails = ["0982306031", "0928958175", "kevin731", "liu.zack0505@gmail.com"]
passwords = ["0982306031", "0928958175", "jeep666k", "83298329zack"]

# handle user
print("輸入0是外婆的帳號, 1是阿母的帳號, 2是阿爸的帳號")
user = int(input("請輸入使用者："))

GMAIL = gmails[user]
PASSWORD = passwords[user]

url = input("請貼上網址：")

seat1 = None
seat2 = None

while True:
    try:
        seat1 = int(input("請輸入第一個位置號碼:"))
        if seat1 > 0:
            break
        else:
            print("請重新輸入")
    except:
        print("請重新輸入")

while True:
    try:
        user_input = input("請輸入第二個位置號碼(按enter可以跳過):")
        if user_input == "":
            break
        if int(user_input) > 0:
            seat2 = int(user_input)
            break
        else:
            print("請重新輸入")
    except:
        print("error")

driver = uc.Chrome()
driver.get(url)
# sign in
try:
    isSignIn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
        (By.XPATH, '/html/body/div[3]/div[4]/div/div/div[1]/div/div[2]/div/div[3]/a[2]')))
    isSignIn.click()
    time.sleep(5)
    email = driver.find_element(By.ID, 'user_login')
    email.clear()
    email.send_keys(GMAIL)
    password = driver.find_element(By.ID, 'user_password')
    password.clear()
    password.send_keys(PASSWORD)
    password.send_keys(Keys.RETURN)
    time.sleep(5)
except:
    print("無登入按鈕")

current_time = time.localtime()
target_time = time.mktime(time.strptime(
    f'{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday} 20:00:00', '%Y-%m-%d %H:%M:%S'))
wait_time = target_time - time.mktime(current_time)

if wait_time < 0:
    wait_time += 86400

print(f"{wait_time} 秒後，開始搶票")
# time.sleep(wait_time)

try:
    # find plus button
    driver.refresh()
    buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'button.btn-default.plus')))
    length = len(buttons)
    if seat1 is not None:
        if seat1 <= length:
            buttons[seat1 - 1].click()
        else:
            buttons[0].click()
    time.sleep(0.5)
    if seat2 is not None:
        if seat2 <= length:
            buttons[seat2 - 1].click()
        else:
            buttons[1].click()
    time.sleep(0.5)
    # check box
    checkbox = driver.find_element(By.ID, 'person_agree_terms')
    if not checkbox.is_selected():
        checkbox.click()
    time.sleep(0.5)
    # next step
    next_step = driver.find_element(
        By.XPATH, '//*[@id="registrationsNewApp"]/div/div[5]/div[4]/button')
    next_step.click()
    # enter the check page(can comment this part when debugging)
    time.sleep(0.5)
    end = WebDriverWait(driver, 600).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="registrations_controller"]/div[4]/div[2]/div/div[4]/a')))
    end.click()
    print("搶票成功")
except KeyError as e:
    print("位置少於兩個")
except Exception as e:
    print("搶票錯誤，請看以下錯誤訊息：")
    print(e)
time.sleep(600)
driver.quit()
