#!/usr/bin/env python
import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
import selenium.webdriver
import selenium
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import time
from selenium.webdriver import FirefoxOptions
from selenium.webdriver import ChromeOptions
import pickle
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from random import randint
import unittest
import random
import urllib
import ConfigParser
import json

import subprocess

options = ChromeOptions()
config = None
WORDS = None
BAD_WORDS = None
SELF_HARM_WORDS = None
FQDNS = None
url = None
global_driver = None

def init_standard():
    global global_driver
    global url
    global options
    if None == global_driver:
        url = "https://youtube.com"
        #options.add_argument("--headless")
        if 'proxy_pac_url' in config:
            print "Setting up proxy pac: " + config['proxy_pac_url']
            options.add_argument("--proxy-auto-detect")
            options.add_argument('--proxy-pac-url=' + config['proxy_pac_url'])
        if is_mobile() :
            print "Setting up mobile browser"
            options.add_argument("user-agent=Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/71.0.3578.98 Mobile/13B143 Safari/601.1.46")
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        options.add_experimental_option("prefs",prefs)
	global_driver = webdriver.Chrome(chrome_options=options)
	#global_driver = webdriver.Chrome("/usr/local/bin/chromedriver.exe")

    return global_driver

timeout = 3

def securly_block_page_details(driver):
    try:
        details_ec = EC.presence_of_element_located((By.ID, 'inline'))
        details = WebDriverWait(driver, 5*timeout).until(details_ec)
        details.click()
        time.sleep(0.5)
        details_div = driver.find_element_by_id('inline-content')
        print "Blocked page details: %s\n" % ( details_div.get_attribute('innerHTML') )
    except Exception as e:
        print "Details not found"

def securly_choose_google_login(driver):
    try:
        google_login_ec = EC.presence_of_element_located((By.CLASS_NAME, 'google-button'))
        google_login = WebDriverWait(driver, timeout).until(google_login_ec)
        print "Found Login Button. Clicking to login..."
        google_login.click()
    except Exception as e:
        print "Not an out-of school case"


def google_do_login(driver):
    try:
        user = driver.find_element_by_id('identifierId')
        user.send_keys(config['kid_name'])
        user.send_keys(Keys.RETURN)
        time.sleep(2)
        pas = driver.find_element_by_name('password')
        pas.send_keys(config['kid_pass'])
        pas.send_keys(Keys.RETURN)
        time.sleep(3)
        print "Logged In"
    except Exception as e:
        print "Securly Login not needed. Proceeding..."

def wikipedia_search_term(driver, term):
    try:
        if is_mobile():
            search_bar_ec = EC.presence_of_element_located((By.ID, 'searchInput'))
        else:
            search_bar_ec = EC.presence_of_element_located((By.ID, 'searchInput'))
        search_bar = WebDriverWait(driver, timeout).until(search_bar_ec)
        search_bar.send_keys(term)
        search_bar.send_keys(Keys.RETURN)
        time.sleep(0.5)
    except Exception as e:
        print "Failed to search: " + str(e)

def wikipedia_search_other_term(driver, term):
    try:
        url_encoded_term = urllib.quote_plus(term)
        driver.get("https://en.wikipedia.org/w/index.php?search="+url_encoded_term+"&title=Special%3ASearch")
    except Exception as e:
        print "Failed to search: " + str(e)

# def youtube_search_term(driver, term):
#     try:
#         search_bar_ec = EC.presence_of_element_located((By.ID, 'header-bar'))
#         search_bar = WebDriverWait(driver, timeout).until(search_bar_ec)
#     except TimeoutException:
#         try:
#             driver.get("https://m.youtube.com/results?search_query="+term);
#         except TimeoutException:
#             driver.quit()
#             quit()
#     try:
#         search_bar = driver.find_element_by_id('search')
#     except Exception as e:
#         print "Failed to search: " + str(e)
#     try: 
#         search_bar = driver.find_element_by_name('search_query')
#         search_bar.send_keys(term)
#         search_bar.send_keys(Keys.RETURN)
# 
#         if is_mobile():
#             yt_search_res_ec = EC.presence_of_element_located((By.XPATH, '//ytm-compact-video-renderer'))
#         else:
#             yt_search_res_ec = EC.presence_of_element_located((By.CLASS_NAME, 'ytd-section-list-renderer'))
#         WebDriverWait(driver, timeout).until(yt_search_res_ec)
#     except Exception as e:
#         print "Failed to search: " + str(e)

def wikipedia_click_random_link(driver, count=1):
    done = False
    retry = 3
    while not done and retry > 0  :
        try:
            if is_mobile():
                links = driver.find_elements(By.XPATH, '//a[contains(@href,"/wiki/")]')
            else:
                links = driver.find_elements(By.XPATH, '//a[contains(@href,"/wiki/")]')
            if len(links):
                index = randint(1, len(links)-1)
                l = links[index]
                if len(l.text) == 0:
                    continue
                print "Clicking link with index: " + str(index) + " link: " + l.get_attribute('innerHTML')
                l.click()
                count -= 1
                if 0 == count:
                    done = True
                time.sleep(1)
            else:
                retry -= 1
                time.sleep(1)
        except Exception as e:
            if( False):
                print "This link didn't work[" +str(e) + "]. Trying another"
        except TimeoutException:
            if( False):
                print "Didn't find anything"

# def youtube_play_random_video(driver):
#     if is_mobile():
#         yt_search_res_ec = EC.presence_of_element_located((By.XPATH, '//ytm-compact-video-renderer'))
#     else:
#         yt_search_res_ec = EC.presence_of_element_located((By.CLASS_NAME, 'ytd-section-list-renderer'))
#     try:
#         WebDriverWait(driver, timeout).until(yt_search_res_ec)
#     except Exception as e:
#         return
# 
#     done = False
#     url = None
#     while not done:
#         try:
#             time.sleep(1)
#             if is_mobile():
#                 print "finding element: karthik1"
#                 links = driver.find_elements_by_xpath("//a[contains(@href, '/watch?v=')]")
#  		
# 	#	user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')
#             else: 
#                 #links = driver.find_elements_by_xpath("//a[contains(@href, '/watch?v=')]")
#                 links = driver.find_elements_by_partial_link_text("/watch?v=")
#             index = randint(1, len(links)-1)
#             l = links[index]
#             if len(l.text) == 0:
#                 continue
#             print "finding element: karthik2"
#             l.click()
#             print "finding element: karthik3"
#             time.sleep(3)
#             url = l.text
#             done = True
#         except Exception as e:
#             print "This link didn't work[" +str(e) + "]. Trying another"
#         except TimeoutException:
#             print "Didn't find anything"
#         finally:
#             if url:
#                 print "Played video with URL: " + url
            

def google_search_term(driver, term):
    driver.get("https://google.com")
    search = driver.find_element_by_name('q')
    search.send_keys(term)
    search.send_keys(Keys.RETURN)
    securly_choose_google_login(driver)
    google_do_login(driver)
    time.sleep(1) # sleep for 5 seconds so you can see the results

def google_search_image_term(driver, term):
    driver.get("https://images.google.com")
    securly_choose_google_login(driver)
    google_do_login(driver)
    search = driver.find_element_by_name('q')
    search.send_keys(term)
    search.send_keys(Keys.RETURN)
    time.sleep(1) # sleep for 5 seconds so you can see the results

def bing_search_term(driver, term):
    driver.get("https://bing.com")
    search = driver.find_element_by_name('q')
    search.send_keys(term)
    time.sleep(0.3)
    try: 
        search_it = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.NAME, "go"))
        )
        search_it.click()
    except:
        search.send_keys(Keys.RETURN)
    securly_choose_google_login(driver)
    google_do_login(driver)
    time.sleep(1) # sleep for 5 seconds so you can see the results

def yahoo_search_term(driver, term):
    driver.get("https://yahoo.com")
    securly_choose_google_login(driver)
    google_do_login(driver)
    search = driver.find_element_by_name('p')
    search.send_keys(term)
    search.send_keys(Keys.RETURN)
    time.sleep(1) # sleep for 5 seconds so you can see the results

# def facebook_access_single_page(driver, url):
#     page = driver.get(url)
#     print ""

def is_mobile():
    global config
    return ('mobile' in config and config['mobile'])

class SecurlyTests(unittest.TestCase):
    global config
    global WORDS
    global BAD_WORDS
    global SELF_HARM_WORDS
    global FQDNS
    driver = None

    #import pdb; pdb.set_trace()
    def read_conf(self):
        global config
        global WORDS
        global BAD_WORDS
        global SELF_HARM_WORDS
        global FQDNS
        cp = ConfigParser.ConfigParser()
        cp.read('securly_tests.conf')
        profile = 'default'
        config = {}
        config['words']             = cp.get('general', 'word_file', 0)
        config['bad_words']         = cp.get('general', 'bad_word_file', 0)
        config['self_harm_words']   = cp.get('general', 'self_harm_word_file', 1)
        config['misc_fqdns']        = json.loads(cp.get("general","misc_fqdns"))
        if cp.has_option('general', 'proxy_pac') :
            config['proxy_pac_url']     = cp.get('general', 'proxy_pac_url', 0)
        config['mobile']            = cp.getboolean('general', 'mobile')

        # Read kid credentials
        config['kid_name']          = cp.get(profile, 'kid_name', 0)
        config['kid_pass']          = cp.get(profile, 'kid_pass', 0)

        # Read Facebook credentials
        config['fb_user']           = cp.get(profile, 'fb_user', 0)
        config['fb_pass']           = cp.get(profile, 'fb_pass', 0)

        # Read Twitter credentials
        config['tw_user']           = cp.get(profile, 'tw_user', 0)
        config['tw_pass']           = cp.get(profile, 'tw_pass', 0)


        WORDS = open(config['words']).read().splitlines()
        BAD_WORDS = open(config['bad_words']).read().splitlines()
        SELF_HARM_WORDS = open(config['self_harm_words']).read().splitlines()
        FQDNS = config['misc_fqdns']

    def init_driver(self):
        global config
        if None == config:
            print "Initializing config"
            self.read_conf()
            
        if None == self.driver :
            print "Initializing driver"
            self.driver = init_standard()

    def setUp(self):
        print "\n--- BEGIN TEST [ " + self.id() + " ] ---"
        self.init_driver()

#     def facebook_single_page():
#         facebook_access_single_page(self.driver, "https://www.facebook.com/nikol.pashinyan")
#         time.sleep(1)

    def testYahooSearch(self):
        global WORDS, BAD_WORDS
        search_term = random.choice(WORDS)
        print self.id() + ": searching for: " + search_term
        yahoo_search_term(self.driver, search_term)
        time.sleep(1)

        search_term = random.choice(BAD_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": searching for bad term: " + search_term
        yahoo_search_term(self.driver, search_term)
        securly_block_page_details(self.driver)
        time.sleep(1)

        search_term = random.choice(SELF_HARM_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": searching for bad term: " + search_term
        yahoo_search_term(self.driver, search_term)
        time.sleep(1)

    def testBingSearch(self):
        global config
        global WORDS
        global BAD_WORDS
        global SELF_HARM_WORDS
        global FQDNS
        search_term = random.choice(WORDS)
        print self.id() + ": searching for: " + search_term
        bing_search_term(self.driver, search_term)
        time.sleep(1)
        search_term = random.choice(BAD_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": searching for bad term: " + search_term
        bing_search_term(self.driver, search_term)
        securly_block_page_details(self.driver)
        time.sleep(1)

        search_term = random.choice(SELF_HARM_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": searching for self-harm term: " + search_term
        bing_search_term(self.driver, search_term)
        time.sleep(1)

    def testGoogleSearch(self):
        global config
        global WORDS
        global BAD_WORDS
        global SELF_HARM_WORDS
        global FQDNS
        search_term = random.choice(WORDS)
        print self.id() + ": searching for: " + search_term
        google_search_term(self.driver, search_term)
        time.sleep(1)
        
        search_term = random.choice(BAD_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": searching for bad term: " + search_term
        google_search_term(self.driver, search_term)
        securly_block_page_details(self.driver)
        time.sleep(1)

        search_term = random.choice(SELF_HARM_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": searching for self-harm term: " + search_term
        google_search_term(self.driver, search_term)
        time.sleep(1)

    def testGoogleImageSearch(self):
        global config
        global WORDS
        global BAD_WORDS
        global SELF_HARM_WORDS
        global FQDNS
        search_term = random.choice(WORDS)
        print self.id() + ": image searching for: " + search_term
        google_search_image_term(self.driver, search_term)
        time.sleep(1)
        
        search_term = random.choice(BAD_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": image searching for bad term: " + search_term
        google_search_image_term(self.driver, search_term)
        securly_block_page_details(self.driver)
        time.sleep(1)

        search_term = random.choice(SELF_HARM_WORDS)
        search_term = search_term.replace("+", " ")
        print self.id() + ": image searching for self-harm term: " + search_term
        google_search_image_term(self.driver, search_term)
        time.sleep(1)

    def testWiki(self):
        global config
        global WORDS
        global BAD_WORDS
        global SELF_HARM_WORDS
        global FQDNS
        self.driver.get("https://wikipedia.org")
        securly_choose_google_login(self.driver)
        google_do_login(self.driver)
        search_term = random.choice(WORDS)
        for i in (0,1):
            print self.id() + ": searching(other) for: " + search_term
            if is_mobile():
                wikipedia_search_term(self.driver, search_term)
            else:
                wikipedia_search_other_term(self.driver, search_term)
            time.sleep(1)
            wikipedia_click_random_link(self.driver)
            if is_mobile(): 
                self.driver.get("https://wikipedia.org")

        search_term = random.choice(WORDS)
        for i in (0,1):
            print self.id() + ": searching for[#" + str(i) + "]: " + search_term
            wikipedia_search_term(self.driver, search_term)
            time.sleep(1)
            wikipedia_click_random_link(self.driver)
            time.sleep(1)
            if is_mobile(): 
                self.driver.get("https://wikipedia.org")

        if is_mobile():
            self.driver.get("https://wikipedia.org")

        search_term = random.choice(BAD_WORDS)
        print self.id() + ": searching for bad word: " + search_term
        wikipedia_search_term(self.driver, search_term)
        securly_block_page_details(self.driver)
        time.sleep(1)
        self.driver.get("https://wikipedia.org")
        time.sleep(1)
        search_term = random.choice(SELF_HARM_WORDS)
        print self.id() + ": searching for self harm word/phrase: " + search_term
        search_term = search_term.replace("+", " ")
        wikipedia_search_term(self.driver, search_term)

#     def testYouTubeVideoTitle(self):
#         global config
#         global WORDS
#         global BAD_WORDS
#         global SELF_HARM_WORDS
#         global FQDNS
#         if is_mobile(): 
#             self.driver.get("https://m.youtube.com")
#         else:
#             self.driver.get("https://www.youtube.com")
#         securly_choose_google_login(self.driver)
#         google_do_login(self.driver)
#         term = random.choice(WORDS)
#         print self.id() + ": Searching for term: " + term
#         youtube_search_term(self.driver, term)
#         print self.id() + ": Play random video"
#         youtube_play_random_video(self.driver);
#         time.sleep(3)
#         if is_mobile(): 
#             self.driver.get("https://m.youtube.com")
#         else:
#             self.driver.get("https://www.youtube.com")
#         term = random.choice(BAD_WORDS)
#         term = term.replace("+", " ")
#         print self.id() + ": Searching for BAD term: " + term
#         youtube_search_term(self.driver, term)
#         securly_block_page_details(self.driver)
#         time.sleep(1)
#         self.driver.get("https://youtube.com")
#         time.sleep(1)
#         term = random.choice(SELF_HARM_WORDS)
#         term = term.replace("+", " ")
#         print self.id() + ": Searching for self harm term: " + term
#         youtube_search_term(self.driver, term)
#         time.sleep(1)
# 
#     def testFacebook(self):
#         global config
#         global WORDS
#         global BAD_WORDS
#         global SELF_HARM_WORDS
#         global FQDNS
#         self.driver.get("https://www.facebook.com")
#         securly_choose_google_login(self.driver)
#         google_do_login(self.driver)
#         email = self.driver.find_element_by_id("email")
#         passw = self.driver.find_element_by_id("pass")
#         login = self.driver.find_element_by_id("loginbutton")
#         email.send_keys(config['fb_user'])
#         passw.send_keys(config['fb_pass'])
#         login.click()
#         #self.driver.get("https://www.facebook.com/apoorvu")
#         time.sleep(1)
#         post_box=self.driver.find_element_by_xpath("//*[@name='xhpc_message']")
#         post_box.click()
#         post_box.send_keys(time.strftime("%x %X"))
#         post_box.send_keys("\n Testing using Name not ID.Selenium is easy.")
#         time.sleep(2)
#         post_it = WebDriverWait(self.driver, 5).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "button._1mf7._4r1q._4jy0._4jy3._4jy1._51sy.selected._42ft"))
#         )
#         post_it.click()
#         print self.id() + ": Posted[ " + time.strftime("%x %X") + " ]..."
#         time.sleep(2)
# 
#     def testTwitter(self):
#         global config
#         global WORDS
#         global BAD_WORDS
#         global SELF_HARM_WORDS
#         global FQDNS
# 
#         self.driver.get("https://twitter.com")
#         securly_choose_google_login(self.driver)
#         google_do_login(self.driver)
#         time.sleep(1)
#         log = WebDriverWait(self.driver, 8).until(
#             EC.presence_of_element_located((By.LINK_TEXT, "Log in"))
#         )
#         log.click()
# 
#         time.sleep(1)
#         if is_mobile():
#             user_ec = EC.presence_of_element_located((By.NAME, 'session[username_or_email]'))
#         else:
#             user_ec = EC.presence_of_element_located((By.CLASS_NAME, 'js-username-field'))
#         username_field = WebDriverWait(self.driver, timeout).until(user_ec)
# 
# #        if is_mobile():
# #            username_field = self.driver.find_element_by_name('session[username_or_email]')
# #        else:
# #            username_field = self.driver.find_element_by_class_name("js-username-field")
#         username_field.send_keys(config['tw_user'])
#         time.sleep(1)
#         if is_mobile():
#             password_field= self.driver.find_element_by_name('session[password]')
#         else:
#             password_field = self.driver.find_element_by_class_name("js-password-field")
# 
#         password_field.send_keys(config['tw_pass'])
# 
#         if is_mobile():
#             password_field.send_keys(Keys.RETURN)
#         else:
#             self.driver.find_element_by_class_name("EdgeButtom--medium").click()
# 
# 
#         time.sleep(1)
#         if is_mobile():
#             post_box_ec = EC.presence_of_element_located((By.XPATH, ".//a[@href='/compose/tweet']"))
#             post_link = WebDriverWait(self.driver, timeout).until(post_box_ec)
#             post_link.click()
#             post_box_ec = EC.presence_of_element_located((By.XPATH, ".//textarea[@data-testid='tweetTextarea_0']"))
#             post_box = WebDriverWait(self.driver, timeout).until(post_box_ec)
#         else: 
#             post_box=self.driver.find_element_by_id("tweet-box-home-timeline")
#         post_box.send_keys(time.strftime("%x %X"))
#         post_text = ""
#         for i in range(0,5):
#             if post_text != "":
#                 post_text += " ";
#             post_text += random.choice(WORDS)
#         post_box.send_keys("\n" + post_text + ".\n")
#         time.sleep(1)
#         if is_mobile():
#             post_it_ec = EC.presence_of_element_located((By.XPATH, ".//div[@data-testid='tweetButton']"))
#             post_it = WebDriverWait(self.driver, timeout).until(post_it_ec)
#         else:
#             post_it = WebDriverWait(self.driver, 5).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "button.tweet-action.EdgeButton.EdgeButton--primary.js-tweet-btn"))
#             )
#         post_it.click()
#         print self.id() + ": Posted[ " + time.strftime("%x %X") + " ]..."
# 
#         time.sleep(1)
#         if is_mobile():
#             post_box_ec = EC.presence_of_element_located((By.XPATH, ".//a[@href='/compose/tweet']"))
#             post_link = WebDriverWait(self.driver, timeout).until(post_box_ec)
#             post_link.click()
#             post_box_ec = EC.presence_of_element_located((By.XPATH, ".//textarea[@data-testid='tweetTextarea_0']"))
#             post_box = WebDriverWait(self.driver, timeout).until(post_box_ec)
#         else: 
#             post_box=self.driver.find_element_by_id("tweet-box-home-timeline")
#         post_box.send_keys(time.strftime("%x %X"))
#         post_text = random.choice(SELF_HARM_WORDS)
#         post_text = post_text.replace('+', ' ')
#         post_box.send_keys("\n" + post_text + "\n")
#         time.sleep(1)
#         if is_mobile():
#             post_it_ec = EC.presence_of_element_located((By.XPATH, ".//div[@data-testid='tweetButton']"))
#             post_it = WebDriverWait(self.driver, timeout).until(post_it_ec)
#         else:
#             post_it = WebDriverWait(self.driver, 5).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "button.tweet-action.EdgeButton.EdgeButton--primary.js-tweet-btn"))
#             )
#         post_it.click()
#         print self.id() + ": Posted[ " + time.strftime("%x %X") + " ]..."
#         time.sleep(2)

    def testMisc(self):
        global config
        global WORDS
        global BAD_WORDS
        global SELF_HARM_WORDS
        global FQDNS
        for fqdn in FQDNS:
            self.driver.get(fqdn)
            securly_choose_google_login(self.driver)
            google_do_login(self.driver)
            print "Visiting " + fqdn + "."
            time.sleep(0.5)
            print "Done with " + fqdn + "."

    def tearDown(self):
        #self.driver.close()
        print "\n--- END TEST [ " + self.id() + " ] ---"

if __name__ == '__main__':
    print "test"
    suite = unittest.TestLoader().loadTestsFromTestCase(SecurlyTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

