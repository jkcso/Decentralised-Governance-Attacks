from urllib.request import Request, urlopen
import os
import ssl


def acquire_real_time_ticket_price():

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    decred_stats = 'https://explorer.dcrdata.org'
    req = Request(decred_stats, headers={'User-Agent': 'Mozilla/5.0'})
    scrap_stats = urlopen(req).read().decode("utf-8")

    start_index = scrap_stats.find('Ticket Pool Size')
    SCRAP_END_INDEX = 332
    ticket_string = scrap_stats[start_index:start_index+SCRAP_END_INDEX]
    TPB = ticket_string.find('.poolSize">')
    TPE = ticket_string.find('</span>')
    ticket_price = ticket_string[TPB:TPE]

    return int(' '.join(ticket_price[len('.poolSize">'):ticket_price.find('</span>')].splitlines()[1].split()).replace(',', ''))


p = acquire_real_time_ticket_price()
print(type(p))
