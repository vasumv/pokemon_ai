import time
import os
from showdown_ai import Selenium
from selenium.webdriver.common.keys import Keys
selenium = Selenium(url='http://replay.pokemonshowdown.com/')

selenium.start_driver()
user_input = raw_input("Enter username: ")
username = selenium.driver.find_element_by_xpath("/html/body/div[2]/div/form/p/label/input")
username.send_keys(user_input)
username.send_keys(Keys.RETURN)
while "Search results" not in selenium.driver.find_element_by_xpath("/html/body/div[2]/div/h1[2]").text:
    print "checking for search thing"
    time.sleep(1)
for i in range(20):
    link = selenium.driver.find_element_by_xpath("/html/body/div[2]/div/ul/li[%d]" % (i+4))
    if "ou" not in link.get_attribute("href"):
        continue
    link.click()
    while not selenium.check_exists_by_xpath("/html/body/div[3]/div/div/div[1]/div/button[2]"):
        time.sleep(1)
    play = selenium.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[1]/div/button[2]")
    play.click()
    while not selenium.check_exists_by_xpath("/html/body/div[3]/div/div/div[3]/button[3]"):
        time.sleep(1)
    #turn = selenium.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[3]/button[4]")
    #turn.click()
    #try:
        #turn.send_keys("100")
    #except UnexpectedAlertPresentException:
        #alert = selenium.driver.switch_to_alert()
        #print "i got the alert"
        #time.sleep(2)
        #alert.send_keys('100')
        #print "just sent 100"
        #time.sleep(2)
        #alert.send_keys(Keys.RETURN)
        #print "just pressed enter"
    time.sleep(2)
    log = selenium.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[2]").text.encode('utf-8')
    while "won the battle" not in log:
        for i in range(5):
            skip = selenium.driver.find_element_by_xpath('/html/body/div[3]/div/div/div[3]/button[3]')
            skip.click()
        log = selenium.driver.find_element_by_xpath("/html/body/div[3]/div/div/div[2]").text.encode('utf-8')
    time.sleep(3)
    url = selenium.driver.current_url
    url_list = url.split('-')
    battle_id = 'ou-' + url_list[1]
    if not os.path.exists("logs/%s" % (user_input)):
        os.makedirs("logs/%s" % (user_input))
    with open("logs/%s/%s.log" % (user_input, battle_id), "w") as f:
        f.write(log)
    selenium.driver.back()
    time.sleep(2)
#play = selenium.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/button[2]')
#play.click()
#for i in range(20):
    #skip = selenium.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[3]/button[3]')
    #skip.click()
#time.sleep(5)
#with open('log2.txt', 'w') as f:
    #f.write(selenium.get_log().encode('utf-8'))
