import time
import re
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

class Selenium():
    BASE_URL="http://play.pokemonshowdown.com"
    def __init__(self, url=BASE_URL, driver_path="/home/vasu/Downloads/chromedriver"):
        self.url = url
        self.driver_path = driver_path
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.alive = True
        self.state = None

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
        elem = self.driver.find_element_by_name("login")
        elem.click()
        time.sleep(1)
        user = self.driver.find_element_by_name("username")
        user.send_keys(username)
        user.send_keys(Keys.RETURN)
        time.sleep(2)
        while not self.check_exists_by_xpath("/html/body/div[4]/div/form/p[4]/label/input"):
            time.sleep(2)
        passwd = self.driver.find_element_by_xpath("/html/body/div[4]/div/form/p[4]/label/input")
        passwd.send_keys(password)
        passwd.send_keys(Keys.RETURN)
        time.sleep(1)

    def start_battle(self):
        url1 = self.driver.current_url
        time.sleep(5)
        form = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[1]/form/p[1]/button")
        form.click()
        ou = self.driver.find_element_by_xpath("/html/body/div[4]/ul[1]/li[4]/button")
        ou.click()
        battle = self.driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[1]/form/p[3]/button")
        battle.click()
        while url1 == self.driver.current_url:
            time.sleep(1.5)
            print "waiting"
        print "found battle"

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
        self.driver.get(self.url)
        time.sleep(2)

    def turn_off_sound(self):
        sound = self.driver.find_element_by_xpath("//*[@id='header']/div[3]/button[2]")
        sound.click()
        mute = self.driver.find_element_by_xpath("/html/body/div[4]/p[3]/label/input")
        mute.click()

    def move(self, index, backup_switch):
        if self.alive:
            move = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[%d]" % (index + 1))
            move.click()
        else:
            self.backup_switch(backup_switch)
        self.wait_for_move()

    def switch(self, index, backup_switch):
        if self.alive:
            choose = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[%d]" % (index + 1))
            choose.click()
        else:
            self.backup_switch(backup_switch)
        self.wait_for_move()

    def backup_switch(self, index):
        choose = self.driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[%d]" % (index + 1))
        choose.click()
        self.wait_for_move()

    def check_alive(self):
        return self.check_exists_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[2]/strong")

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def wait_for_move(self):
        move_exists = self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
        while move_exists == False:
            print "waiting for their move"
            time.sleep(2)
            move_exists = self.check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
        print "their move just ended"

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
                hp = re.sub("[^0-9]", "", title)
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

if __name__ == "__main__":
    with open("pokemon_team.txt") as f:
        selenium = Selenium()
        selenium.start_driver()
        selenium.turn_off_sound()
        selenium.login("asdf8000", "seleniumpython")
        selenium.make_team(f.read())
        selenium.start_battle()
        #selenium.switch(1, 3)
        #opp_team = selenium.get_opp_team()
        #print "primary:", opp_team.primary()
        #print "pokes: ", opp_team.poke_list
        #print "poke: ", opp_team.primary().moveset
#flinch_count = 0
#chromePath = "/home/vasu/Downloads/chromedriver"
#url = "http://play.pokemonshowdown.com"
#f = open("pokemon_team.txt")
#team = f.read()
#f2 = open("darkpokes.txt")
#darkpokes = f2.read()
#f3 = open("threats.txt")
#threats = f3.read()
#f4 = open("darkthreats.txt")
#dark_threats = f4.read()
#username = "asdf7000"
#password = "seleniumpython"


#def make_team(team):
        #builder = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[2]/p[1]/button")
        #builder.click()
        #new_team = driver.find_element_by_xpath("/html/body/div[4]/div/ul/li[2]/button")
        #new_team.click()
        #time.sleep(3)
        #import_button = driver.find_element_by_xpath("/html/body/div[4]/div[2]/ol/li[4]/button")
        #import_button.click()
        #textfield = driver.find_element_by_xpath("/html/body/div[4]/textarea")
        #textfield.send_keys(team)
        #save = driver.find_element_by_xpath("/html/body/div[4]/div/button[3]")
        #save.click()
        #driver.get(url)
        #time.sleep(2)

#def start_battle():
        #url1 = driver.current_url
        #time.sleep(5)
        #form = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[1]/form/p[1]/button")
        #form.click()
        #ou = driver.find_element_by_xpath("/html/body/div[4]/ul[1]/li[4]/button")
        #ou.click()
        #battle = driver.find_element_by_xpath("/html/body/div[2]/div/div[1]/div[2]/div[1]/form/p[3]/button")
        #battle.click()
        ##challenge chris:
        ##lobby = driver.find_element_by_xpath("/html/body/div[3]/div/div/div[1]/a")
        ##lobby.click()
        ##time.sleep(2)
        ##usav = driver.find_element_by_xpath("//*[@id='lobby-userlist-user-usavisfat']/button/span")
        ##usav.click()
        ##time.sleep(2)
        ##challenge = driver.find_element_by_xpath("/html/body/div[5]/p/button[1]")
        ##challenge.click()
        ##form = driver.find_element_by_xpath("//*[@id='mainmenu']/div/div[1]/div[1]/div/div[1]/div[1]/form/p[2]/button")
        ##form.click()
        ##time.sleep(2)
        ##ou = driver.find_element_by_xpath("/html/body/div[5]/ul[1]/li[3]/button")
        ##ou.click()
        ##time.sleep(2)
        ##make_challenge = driver.find_element_by_xpath("//*[@id='mainmenu']/div/div[1]/div[1]/div/div[1]/div[1]/form/p[4]/button[1]")
        ##make_challenge.click()
        ##lobby_quit = driver.find_element_by_xpath("//*[@id='header']/div[2]/div/ul[2]/li[1]/a[2]")
        ##lobby_quit.click()

        #while url1 == driver.current_url:
            #time.sleep(1.5)
            #print "waiting"
        #print "found battle"

#def switch_poke(poke):
        #if poke == "Smeargle":
            #choose = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[4]")
            #choose.click()
        #elif poke == "Diglett":
            #choose = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[2]")
            #choose.click()
        #elif poke == "Dugtrio":
            #choose = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[3]")
            #choose.click()
        #elif poke == "Clefable":
            #choose = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[5]")
            #choose.click()
        #elif poke == "Espeon":
            #choose = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[6]")
            #choose.click()
        #elif poke == "Sableye":
            #choose = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
            #choose.click()
        #time.sleep(2)
        #start_timer()
        #wait_for_move()

#def make_move(move):
        #if move == "Taunt" or move == "Moonlight"  or move == "Dark Void"  or move == "Earthquake" or move == "Morning Sun":
            #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
            #move.click()
        #elif move == "Geomancy" or move == "Reversal"  or move == "Stored Power"  or move == "Knock Off":
            #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[2]")
            #move.click()
        #elif move == "Baton Pass" or move == "Stealth Rock"  or move == "Moonblast"  or move == "Hidden Power Fighting" or move == "Gravity":
            #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[3]")
            #move.click()
        #elif move == "Memento" or move == "Will-O-Wisp"  or move == "Substitute"  or move == "Cotton Guard":
            #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[4]")
            #move.click()
        #time.sleep(2)
        #start_timer()
        #wait_for_move()
        #log = get_log()
        #if log.count("flinched and couldn't move!") > flinch_count:
            #print "i got flinched!"
            #while log.count("flinched and couldn't move!") > flinch_count:
                #if move == "Taunt" or move == "Moonlight"  or move == "Dark Void"  or move == "Earthquake" or move == "Morning Sun":
                    #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
                    #move.click()
                #elif move == "Geomancy" or move == "Reversal"  or move == "Stored Power"  or move == "Knock Off":
                    #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[2]")
                    #move.click()
                #elif move == "Baton Pass" or move == "Stealth Rock"  or move == "Moonblast"  or move == "Hidden Power Fighting" or move == "Gravity":
                    #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[3]")
                    #move.click()
                #elif move == "Memento" or move == "Will-O-Wisp"  or move == "Substitute"  or move == "Cotton Guard":
                    #move = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[4]")
                    #move.click()
                #global flinch_count
                #flinch_count += 1
                #log = get_log()

#def get_team():
        #team = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]/div[15]/em")
        #print team.text
        #team_list = team.text.split("/")
        #print team_list
        #return team_list

#def get_hp():
        #if check_exists_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[contains(@class,'statbar rstatbar')]/div/div[1]"):
            #hp_text = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[5]/div[contains(@class,'statbar rstatbar')]/div/div[1]")
            #hp = hp_text.text.strip("%")
            #hp = int(hp)
        #else:
            #hp = 0
        #return hp

#def get_weather():
        #if check_exists_by_xpath("/html/body/div[4]/div[1]/div/div[2]"):
            #weather = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[2]")
            #return weather.text
        #else:
            #return "none"

#def get_log():
        #log = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]")
        #return log.text

#def get_ditto():
        #transformed = check_exists_by_xpath("/html/body/div[5]/div[1]/div/div[5]/div[1]/div/div[4]/span")
        #return transformed

#def get_player_number():
        #player = driver.find_element_by_xpath("/html/body/div[4]/div[3]/div[1]/div[1]/small")
        #print player.text
        #if username in player.text:
            #return 1
        #else:
            #return 2

#def get_opp_poke():
        #img = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[4]/div[1]/img[6]")
        #text = img.get_attribute('src')
        #back = text.rindex('.')
        #poke = text[46:back]
        #if "shiny" in poke:
            #poke = poke[6:]
        #return poke

#def get_my_poke():
        #return None

#def check_sub():
        #sub = driver.find_element_by_xpath("/html/body/div[4]/div[1]/div/div[4]/div[4]/img[1]")
        #sub_text = sub.get_attribute('style')
        #sub_text = sub_text[-2:-1]
        #opacity = int(sub_text)
        #print "my opacity is " + str(opacity)
        #if opacity > 1:
            #return True
        #else:
            #return False


#def check_exists_by_xpath(xpath):
        #try:
            #driver.find_element_by_xpath(xpath)
        #except NoSuchElementException:
            #return False
        #return True

#def check_exists_by_class_name(name):
        #try:
            #driver.find_element_by_class_name(name)
        #except NoSuchElementException:
            #return False
        #return True

#def check_exists_by_name(name):
        #try:
            #driver.find_element_by_name(name)
        #except NoSuchElementException:
            #return False
        #return True

#def start_timer():
        #if check_exists_by_xpath("/html/body/div[4]/div[5]/div/p[2]/button"):
            #timer = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/p[2]/button")
            #if timer.text == "Start timer":
                #timer.click()

#def turn_off_sound():
        #sound = driver.find_element_by_xpath("//*[@id='header']/div[3]/button[2]")
        #sound.click()
        #mute = driver.find_element_by_xpath("/html/body/div[4]/p[3]/label/input")
        #mute.click()

#def chat(message):
        #chatbox = driver.find_element_by_xpath("/html/body/div[4]/div[4]/form/textarea[2]")
        #chatbox.send_keys(message)
        #chatbox.send_keys(Keys.RETURN)

#def check_taunt():
        #bad = driver.find_elements_by_class_name("bad")
        #bad_text = [x.text for x in bad]
        #if "Taunt" in bad_text:
            #return True
        #else:
            #return False

#def check_toxic():
        #status = driver.find_elements_by_class_name("status")
        #status_text = [x.text for x in status]
        #print status_text
        #if any("TOX" in x for x in status_text):
            #return True
        #else:
            #return False

#class FinishedException(Exception):
        #def __init__(self, won):
            #self.won = won

#class LostException():
        #def __init__(self, lost):
            #self.lost = lost

#def wait_for_move():
        #move_exists = check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
        #while move_exists == False:
            #print "waiting for their move"
            #time.sleep(2)
            #move_exists = check_exists_by_xpath("/html/body/div[4]/div[5]/div/div[2]/div[2]/button[1]")
            #if check_exists_by_xpath("/html/body/div[4]/div[5]/div/p[1]/em/button[2]"):
                #save_replay = driver.find_element_by_xpath("/html/body/div[4]/div[5]/div/p[1]/em/button[2]")
                #save_replay.click()
                #time.sleep(10)
                #raise FinishedException(True)
        #time.sleep(3)
        #print "their move just ended"

#def run(driver):
        #driver.get(url)
        #start_battle()
        #time.sleep(5)
        #with open("introchat.txt", "r") as f5:
            #hellomessage = f5.read()
            #chat(hellomessage)
        #opponent_team = get_team()
        #opp_team = [x.encode('ascii','ignore').strip() for x in opponent_team]
        #player = get_player_number()
        #print "i am player " + str(player)
        #wait_for_move()
        #switch_poke("Sableye")
        #print "used taunt"
        #make_move("Taunt")
        #taunt = check_taunt()
        #tox = check_toxic()
        #print "tox: " + str(tox)
        #time.sleep(5)
        #curr_hp = get_hp()
        #print curr_hp
        #if curr_hp > 60:
            #while curr_hp > 60:
                #taunt = check_taunt()
                #if taunt:
                    #print "used knock off"
                    #make_move("Knock Off")
                    #curr_hp = get_hp()
                    #print curr_hp
                #else:
                    #make_move("Taunt")
                    #curr_hp = get_hp()
                #log = get_log()
                #if curr_hp == 0 and "bot1 fainted" in log:
                    #print "Sableye fainted"
                    #break
                #taunt = check_taunt()
        #log = get_log();
        #taunt = check_taunt()
        #while "bot1 fainted" not in log:
            #if taunt:
                #make_move("Gravity")
                #log = get_log()
                #break
            #else:
                #make_move("Taunt")
                #taunt = check_taunt()
            #log = get_log()
        #time.sleep(5)
        #while "bot1 fainted" not in log:
            #taunt = check_taunt()
            #if taunt:
                #make_move("Knock Off")
            #else:
                #make_move("Taunt")
            #taunt = check_taunt()
            #curr_hp = get_hp()
            #log = get_log()
        #print "switching to diglett"
        #switch_poke("Diglett")
        #opp_poke = get_opp_poke()
        #log = get_log()
        #if opp_poke == "terrakion" or opp_poke == "bisharp" or opp_poke == "thundurus" or opp_poke == "absol-mega" or opp_poke == "lucario":
            #print "i see threat, will use earthquake"
            #while opp_poke == "terrakion" or opp_poke == "bisharp" or opp_poke == "thundurus":
                #make_move("Earthquake")
                #opp_poke = get_opp_poke()
                #log = get_log()
                #if "bot2 fainted" in log:
                    #print "Diglett fainted"
                    #break
        #if "bot2 fainted" not in log:
            #make_move("Memento")
        #print "switching to dugtrio"
        #switch_poke("Dugtrio")
        #opp_poke = get_opp_poke()
        #log = get_log()
        #if opp_poke == "terrakion" or opp_poke == "bisharp" or opp_poke == "thundurus" or opp_poke == "absol-mega":
            #print "i see threat, will use earthquake"
            #while opp_poke == "terrakion" or opp_poke == "bisharp" or opp_poke == "thundurus":
                #make_move("Earthquake")
                #opp_poke = get_opp_poke()
                #log = get_log()
                #if "bot3 fainted" in log:
                    #print "Dugtrio fainted"
                    #break
        #if "bot3 fainted" not in log:
            #make_move("Memento")
        #print "switching to smeargle"
        #sleep = 0
        #switch_poke("Smeargle")
        #if get_opp_poke() in threats:
            #print "i see threat"
            #make_move("Dark Void")
            #sleep = 1
            #log = get_log()
        #if ("Sandstorm" in get_weather() and "Excadrill" in opp_team) or ("Talonflame" in opp_team and get_opp_poke() != "talonflame"):
            #geo = 0
            #make_move("Cotton Guard")
        #else:
            #geo = 1
            #make_move("Geomancy")
        #print "using Geomancy"
        #log = get_log()
        #if "bot4 fainted" in log:
            #print "smeargle fainted darn"
            #raise FinishedException(False)
        #log = get_log()
        #if get_opp_poke() in threats and sleep != 1:
            #print "i see threat"
            #make_move("Dark Void")
            #log = get_log()
        #if geo == 1:
            #make_move("Cotton Guard")
        #else:
            #make_move("Geomancy")
        #print "using cotton guard"
        #log = get_log()
        #if "bot4 fainted" in log:
            #print "smeargle fainted darn"
            #raise FinishedException(False)
        #make_move("Baton Pass")
        #print "using baton pass"
        #log = get_log()
        #if "bot4 fainted" in log:
            #print "smeargle fainted darn"
            #raise FinishedException(False)
        #if any(x in dark_threats for x in opp_team):
            #print "hello there's a darkthreat in their team"
            #switch_poke("Clefable")
            #make_move("Substitute")
            #subcount = 0
            #while True:
                #log = get_log()
                #if "bot5 fainted" in log:
                    #print "clefable fainted darn"
                    #raise FinishedException(False)
                #sub = check_sub()
                #hp = get_hp()
                #if(sub):
                    #while(sub):
                        #subcount += 1
                        #print get_opp_poke()
                        #hp = get_hp()
                        #if get_opp_poke() not in darkpokes or get_opp_poke() == "gyarados":
                            #print "this is not a dark poke"
                            #print "my hp is " + str(hp)
                            #if hp < 50:
                                #make_move("Moonlight")
                            #else:
                                #make_move("Stored Power")
                        #else:
                            #print "this is a dark poke"
                            #print "my hp is " + str(hp)
                            #if hp < 50:
                                #make_move("Moonlight")
                            #else:
                                #make_move("Moonblast")
                        #sub = check_sub()
                #elif sub == False and hp > 50:
                    #if subcount > 0:
                        #make_move("Substitute")
                    #else:
                        #curr_opp_poke = get_opp_poke()
                        #if get_opp_poke() not in darkpokes or get_opp_poke() == "gyarados":
                            #make_move("Stored Power")
                        #else:
                            #make_move("Moonblast")
                        #if get_opp_poke() != curr_opp_poke:
                            #make_move("Substitute")
                    #subcount = 0
                #else:
                    #make_move("Moonlight")

        #else:
            #switch_poke("Espeon")
            #hp = get_hp()
            #log = get_log()
            #subcount = 0
            #make_move("Substitute")
            ##TEST LOGIC:
            #while True:
                #log = get_log()
                #if "bot6 fainted" in log:
                    #print "espeon fainted darn"
                    #raise FinishedException(False)
                #sub = check_sub()
                #hp = get_hp()
                #if(sub):
                    #while(sub):
                        #subcount += 1
                        #print get_opp_poke()
                        #hp = get_hp()
                        #if get_opp_poke() not in darkpokes or get_opp_poke() == "gyarados":
                            #print "this is not a dark poke"
                            #print "my hp is " + str(hp)
                            #if hp < 50:
                                #make_move("Morning Sun")
                            #else:
                                #make_move("Stored Power")
                        #else:
                            #print "this is a dark poke"
                            #print "my hp is " + str(hp)
                            #if hp < 50:
                                #make_move("Morning Sun")
                            #else:
                                #make_move("Hidden Power Fighting")
                        #sub = check_sub()
                #elif sub == False and hp > 50 and "Rain" not in get_weather() and "Sandstorm" not in get_weather():
                    #if subcount > 0 and get_opp_poke() != "talonflame" and check_toxic() != True:
                        #make_move("Substitute")
                    #else:
                        #curr_opp_poke = get_opp_poke()
                        #if get_opp_poke() not in darkpokes or get_opp_poke() == "gyarados":
                            #make_move("Stored Power")
                        #else:
                            #make_move("Hidden Power Fighting")
                        #if get_opp_poke() != curr_opp_poke:
                            #make_move("Substitute")
                    #subcount = 0
                #elif hp <= 50 and "Rain" not in get_weather() and "Sandstorm" not in get_weather() and get_opp_poke != "metagross-mega":
                    #make_move("Morning Sun")
                #else:
                    #if get_opp_poke() not in darkpokes or get_opp_poke() == "gyarados":
                        #make_move("Stored Power")
                    #else:
                        #make_move("Hidden Power Fighting")

#driver = webdriver.Chrome(executable_path=chromePath)
#driver.get(url)
#turn_off_sound()
#login(username, password)
##make_team(team)
##with open("asdf6000wins", "a") as f:
        ##while True:
            ##try:
                ##time.sleep(2)
                ##flinch_count = 0
                ##run(driver)
            ##except FinishedException as e:
                ##print "Actually won (or smeargle/espeon died)"
                ##won = e.won
            ##except Exception as e:
                ##print traceback.format_exc()
                ##log = get_log()
                ##if "forfeited" in log:
                    ##won = True
                ##else:
                    ##won = False
            ##chat("gg")
            ##f.write(str(won)+"\t"+driver.current_url+"\n")
            ##f.flush()
