from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = input("請貼上網址：")

driver = webdriver.Chrome()
driver.get(url)
##sign in
try:
    isSignIn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[4]/div/div/div[1]/div/div[2]/div/div[3]/a[2]')))
    isSignIn.click()
    email = driver.find_element(By.ID, 'user_login')
    email.clear()
    email.send_keys('0982306031')
    password = driver.find_element(By.ID, 'user_password')
    password.clear()
    password.send_keys('0982306031')
    driver.find_element(By.XPATH, '//*[@id="new_user"]/input[3]').click()
    dictCookies = driver.get_cookies()
except:
    print("無登入按鈕")
#click the button
current_time = time.localtime()
target_time = time.mktime(time.strptime(f'{current_time.tm_year}-{current_time.tm_mon}-{current_time.tm_mday} 20:00:00', '%Y-%m-%d %H:%M:%S'))
wait_time = target_time - time.mktime(current_time)

if wait_time > 0:
    print(f"{wait_time} 秒後，開始搶票")
    time.sleep(wait_time)
try:
    driver.refresh()
    buttons = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button.btn-default.plus')))
    length = len(buttons)
    if length >= 6:
        buttons[4].click()
        buttons[5].click()
    elif length >= 2:
        buttons[0].click()
        buttons[1].click()
    else:
        raise KeyError()
    checkbox = driver.find_element(By.ID, 'person_agree_terms')
    if not checkbox.is_selected():
        checkbox.click()
    next_step = driver.find_element(By.XPATH, '//*[@id="registrationsNewApp"]/div/div[5]/div[4]/button')
    next_step.click()
    end = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '//*[@id="registrations_controller"]/div[4]/div[2]/div/div[4]/a')))
    end.click()
    print("搶票成功")
    time.sleep(50)
except KeyError as e:
    print("位置少於兩個")
except :
    print("沒有票了")
driver.quit()