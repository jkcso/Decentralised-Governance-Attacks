from urllib.request import Request, urlopen
import os
import ssl


def new_mn_rt():

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    mn_stats = 'https://masternodes.online/currencies/DASH'
    req_stats = Request(mn_stats, headers={'User-Agent': 'Mozilla/5.0'})
    scraped_stats = urlopen(req_stats).read().decode("utf-8")

    start_index = scraped_stats.find('Active masternodes')
    scraped_end_index = 45
    mn_string = scraped_stats[start_index:start_index+scraped_end_index]
    mn_string_begin = mn_string.find('<td>')
    mn_real_time_total = mn_string[mn_string_begin+4:-1]

    return int(mn_real_time_total.replace(',', ''))

# x
def reward():

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    mn_block_rew_stats = 'https://bitinfocharts.com/dash/'
    req_stats = Request(mn_block_rew_stats, headers={'User-Agent': 'Mozilla/5.0'})
    scraped_stats = urlopen(req_stats).read().decode("utf-8")

    start_index = scraped_stats.find('block reward')
    scraped_end_index = 18
    mn_string = scraped_stats[start_index:start_index+scraped_end_index]
    mn_block_string_begin = mn_string.find('">')
    mn_block_rew_string = mn_string[mn_block_string_begin+2:]

    return float(mn_block_rew_string)


p = reward()
print(p)
print(type(p))
