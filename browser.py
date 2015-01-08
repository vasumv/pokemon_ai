import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

class Selenium():
    BASE_URL="http://play.pokemonshowdown.com"
    #BASE_URL="http://frost.psim.us"
    def __init__(self, url=BASE_URL, driver_path="/home/vasu/Downloads/chromedriver"):
        self.url = url
        self.driver_path = driver_path
        #PROXY = "127.0.0.1:9666"
        #chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--proxy-server=%s' % PROXY)
        #self.driver = webdriver.Chrome(executable_path=self.driver_path, chrome_options=chrome_options)
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        #self.driver = webdriver.PhantomJS()

        self.state = None
        self.poke_map = {
            0:0,1:1,2:2,3:3,4:4,5:5
        }

    def start_driver(self):
        self.driver.get(self.url)

    def get_state(self):
        url = self.driver.current_url
        if "battle" in url:
            return "battle"
        else:
            return "lobby"

    def login(self, username, password):
        time.sleep(1)
        #button = driver.find_element_by_xpath("//*[@id='mainmenu']/div/div[1]/div[2]/div[1]/form/p[1]/button")
        #text = button.text
        #if text != "Random Battle":
            #while text != "Random Battle":
                #time.sleep(2)
                #text = button.text
        while not self.check_exists_by_xpath("//*[@id='mainmenu']/div/div[1]/div[2]/div[1]/form/p[1]/button"):
            time.sleep(1)
        elem = self.driver.find_element_by_name("login")
        elem.click()
        time.sleep(1)
        user = self.driver.find_element_by_name("username")
        user.send_keys(username)
        user.send_keys(Keys.RETURN)
        while not self.check_exists_by_name("password"):
            time.sleep(1)
        passwd = self.driver.find_element_by_name("password")
        passwd.send_keys(password)
        passwd.send_keys(Keys.RETURN)
        time.sleep(1)

    def choose_tier(self, tier='ou'):
        form = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[1]/form/p[1]/button")
        form.click()
        ou = self.driver.find_element_by_xpath("/html/body/div[4]/ul[1]/li[4]/button")
        ou.click()

    def start_battle(self):
        url1 = self.driver.current_url
        battle = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[1]/form/p[3]/button")
        battle.click()
        while url1 == self.driver.current_url:
            time.sleep(1.5)
            #print "waiting"
        #print "found battle"

    def get_battle_id(self):
        url = self.driver.current_url
        url_list = url.split('-')
        id = url_list[-2:]
        return '-'.join(id)

    def make_team(self, team):
        builder = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[2]/p[1]/button")
        builder.click()
        new_team = self.driver.find_element_by_xpath("/html/body/div[4]/div/ul/li[2]/button")
        new_team.click()
        time.sleep(3)
        import_button = self.driver.find_element_by_xpath("/html/body/div[4]/div[2]/ol/li[4]/button")
        import_button.click()
        textfield = self.driver.find_element_by_xpath("/html/body/div[4]/textarea")
        textfield.send_keys(team)
        save = self.driver.find_element_by_xpath("/html/body/div[4]/div/button[3]")
        save.click()
        close_button = self.driver.find_element_by_xpath("//*[@id='header']/div[2]/div/ul[1]/li[2]/a[2]")
        close_button.click()
        time.sleep(2)

    def turn_off_sound(self):
        sound = self.driver.find_element_by_xpath("//*[@id='header']/div[3]/button[2]")
        sound.click()
        mute = self.driver.find_element_by_xpath("/html/body/div[4]/p[3]/label/input")
        mute.click()

    def get_opp_primary(self):
        img = self.driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[4]/div[1]/img[6]")
        text = img.get_attribute('src')
        back = text.rindex('.')
        poke = text[46:back]
        if "shiny" in poke:
            poke = poke[6:]
        return poke

    def move(self, index, backup_switch, mega=False, volt_turn=None):
        if self.check_alive():
            if mega:
                mega_button = self.driver.find_element_by_xpath('/html/body/div[4]/div[5]/div/div[2]/div[2]/label/input')
                mega_button.click()
            move = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[%d]" % (index + 1))
            move.click()
            if volt_turn is not None:
                #print "Waiting for volt turn"
                self.wait_for_move()
                self.volt_turn(volt_turn)
        self.wait_for_move()
        self.backup_switch(backup_switch)

    def switch(self, index, backup_switch):
        if self.check_alive():
            i = self.poke_map[index]
            choose = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[3]/div[2]/button[%d]" % (i + 1))
            choose.click()
            old_primary = None
            for k, v in self.poke_map.items():
                if v == 0:
                    old_primary = k

            self.poke_map[index] = 0
            self.poke_map[old_primary] = i

        self.wait_for_move()
        self.backup_switch(backup_switch)

    def backup_switch(self, index):
        #print "Backup switching"
        if not self.check_alive():
            #print "Is alive"
            i = self.poke_map[index]
            choose = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[%d]" % (i + 1))
            choose.click()
            old_primary = None
            for k, v in self.poke_map.items():
                if v == 0:
                    old_primary = k
            self.poke_map[index] = 0
            self.poke_map[old_primary] = i
            self.wait_for_move()

    def volt_turn_switch(self, index):
        if not self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[6]"):
            pass
        else:
            i = self.poke_map[index]
            choose = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[%d]" % (i + 1))
            choose.click()
            old_primary = None
            for k, v in self.poke_map.items():
                if v == 0:
                    old_primary = k
            self.poke_map[index] = 0
            self.poke_map[old_primary] = i
        self.wait_for_move()

    def volt_turn(self, volt_turn):
        #print "Volt turning"
        my_team = self.get_my_team()
        for poke in my_team.values():
            #print poke['primary'], poke['alive']
            if poke['primary'] and poke['alive']:
                self.volt_turn_switch(volt_turn)
                break

    def check_alive(self):
        return self.check_exists_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[2]/strong")

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def check_exists_by_id(self, id):
        try:
            self.driver.find_element_by_id(id)
        except NoSuchElementException:
            return False
        return True

    def check_exists_by_name(self, name):
        try:
            self.driver.find_element_by_name(name)
        except NoSuchElementException:
            return False
        return True

    def start_timer(self):
        if self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/p[2]/button"):
            timer = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/p[2]/button")
            print "Got timer", timer.text
            if timer.text == "Start timer":
                timer.click()

    def get_log(self):
        log = self.driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]")
        return log.text.encode('utf-8')

    def wait_for_move(self):
        move_exists = self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
        self.start_timer()
        while move_exists == False:
            #print "waiting for their move"
            time.sleep(2)
            move_exists = self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
            if self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/p[1]/em/button[2]"):
                save_replay = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/p[1]/em/button[2]")
                save_replay.click()
                #print "clicked save replay"
                while not self.check_exists_by_id(self.get_battle_id()):
                    time.sleep(1)
                ps_overlay = self.driver.find_element_by_xpath("/html/body/div[6]")
                ps_overlay.click()
                raise SeleniumException()

        #print "their move just ended"

    def reset(self):
        close = self.driver.find_element_by_xpath("//*[@id='header']/div[2]/div/ul[2]/li/a[2]")
        close.click()
        if self.check_exists_by_xpath("/html/body/div[6]/div/form/p[2]/button[1]"):
            forfeit = self.driver.find_element_by_xpath("/html/body/div[6]/div/form/p[2]/button[1]")
            forfeit.click()
        time.sleep(2)

    def close(self):
        self.driver.close()

    def get_opp_team(self):
        names = self.driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]/div[15]/em")
        name_list = names.text.split("/")
        name_list = [x.strip(" ") for x in name_list]
        opp_info = {}
        for i in range(2, 4):
            for j in range(1, 4):
                opp_poke_info = {}
                opp_health = self.driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[8]/div/div[%d]/span[%d]" % (i, j))
                title = opp_health.get_attribute("title")
                hp = re.sub("[^0-9]", "", title)
                health = 100.0 if hp == '' else float(hp)
                name_info = ''.join([x for x in name_list if x in title])
                alive = not "fainted" in title
                primary = "active" in title
                if primary:
                    opp_poke_info['health'] = self.get_opp_primary_health()
                else:
                    opp_poke_info['health'] = health
                opp_poke_info['alive'] = alive
                opp_poke_info['primary'] = primary
                opp_info[name_info] = opp_poke_info
        return opp_info

    def get_my_team(self):
        names = self.driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]/div[14]/em")
        name_list = names.text.split("/")
        name_list = [x.strip(" ") for x in name_list]
        my_info = {}
        for i in range(2, 4):
            for j in range(1, 4):
                my_poke_info = {}
                my_health = self.driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[7]/div/div[%d]/span[%d]" % (i, j))
                title = my_health.get_attribute("title")
                hp = re.sub(r"[^0-9\.]", "", title)
                health = 100.0 if hp == '' else float(hp)
                name_info = ''.join([x for x in name_list if x in title])
                alive = not "fainted" in title
                primary = "active" in title
                if primary:
                    my_poke_info['health'] = self.get_my_primary_health()
                else:
                    my_poke_info['health'] = health
                my_poke_info['alive'] = alive
                my_poke_info['primary'] = primary
                my_info[name_info] = my_poke_info
        return my_info


    def get_my_primary_health(self):
        if self.check_exists_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[contains(@class,'statbar rstatbar')]/div/div[1]"):
            hp_text = self.driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[contains(@class,'statbar rstatbar')]/div/div[1]")
            hp = hp_text.text.strip("%")
            hp = int(hp)
        else:
            hp = 0
        return hp

    def get_opp_primary_health(self):
        if self.check_exists_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[contains(@class,'statbar lstatbar')]/div/div[1]"):
            hp_text = self.driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[contains(@class,'statbar lstatbar')]/div/div[1]")
            hp = hp_text.text.strip("%")
            hp = int(hp)
        else:
            hp = 0
        return hp

class SeleniumException(Exception):
    pass

if __name__ == "__main__":
    with open('log.txt', 'r') as fp:
        log_text = fp.read()
    SimulatorLog.parse(log_text)
    #selenium = Selenium(url='http://replay.pokemonshowdown.com/oususpecttest-197218079')

    #selenium.start_driver()
    #play = selenium.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[1]/div/button[2]')
    #play.click()
    #for i in range(20):
        #skip = selenium.driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div[3]/button[3]')
        #skip.click()
    #time.sleep(5)
    #with open('log2.txt', 'w') as f:
        #f.write(selenium.get_log().encode('utf-8'))
