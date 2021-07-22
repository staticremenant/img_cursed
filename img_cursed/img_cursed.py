# system libraries
import time
import random
import os
from auth_data import vk_login, vk_password

# selenium and bs4 libraries
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from PIL import Image
from string import digits, ascii_lowercase
import itertools
from fake_useragent import UserAgent

# recaptcha libraries
import speech_recognition as sr
import requests
import pydub


def delay():
    time.sleep(random.randint(2, 3))


def delay_strong():
    time.sleep(random.randint(5, 10))


# set options for browser and requests headers
ua = UserAgent()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
    (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 OPR/73.0.3856.427"
options = webdriver.FirefoxOptions()
options.set_preference("general.useragent.override", user_agent)
options.set_preference("dom.webdriver.enabled", False)
options.set_preference("media.volume_scale", "0.0")
# options.add_argument("--headless")
headers = {
    "user-agent": ua.random
}

driver = webdriver.Firefox(
    executable_path=os.path.normpath(os.getcwd() + r"\geckodriver.exe"),
    options=options
)

print("[INFO] Starting...")

print("[INFO-PICTURES] Downloading pictures...")

# preparing to downloading pictures
symbols = digits + ascii_lowercase  # alphabet for url creation
str_length = 5  # you can change that parameter but you need to check url in line 80 then
count = 0  # count of pictures download
removed = ["imgur", r"//st.", "imageshack"]  # broken images

# getting last url symbols from file
with open(os.path.normpath(os.getcwd() + r"\data_url\last_url.txt"), "r", encoding="utf-8") as file:
    f_last_symbols = file.read()
    print("[INFO-PICTURES] Last url symbols was: " + f_last_symbols)
    file.close()
os.remove(os.path.normpath(os.getcwd() + fr"\data_url\last_url.txt"))

# creating new urls and downloading pictures
print("[INFO-PICTURES] Counting url...")
print("-"*20)

start = "a"  # you can change start number of url
for last_symbols in itertools.product(symbols, repeat=str_length):
    last_symbols = start + "".join(last_symbols)

    if last_symbols > f_last_symbols:
        if count < 10:
            url = fr"https://prnt.sc/{last_symbols}"
            print(f"[INFO-PICTURES] Checking url #{last_symbols}: {url}")
            req = requests.get(url=url, headers=headers)
            delay()
            soup = BeautifulSoup(req.text, "lxml")

            try:
                image = soup.find("img")
                image_url = image["src"]
                if removed[0] in image_url:
                    print("[INFO-PICTURES] This image was removed by case [1]")
                    print("-" * 20)
                elif removed[1] in image_url:
                    print("[INFO-PICTURES] This image was removed by case [2]")
                    print("-" * 20)
                elif removed[2] in image_url:
                    print("[INFO-PICTURES] This image was removed by case [3]")
                    print("-" * 20)
                else:
                    if count == 9:
                        count += 1
                        img = Image.open(requests.get(image_url, stream=True).raw)
                        img.save(os.path.normpath(os.getcwd() + fr"\data_images\{count}.png"))

                        # saving last url in last_url.txt
                        with open(os.path.normpath(os.getcwd() + r"\data_url\last_url.txt"), "w",
                                  encoding="utf-8") as file:
                            file.write(last_symbols)
                            file.close()

                        # creating backup last_url_backup.txt
                        os.remove(os.path.normpath(os.getcwd() + fr"\data_url\last_url_backup.txt"))
                        with open(os.path.normpath(os.getcwd() + r"\data_url\last_url_backup.txt"), "w",
                                  encoding="utf-8") as file:
                            file.write(last_symbols)
                            file.close()
                        print(f"[INFO-PICTURES] {count} picture/pictures was/were downloaded")
                        print(f"[INFO-PICTURES] *{last_symbols}* was written in file")
                        print("-" * 20)
                    else:
                        if count < 9:
                            count += 1
                            img = Image.open(requests.get(image_url, stream=True).raw)
                            img.save(os.path.normpath(os.getcwd() + fr"\data_images\{count}.png"))
                            print(f"[INFO-PICTURES] {count} picture/pictures was/were downloaded")
                            print("-" * 20)

                delay_strong()

            except Exception as ex:
                print(ex)
                print("[ERROR-PICTURES] There was some error with downloading pictures")
                delay_strong()
                print("-" * 20)
        else:
            break

        if last_symbols == start + "zzzzz":
            if start != "z":
                start = chr(ord(start.lower())+1)

print("[INFO] Opening browser...")

try:
    # going to vk.com and logging in
    print("[INFO-VK] Logging in...")
    driver.get("https://vk.com/")
    driver.find_element_by_id("index_email").send_keys(vk_login)
    driver.find_element_by_id("index_pass").send_keys(vk_password)
    driver.find_element_by_id("index_login_button").click()
    delay_strong()

    time.sleep(50)

    # check if recaptcha has appeared and then solve it
    print("[INFO-VK] Checking for recaptcha...")
    try:
        # switch to recaptcha frame
        frames = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(frames[0])
        delay()

        # click on captcha box
        driver.find_element_by_class_name("recaptcha-checkbox-border").click()
        delay()
        print("[INFO-CAPTCHA] Solving recaptcha...")

        # switch to captcha audio control frame
        driver.switch_to.default_content()
        frames = driver.find_element_by_xpath("/html/body/div[13]/div[4]").find_elements_by_tag_name("iframe")
        driver.switch_to.frame(frames[0])
        delay()

        # click on captcha audio button
        driver.find_element_by_id("recaptcha-audio-button").click()
        delay()

        # switch to recaptcha audio challenge frame
        driver.switch_to.default_content()
        frames = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(frames[-1])
        delay()

        # click on the play button
        driver.find_element_by_xpath("/html/body/div/div/div[3]/div").click()
        delay()

        # get the mp3 audio file
        src = driver.find_element_by_id("audio-source").get_attribute("src")
        print(f"[INFO-CAPTCHA] Audio src: {src}")

        # download the mp3 audio file from the source
        print("[INFO-CAPTCHA] Downloading audio captcha...")
        download = requests.get(src)
        delay()

        if download.status_code == 200:
            with open(os.path.normpath(os.getcwd() + r"\data_audio\sample.mp3"), 'wb') as f:
                f.write(download.content)
            print("[INFO-CAPTCHA] Audio captcha has downloaded successfully")
        else:
            print("[ERROR-CAPTCHA] Download Failed For File sample.mp3")

        # load downloaded mp3 audio file as .wav
        try:
            sound = pydub.AudioSegment.from_mp3(os.path.normpath(os.getcwd() + r"\data_audio\sample.mp3"))
            sound.export(os.path.normpath(os.getcwd() + r"\data_audio\sample.wav"), format="wav")
        except Exception as ex:
            print(ex)
            print("[ERROR-CAPTCHA] Please run program as administrator")

        r = sr.Recognizer()
        sample_audio = sr.AudioFile(os.path.normpath(os.getcwd() + r"\data_audio\sample.wav"))

        with sample_audio as source:
            audio = r.record(source)

        # translate audio to text with google voice recognition
        key = r.recognize_google(audio)
        print(f"[INFO-CAPTCHA] Recaptcha Passcode: {key}")
        delay()

        # send key in results and submit
        driver.find_element_by_id("audio-response").send_keys(key.lower())
        delay()
        driver.find_element_by_id("audio-response").send_keys(Keys.ENTER)
        driver.switch_to.default_content()
        delay()

        # deleting audio files
        os.remove(os.path.normpath(os.getcwd() + r"\data_audio\sample.mp3"))
        os.remove(os.path.normpath(os.getcwd() + r"\data_audio\sample.wav"))
        print(f"[INFO-CAPTCHA] Captcha was solved successfully")
        print(f"[INFO-CAPTCHA] Audio files were deleted")

    except Exception as ex:
        print(ex)
        print("[INFO-CAPTCHA] Captcha hasn't found")

    print("[INFO-VK] Logged in VK successfully")

    # going to community
    print("[INFO-VK] Going to community...")
    driver.get("https://vk.com/img_cursed")
    driver.find_element_by_id("submit_post_box").click()
    delay()

    # uploading pictures from data_images
    textarea = driver.find_element_by_class_name("file")
    count = 0
    pics_count = 20  # maximum count of pictures in data_images
    print("[INFO-VK] Uploading pictures...")

    for i in range(1, pics_count, 1):
        check_file = os.path.exists(os.path.normpath(os.getcwd() + fr"\data_images\{i}.png"))
        if check_file:
            count += 1
            textarea.send_keys(os.path.normpath(os.getcwd() + fr"\data_images\{i}.png"))
            delay()
            os.remove(os.path.normpath(os.getcwd() + fr"\data_images\{i}.png"))
            print(f"[INFO-VK] Pictures uploaded: {count}")
        else:
            i += 1
        if count == 10:
            break

    # posting pictures
    driver.find_element_by_id("send_post").click()
    print("[INFO-VK] Pictures has posted successfully")
    delay()

except Exception as ex:
    print(ex)
    print("[ERROR-VK] There was some error with locating VK elements or pictures")

finally:
    # closing browser
    delay()
    driver.close()
    driver.quit()
    print("[INFO] Browser has closed successfully")
    print("[INFO] Closing program...")
    delay_strong()
