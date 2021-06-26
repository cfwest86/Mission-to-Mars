
# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    # Run all scraping functions and store results in dictionary
    news_title, news_paragraph, news_href = mars_news(browser)
    mars_high, mars_low, mars_date = mars_weather(browser)
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "news_href": news_href,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": mars_hemispheres(browser),
      "orbiter_image": featured_orbiter_image(browser),
      "mars_high": mars_high,
      "mars_low" : mars_low,
      "mars_date": mars_date,
      }
    
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/mars2020/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:
        
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = news_soup.findAll('a')[59].get_text()
        news_href = news_soup.findAll("a")[58].get('href')
        # Use the parent element to find the paragraph text
        news_p = news_soup.findAll('p')[4].get_text()
    
    except AttributeError:
        return None, None

    return news_title, news_p, news_href

#get mars temps 

def mars_weather(browser):
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/mars2020/weather/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    weather_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:
        
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        mars_high = weather_soup.findAll('span', class_="fahrenheit")[0].get_text()
        mars_low = weather_soup.findAll('span', class_="fahrenheit")[1].get_text()
        mars_date= weather_soup.find('span', class_="earthDate").get_text()
    except AttributeError:
        return None, None

    return mars_high, mars_low, mars_date


# ### Featured Images 

def featured_image(browser):
    # Visit URL
    url = 'https://mars.nasa.gov/mars2020/multimedia/raw-images/'
    browser.visit(url)

    # Find and click the full image button
 

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url by tag, index of tag and then get src 
        img_url = img_soup.findAll("img")[2].get('src')

    except AttributeError:
        return None
    
    return img_url

def featured_orbiter_image(browser):
    # Visit URL
    url = 'https://www.nasa.gov/mission_pages/MRO/images/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('a')[69]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='img-responsive').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    orbiter_img_url = f'https://nasa.gov{img_url_rel}'

    return orbiter_img_url

#By specifying an index of 0, we're telling Pandas to pull only the first table it encounters,
#or the first item in the list. Then, it turns the table into a DataFrame.
# we then assign columns to clarify the information
#df.set_index('description', inplace=True) By using the .set_index() function, we're turning the Description column into the DataFrame's index. inplace=True means that the updated index will remain in place, without having to reassign the DataFrame to a new variable.
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


def mars_hemispheres(browser):
    hemisphere_image_urls = []
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    for x in range (0,4):
    
        hemispheres = {} 
        hem = browser.find_by_tag('h3')[x]
        hem.click()
        html = browser.html
        hem_soup= soup(html, 'html.parser')
        browser.is_element_present_by_css('div.list_text', wait_time=1)
        title = hem_soup.find('h2').get_text()
        img_url_rel = hem_soup.find('img', class_="wide-image").get('src')
        img_url = f'https://marshemispheres.com/{img_url_rel}'
        hemispheres.update({'img_url':img_url,"title": title})
        hemisphere_image_urls.append(hemispheres)
        browser.back()

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

