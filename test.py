import json
from locale import currency
import os
from time import sleep
from bs4 import BeautifulSoup
import certifi
import requests
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def get_cookies():
    # Set up undetected Chrome driver
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = uc.Chrome(options=options)
    driver.get(
        "https://kktix.com/users/sign_in?back_to=https%3A%2F%2Fkktix.com%2F")

    # Wait for the page to load
    sleep(5)

    # Fill in the login form
    email_input = driver.find_element(By.ID, "user_login")
    password_input = driver.find_element(By.ID, "user_password")
    email_input.send_keys("liu.zack0505@gmail.com")
    password_input.send_keys("83298329zack")
    password_input.send_keys(Keys.RETURN)

    # Give some time for the login to complete
    sleep(10)

    # Get cookies after login
    cookies = driver.get_cookies()

    # Save cookies to a file
    with open("cookie.json", "w") as cookie_file:
        json.dump(cookies, cookie_file)

    driver.quit()

    return cookies


def get_csrf_token(text):
    soup = BeautifulSoup(text, "html.parser")
    csrf_token = soup.find("meta", attrs={"name": "csrf-token"})
    if csrf_token:
        return csrf_token["content"]


if __name__ == "__main__":
    event_id = "67c142aa-copy-1"
    if not os.path.exists("cookie.json"):
        cookies = get_cookies()
    else:
        with open("cookie.json", "r") as cookie_file:
            cookies = json.load(cookie_file)

    # initialize the session
    info_session = requests.Session()
    for cookie in cookies:
        info_session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', None),
                                 path=cookie.get('path', '/'), expires=cookie.get('expiry', None))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Referer": "https://kktix.com/events/{event_id}/registrations/new",
    }
    info_session.headers.update(headers)

    # URL for event_page
    page_url = f"https://kktix.com/events/{event_id}/registrations/new"
    response = info_session.get(page_url, verify=False)

    # Check the response
    if response.status_code != 200:
        print("Failed to load the order page. Status code:", response.status_code)
        exit(1)

    info_session.cookies.update(response.cookies)
    csrf_token = info_session.cookies.get("XSRF-TOKEN")
    if not csrf_token:
        print("Failed to extract CSRF token at order page.")
        exit(1)
    info_session.headers.update({
        "X-Csrf-Token": csrf_token,
        "X-Requested-With": "XMLHttpRequest",
    })

    event_info_url = f"https://kktix.com/g/events/{event_id}/base_info"
    event_info_response = info_session.get(
        event_info_url, headers=headers, verify=False)
    if event_info_response.status_code != 200:
        print("Failed to load the event info. Status code:",
              event_info_response.status_code)
        exit(1)
    event_info = event_info_response.json()

    info_session.cookies.update(event_info_response.cookies)

    # get the register info
    register_info_url = f"https://kktix.com/g/events/{event_id}/register_info"
    register_info_response = info_session.get(
        register_info_url, headers=headers, verify=False)
    if register_info_response.status_code != 200:
        print("Failed to load the register info. Status code:",
              register_info_response.status_code)
        exit(1)

    # update session cookies
    info_session.cookies.update(register_info_response.cookies)
    csrf_token = register_info_response.cookies.get("XSRF-TOKEN")

    order_session = requests.Session()
    filtered_cookies = [
        cookie for cookie in info_session.cookies if cookie.domain == ".kktix.com"
    ]

    for cookie in filtered_cookies:
        order_session.cookies.set(cookie.name, cookie.value,
                                  domain=cookie.domain, path=cookie.path,
                                  expires=cookie.expires)
    order_session.cookies.update(
        {"_gali": "person_agree_terms", "locale": "zh-TW"})

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "Referer": "https://kktix.com/",
        "Origin": "https://kktix.com",
        "Content-Type": "application/json",
        "sec-ch-ua": '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "priority": "u=1, i",
    }

    # orfer the ticket
    order_url = f"https://kktix/queue/{event_id}?authenticity_token={csrf_token}"
    order_data = {
        "currency": "TWD",
        "recaptcha": {},
        "agreeterm": "true",
        "ticket": []
    }
    ticket_names = ["座位1", "座位2"]
    ticket_types = event_info["eventData"]["tickets"]
    for name in ticket_names:
        ticket_type = next(
            (ticket for ticket in ticket_types if ticket["name"] == name), None)
        if ticket_type:
            order_data["ticket"].append({
                "id": ticket_type["id"],
                "quantity": 1,
                "invitationCodes": [],
                "member_code": "",
                "use_qualification_id": None
            })
    order_ticket_response = order_session.post(
        order_url, headers=headers, json=order_data, verify=False)
    print(order_ticket_response.text)
    if order_ticket_response.status_code != 200:
        print("Failed to order the ticket. Status code:",
              order_ticket_response.status_code)
        exit(1)
    order_ticket_response_json = order_ticket_response.json()

    # get param
    param_url = f"https://queue.kktix.com/queue/token/{order_ticket_response_json["token"]}"
    param_response = order_session.get(
        param_url, headers=headers, verify=False)
    if param_response.status_code != 200:
        print("Failed to get the param. Status code:",
              param_response.status_code)
        exit(1)

    param_response_json = param_response.json()
    print(
        f"https://kktix.com/events/{event_id}/registrations/{param_response_json["to_param"]}#/")
