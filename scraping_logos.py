import selenium
from selenium import webdriver
import time
import requests
import os
from PIL import Image
import io
import hashlib
import codecs

DRIVER_PATH = 'chromedriver_win32/chromedriver.exe'

file = open('Investors.csv', 'r', encoding='utf-8') 

#function to find image links
def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=1):

    #search for query
    wd.get('https://www.google.ae/imghp?hl=en&ogbl')
    search_box = wd.find_element_by_css_selector('input.gLFyf')
    search_box.send_keys(query+' company logo')
    search_box.submit()

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                time.sleep(sleep_between_interactions)

                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls

#function for downloading images
def persist_image(folder_path:str,file_name:str,url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        folder_path = os.path.join(folder_path,file_name)

        #add image to existing folder
        if os.path.exists(folder_path):
            file_path = os.path.join(folder_path, file_name + '.jpg')
        #create folder if does not exist and add image
        else:
            os.mkdir(folder_path)
            file_path = os.path.join(folder_path, file_name + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
            print(f)
        print(f"SUCCESS - saved {url} - as {file_path}")

    #raise exception if file cannot be saved
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

#main function
if __name__ == '__main__':
    wd = webdriver.Chrome(executable_path=DRIVER_PATH)
    queries = []
    website = []
    category = []
    first_line = file.readline()

    #read file and store data
    for line in file:
        if line.split(',')[0] != '':
            queries.append(line.split(',')[0])
        website.append(line.split(',')[1])
        category.append(line.split(',')[3])

    #search for query logos
    for query in queries:
        wd.get('https://www.google.ae/imghp?hl=en&ogbl')
        
        links = fetch_image_urls(query,1,wd)

        images_path = 'fake'
        for i in links:
            persist_image(images_path,query,i)

    file.close()

    #open file for writing logo names
    wfile = open('InvestorsLol.csv', 'w', encoding='utf-8') 

    #write first line
    wfile.write(first_line)
    i=0

    #write all data in new file
    for line in range(len(queries)):
        wfile.write(queries[i]+',')
        wfile.write(website[i]+',')
        wfile.write(queries[i]+'.jpg'+',')
        wfile.write(category[i])
        i = i+1

    #close file
    wfile.close()
    wd.quit()



