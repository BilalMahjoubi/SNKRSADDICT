import requests as rq
import json
import time
import datetime
import urllib3
import logging
import dotenv
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, HardwareType
from fp.fp import FreeProxy
from selenium import webdriver

logging.basicConfig(filename='SNKRSlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s',
                    level=logging.DEBUG)

software_names = [SoftwareName.CHROME.value]
hardware_type = [HardwareType.MOBILE__PHONE]
user_agent_rotator = UserAgent(software_names=software_names, hardware_type=hardware_type)
CONFIG = dotenv.dotenv_values()

proxyObject = FreeProxy(country_id=['FR'], rand=True)

INSTOCK = []


def scrape_site(headers, proxy):
    """
    Scrapes SNKRS site and adds items to array
    :return: None
    """
    items = []
    anchor = 0
    while anchor < 180:
        url = f'https://api.nike.com/product_feed/threads/v2/?anchor={anchor}&count=60&filter=marketplace%28{CONFIG["LOCATION"]}%29&filter=language%28{CONFIG["LANGUAGE"]}%29&filter=channelId%28010794e5-35fe-4e32-aaff-cd2c74f89d61%29&filter=exclusiveAccess%28true%2Cfalse%29&fields=active%2Cid%2ClastFetchTime%2CproductInfo%2CpublishedContent.nodes%2CpublishedContent.subType%2CpublishedContent.properties.coverCard%2CpublishedContent.properties.productCard%2CpublishedContent.properties.products%2CpublishedContent.properties.publish.collections%2CpublishedContent.properties.relatedThreads%2CpublishedContent.properties.seo%2CpublishedContent.properties.threadType%2CpublishedContent.properties.custom%2CpublishedContent.properties.title'
        try:
            html = rq.get(url=url, timeout=20, verify=False, headers=headers, proxies=proxy)
            output = json.loads(html.text)
            for item in output['objects']:
                items.append(item)
                logging.info(msg='Successfully scraped SNKRS site')
        except Exception as e:
            print('Error - ', e)
            logging.error(msg=e)
        anchor += 60
        time.sleep(float(CONFIG['DELAY']))
    return items


def checker(product, colour):
    """
    Determines whether the product status has changed
    :param product: Shoe name
    :param colour: Shoe colour
    :return: None
    """
    for item in INSTOCK:
        if item == [product, colour]:
            return True
    return False


def discord_webhook(title, colour, slug, thumbnail):
    """
    Sends a Discord webhook notification to the specified webhook URL
    :param title: Shoe name
    :param colour: Shoe Colour
    :param slug: Shoe URL
    :param thumbnail: URL to shoe image
    :return: None
    """
    data = {}
    data["username"] = CONFIG['USERNAME']
    data["avatar_url"] = CONFIG['AVATAR_URL']
    data["embeds"] = []
    embed = {}
    if title != '' and colour != '' and slug != '':
        embed["title"] = title
        embed["fields"] = [{'name': 'Colour', 'value': colour}]
        embed["url"] = 'https://www.nike.com/gb/launch/t/' + slug
        embed["thumbnail"] = {'url': thumbnail}
    else:
        embed["description"] = "Bonjour"
    embed["color"] = int(CONFIG['COLOUR'])
    embed["footer"] = {'text': 'SNKRS ADDICT'}
    embed["timestamp"] = str(datetime.datetime.utcnow())
    data["embeds"].append(embed)

    result = rq.post(CONFIG['WEBHOOK'], data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except rq.exceptions.HTTPError as err:
        logging.error(msg=err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))
        logging.info(msg="Payload delivered successfully, code {}.".format(result.status_code))


def remove_duplicates(mylist):
    """
    Removes duplicate values from a list
    :param mylist: list
    :return: list
    """
    return [list(t) for t in set(tuple(element) for element in mylist)]


def comparitor(j, start):
    if checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
        pass
    else:
        INSTOCK.append([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
        if start == 0:
            print('Sending notification to Discord...')
            discord_webhook(j['merchProduct']['labelName'], j['productContent']['colorDescription'],
                            j['productContent']['slug'], j['imageUrls']['productImageUrl'])
            logging.info(msg='Sending new notification')


def monitor():
    """
    Initiates the monitor
    :return: None
    """

    print('STARTING MONITOR')
    logging.info(msg='Successfully started monitor')
    discord_webhook(title='', slug='', colour='', thumbnail='')
    start = 1
    proxy_no = 0

    proxy_list = CONFIG['PROXY'].split('%')
    proxy = {"http": f"http://{proxyObject.get()}"} if proxy_list[0] == "" else proxy_list[proxy_no]
    headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
    keywords = CONFIG['KEYWORDS'].split('%')
    while True:
        items = scrape_site(proxy, headers)
        for item in items:
            try:
                for j in item['productInfo']:
                    if j['availability']['available'] == True and j['merchProduct']['status'] == 'ACTIVE':
                        check = False
                        if keywords == "":
                            comparitor(j, start)
                        else:
                            for key in keywords:
                                if key.lower() in j['merchProduct']['labelName'].lower() or key.lower() in \
                                        j['productContent']['colorDescription'].lower():
                                    check = True
                                    break
                            if check:
                                comparitor(j, start)
                    else:
                        if checker(j['merchProduct']['labelName'], j['productContent']['colorDescription']):
                            INSTOCK.remove([j['merchProduct']['labelName'], j['productContent']['colorDescription']])
            except rq.exceptions.HTTPError as e:
                logging.error(e)
                headers = {'User-Agent': user_agent_rotator.get_random_user_agent()}
                if CONFIG['PROXY'] == "":
                    proxy = {"http": f"http://{proxyObject.get()}"}
                else:
                    proxy_no = 0 if proxy_no == (len(proxy_list) - 1) else proxy_no + 1
                    proxy = proxy_list[proxy_no]
            except Exception as e:
                logging.error(e)
        start = 0


def login(mail, mdp):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" #readMe
    chrome_driver_binary = "/Users/gabrieldray/Downloads/chromedriver" #readMe
    chrome = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

    list_page = ["https://www.nike.com/login", "https://www.courir.com/on/demandware.store/Sites-Courir-FR-Site/fr_FR/Login-Show"]
    for webpage in list_page:

        chrome.get(webpage)

        dico_form = {"courir": "login-form clearfix", "nike": "nike-unite-form"}  # id pour stockx

        start = webpage.find("www.") + len("www.")
        end = webpage.find(".com")
        site_name = webpage[start:end]
        print(site_name)

        xpath_input = f"""//form[@class="{dico_form.get(site_name)}"]//input"""
        xpath_button = f"""//form[@class="{dico_form.get(site_name)}"]//button"""

        _inputs = chrome.find_elements_by_xpath(xpath_input)
        _buttons = chrome.find_elements_by_xpath(xpath_button)

        list_name_attribute = []

        for inpt in _inputs:
            if (inpt.get_attribute('type') != "hidden"):
                list_name_attribute.append(inpt.get_attribute('id'))

        print(list_name_attribute)

        chrome.find_element_by_id(list_name_attribute[0]).send_keys(mail)
        chrome.find_element_by_id(list_name_attribute[1]).send_keys(mdp)
        # chrome.find_element_by_xpath(xpath_button).click()

        # return list_name_attribute


if __name__ == '__main__':

    file = open("user.csv", "r")
    user = []
    for line in file:
        s = line.strip()
        line_list = s.split(";")
        user.append(line_list)
    file.close()

    print(user[0][0])
    print(user[0][2])

    login(user[0][0], user[0][2])
    urllib3.disable_warnings()
    monitor()
