from urllib.parse import urlparse
import browser_cookie3
from requests.utils import dict_from_cookiejar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.service import Service # Apparently this avoids selenium-manager
from selenium.webdriver.support import expected_conditions as EC
import yt_dlp
import threading


apple_url = "https://music.apple.com"
playlist_url = "PLAYLIST LINK HERE"
timeout_wait_time = 15


save_location = "Downloaded/"
filename_template = "%(title)s.%(ext)s"


driver = webdriver.Firefox(service=Service('/usr/bin/geckodriver')) # This change together with line 6 should fix "NoSuchDriverException on Linux"
base_url = urlparse(apple_url).netloc
cookies = browser_cookie3.firefox(domain_name=f'.{base_url}')
cookies_dict = dict_from_cookiejar(cookies)
driver.get(apple_url)
for c_name, c_value in cookies_dict.items():
    driver.add_cookie({'name': c_name, 'value': c_value})
driver.get(playlist_url)


song_data = WebDriverWait(driver, timeout_wait_time).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@data-testid="track-list-item"]')))


print("Found these songs:")
for i in range(len(song_data)):
    stripped_data = song_data[i].get_attribute("aria-label")
    modified_data = stripped_data.replace("Explicit, ", "")
    song_data[i] = modified_data
    print(modified_data)


driver.quit()


def search_and_download_youtube_music(search_term):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"{save_location}/{filename_template}",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'webm',
            'preferredquality': '192',
        }],
    }


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download(f'ytsearch1:{search_term}')
        print(error_code)


    except Exception as e:
        print(f"An error occurred: {e}")


# This is very stupid, only reason I made it like this was as I was downloading only small playlists, and my machine can support it.
for song in song_data:
    threading.Thread(target=search_and_download_youtube_music, args=(song, )).start()
