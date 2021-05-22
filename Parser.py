from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import datetime

class SingleMatchParser:
    def __init__(self, url, driver):
        self.url = url
        self.dict = None
        driver.switch_to.window(driver.current_window_handle)
        self.driver = driver
        self.score_sets = None
        self.sets_duration = None
        self.match_duration = None
        self.sets_stat = None
        self.pbp_score = None
        self.serving_idxs = None
        self.k1 = None
        self.k2 = None
        self.status = "Ended"
        
    def wait_until_cond(self, css):
        flag = 0
        while True:
            try:
                self.driver.find_element_by_css_selector(css)
                break
            except Exception:
                if (flag < 10):
                    sleep(1)
                    flag += 1
                else:
                    raise NoSuchElementException
                   
    def find_status(self):
        self.wait_until_cond("div.Cell-decync-0.fUNPnK")
        text = self.driver.find_elements_by_css_selector("div.Cell-decync-0.fUNPnK")
        if len(text) == 1:
            text = text[0].text.split()
        else:
            text = text[1].text.split()
        if "Not" in text:
            self.status = "Not started"
        if "Walkover" in text:
            self.status = "Walkover"
        if "Retired" in text:
            self.status = "Retired"
        if "Canceled" in text:
            self.status = "Canceled"
    
    def scroll_page(self):
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        pos = 0
        step = 500
        while pos < page_height:
            self.driver.execute_script("window.scrollTo(0, {p})".format(p=pos))
            sleep(0.5)
            pos += step
    
    
    def get_player_names(self):
        self.wait_until_cond("h2.styles__PageTitle-rztuto-1.dgCfTI")
        text = self.driver.find_element_by_css_selector("h2.styles__PageTitle-rztuto-1.dgCfTI").text
        assert text != '' and ' - ' in text ### CHECK
        player1, player2 = text.split(' - ')
        self.player2idx = {player1.lower(): 1, player2.lower(): 2}
        self.player1 = player1
        self.player2 = player2
    
    def get_total_score(self):
        self.wait_until_cond("div.styles__StyledResult-sc-171us6i-4.hbbalZ")
        text = self.driver.find_element_by_css_selector("div.styles__StyledResult-sc-171us6i-4.hbbalZ").text
        assert text != '' and ' - ' in text ### CHECK
        self.score1, self.score2 = text.split(' - ')
    
    def get_match_timings(self):
        self.wait_until_cond("div.Cell-decync-0.fUNPnK")
        try:
            text = self.driver.find_elements_by_css_selector("div.Cell-decync-0.fUNPnK")
            if len(text) == 1:
                text = text[0].text
            else:
                text = text[1].text
            assert text != '' and '\n' in text ### CHECK
            ### TO DO: format processing
            if "after" in text.split('\n')[1]:
                self.match_duration = text.split('\n')[1]
            self.date = text.split('\n')[0]
        except Exception:
            pass
    
    def get_sets_score(self):
        try:
            self.wait_until_cond("td.styles__Td-sc-1vgi783-5.gWZBVs")
            score = []
            for x in self.driver.find_elements_by_css_selector("td.styles__Td-sc-1vgi783-5.gWZBVs"):
                if 'm' not in x.text and x.text.split() != []:
#                     if ((("7" in x.text.split()[0] and "6" in x.text.split()[1]) or ("6" in x.text.split()[0] and "7" in x.text.split()[1]))):
#                         temp1 = x.text.split()[0][0]
#                         temp2 = x.text.split()[1][0]
#                         temp1 += ("(" + x.text.split()[0][1:] + ")")
#                         temp2 += ("(" + x.text.split()[1][1:] + ")")
#                         score.append(tuple([temp1, temp2]))
#                     else:
                    score.append(tuple([x.text.split()[0], x.text.split()[1]]))
            self.score_sets = score
        except NoSuchElementException:
            pass
    

    def get_sets_time(self):
        wait_until_cond("td.styles__Td-sc-1vgi783-5.gWZBVs")
        res = []
        try:
            for x in web.find_elements_by_css_selector("td.styles__Td-sc-1vgi783-5.gWZBVs"):
                if 'm' in x.text:
                    if 'h' in x.text:
                        time = x.text.split('m')
                        hrs = time[0].split(' ')[0][:-1]
                        mnt = time[0].split(' ')[1]
                        res.append(int(hrs) * 60 + int(mnt))
                    else:
                        time = x.text.split('m')
                        mnt = time[0]
                        res.append(int(mnt))
            self.sets_duration = res
        except NoSuchElementException:
            pass
        
    def get_pbp_info(self):
        self.wait_until_cond("div.Panel-rtew71-0.gocrVi")
        need_to_click = []
        for x in self.driver.find_elements_by_css_selector('div.PointByPointStyles__SetTitle-sc-1afd54v-0.jJUJIT'):
            need_to_click.append(x)
        for x in self.driver.find_elements_by_css_selector('div.PointByPointStyles__SetTitle-sc-1afd54v-0.ewXxWS')[1:]:
            need_to_click.append(x)
        for x in need_to_click:
            x.click()
            sleep(0.7)

        try:
            pbp_score = defaultdict(list)
            serving_idxs = dict()
            pbp_board = self.driver.find_element_by_class_name('gocrVi')
            rows_board = pbp_board.find_elements_by_xpath("*")

            def _get_single_game_serving_player(elem):
                try:
                    game_score = elem.find_element_by_class_name('dllYgZ')
                    p1, p2 = game_score.find_elements_by_xpath("*")
                    p1_class = p1.get_attribute("class").split()[-1]
                    p2_class = p2.get_attribute("class").split()[-1]
                except Exception:
                    return 1
                assert not (p1_class == p2_class == 'boODVR') ### CHECK
                if p1_class == 'boODVR': # class of serving player
                    return 0
                elif p2_class == 'boODVR':
                    return 1
                else:
                    return -1

            def _get_single_game_pbp(elem):
                game_board = elem.find_element_by_class_name('exWgBj')
                score_cols = game_board.find_elements_by_xpath("*")            
                pbp = [tuple(x.text.split('\n')) for x in score_cols]
                return pbp

            set_key = None
            pbp_within_set = []
            serving_within_set = []
            for row in rows_board:
                row_class = row.get_attribute("class").split()[-1]
                if row_class == 'ewXxWS': # game title
                    if set_key: # push previous block
                        pbp_score[set_key] = pbp_within_set[::-1]
                        serving_idxs[set_key] = serving_within_set[::-1]
                        pbp_within_set = []
                        serving_within_set = []
                    set_key = row.text
                elif row_class == 'cTCsdV': # game scores
                    pbp_single_game = _get_single_game_pbp(row)
                    serving_single_game = _get_single_game_serving_player(row)
                    pbp_within_set.append(pbp_single_game)
                    serving_within_set.append(serving_single_game)
            pbp_score[set_key] = pbp_within_set[::-1]
            serving_idxs[set_key] = serving_within_set[::-1]
            self.pbp_score, self.serving_idxs = pbp_score, serving_idxs
        except Exception:
            pass
    
    
    def get_sets_stat(self):
        try:
            block = self.driver.find_elements_by_css_selector("a.Label-sc-19k9vkh-0.bfqsCw")
            if block != []:
                stat = defaultdict(dict)
                for tab in block:
                    tab.click()
                    tab_name = tab.text
                    rows = self.driver.find_elements_by_css_selector("div.Cell-decync-0.StatisticsStyles__StatisticsItemCell-zf4n59-2.dihIaT")
                    for row in rows:
                        p1, metric, p2 = row.text.split('\n')
                        stat[tab_name][metric] = [p1, p2]
                self.sets_stat = stat
        except NoSuchElementException:
            pass
    

    def get_odds(self):
        try:
            text = self.driver.find_element_by_css_selector("div.Cell-decync-0.fUNPnK.u-mV8").text.split()
            assert text != '' and len(text) == 4 ### Check
            self.k1 = float(text[1])
            self.k2 = float(text[3])
        except NoSuchElementException:
            pass
    
    
    def get_match_info(self):
        info = dict()
        rows = self.driver.find_elements_by_css_selector("div.styles__MatchInfoRow-sc-1nav912-1.gkEvHG")
        for row in rows:
            records = row.text.split('\n')
            for rec in records:
                assert ': ' in rec ### CHECK
                k, v = rec.split(': ')
                info[k] = v
        if "Venue" in info:
            del info["Venue"]
        if "Start date" in info:
            del info["Start date"]
        self.match_info = info

    
    def parse_page(self):
        self.find_status()
        if self.status == "Not started":
            self.scroll_page()
            self.get_player_names()
            self.get_odds()
            self.get_match_info()
            self.get_match_timings()
        else:
            if (self.status != "Canceled"):
                self.scroll_page()
                self.get_player_names()
                self.get_match_timings()
                self.get_odds()
                self.get_match_info()
                if (self.status != "Walkover"):
                    self.get_sets_time()
                    self.get_sets_score()
                    self.get_pbp_info()
                    self.get_sets_stat()
        
    def as_dict(self):
        self.parse_page()
        if self.status != "Canceled":
            self.dict = {
                'match_url': self.url, 
                'player1': self.player1, 
                'player2': self.player2,
                'status': self.status,
                'match_info': self.match_info,
                'date': self.date,
                'match_duration': self.match_duration,
                'score_sets': self.score_sets,
                'sets_duration': self.sets_duration,
                'sets_stat': self.sets_stat,
                'score_pbp': self.pbp_score,
                'serving_idxs': self.serving_idxs,
                'k1': self.k1,
                'k2': self.k2,
            }
        return self.dict


def wait_until_cond(css):
        flag = 0
        while True:
            try:
                web.find_element_by_css_selector(css)
                break
            except Exception:
                if (flag < 10):
                    sleep(1)
                    flag += 1
                else:
                    raise NoSuchElementException

## Функция нахождения css ссылок для нажатия на матч
def find_css_urls():
    css_urls = web.find_elements_by_css_selector("a.EventCellstyles__Link-sc-1m83enb-0.dhKVQJ")
    return css_urls

## Преход на страницу матча
def go_to_match():
    wait_until_cond("a.styles__EventLink-d389b-0.dqBRye")
    elem = web.find_element_by_css_selector("a.styles__EventLink-d389b-0.dqBRye")
    elem.click()

## Поиск лузера    
def set_loser(loser_name, match): 
    wait_until_cond("div.Content-sc-1o55eay-0.EventCellstyles__WinIndicator-ni00fg-4.kCvfzg")
    if loser_name == match["player1"]:
        match["player1_win"] = 0
    else:
        match["player1_win"] = 1
    
## Открытие вкладки справа    
def open_tab(css_urls, parsed):
    flag, css, match_url = 0, "", ""
    for css in css_urls:
        match_url = css.get_attribute("href")
        if match_url not in parsed:
            parsed.append(match_url)
            css.click()
            flag = 1
            break
    return [flag, css, match_url]


def is_single():
#     wait_until_cond("a.styles__EventLink-d389b-0.koniBB")
    text = web.find_element_by_css_selector("div.styles__WidgetHeader-d389b-1.jiWJIS").text
    assert text != '' ### CHECK
    if ("Doubles" in text) or ("Mixed" in text) or ("." not in text):
        return 0
    return 1
        
## Скроллим для прогрузки матчей    
def scroll_page(pos):
    t = 0
    while t < pos + 300:
        web.execute_script("window.scrollTo(0, {p})".format(p=t))
        t += 400
        sleep(0.5)
    sleep(0.5)
    
def find_stage():
    el = web.find_element_by_css_selector("ul.BreadcrumbContent__Content-ciuw58-0.styles__WidgetBreadcrumb-d389b-5.ghJOmO")
    return el.text.split()[-1]

## Поиск раунда
def set_stage(stage, match):
    match["round"] = stage
    
## Добавление ссылок    
def add_hrefs(hrefs):
    elements = web.find_elements_by_css_selector("div.styles__TeamSectionMain-sc-171us6i-1.eIMsEV a")
    player1 = elements[-2].get_attribute("href")
    player2 = elements[-1].get_attribute("href")
    hrefs.add(player1)
    hrefs.add(player2)
        
## Парсим страницу определенной даты
def parse_date(date, matches, hrefs):
    web.switch_to.window(web.current_window_handle)
    pos = 0
    parsed = []
    page_height = web.execute_script("return document.body.scrollHeight") ## Высота страницы
    url = "https://www.sofascore.com/tennis/atp/" + date  ## Страница с матчами
    web.get(url)
    web.execute_script("window.scrollTo(0, {p})".format(p=0)) ## Переход в начало страницы
    while True:
        sleep(0.7)
        css_urls = find_css_urls()
        sleep(0.5)
        flag, css, match_url = open_tab(css_urls, parsed)
        if flag == 1:
            sleep(0.7) ## Sleep без которого не работают следующие 2 строки
            if is_single():
                add_hrefs(hrefs)
                stage = find_stage()
                loser_name = css.find_element_by_css_selector("div.Content-sc-1o55eay-0.EventCellstyles__WinIndicator-ni00fg-4.kCvfzg").text ## Поиск лузера            
                go_to_match()
                sleep(0.7) ## Sleep без которого не успевает прогрузиться страница для корректного скроллинга
                match = SingleMatchParser(match_url, web).as_dict() ## Парсинг страницы матча -> match
                web.get(url) ## Возврат на основную страницу парсинга
                sleep(0.7)
                if match != None:
                    set_loser(loser_name, match)
                    set_stage(stage, match)
                    matches.append(match)
            pos += 50
            scroll_page(pos)  
            flag = 0
        else:
            break  ## Выход из парсинга страницы, когда не осталось новых ссылок в css_urls
    print("Parsed matches on date: {d}".format(d = date), len(parsed))


## Парсинг по датам, вернет matches - массив матчей, hrefs - сет ссылок игроков
def parse(startdate, enddate, matches, hrefs, path):
    global web
    web = webdriver.Chrome(path)
    while startdate != enddate:
        parse_date(str(startdate), matches, hrefs) 
        startdate += datetime.timedelta(1)


