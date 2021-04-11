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

logging.basicConfig(filename='SNKRSlog.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.DEBUG)

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
