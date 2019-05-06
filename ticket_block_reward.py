from urllib.request import Request, urlopen
import os
import ssl


def acquire_real_time_ticket_reward():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    decred_stats = 'https://explorer.dcrdata.org'
    req = Request(decred_stats, headers={'User-Agent': 'Mozilla/5.0'})
    scrap_stats = urlopen(req).read().decode("utf-8")

    start_index = scrap_stats.find('PoW Reward')
    SCRAP_END_INDEX = 290
    ticket_string = scrap_stats[start_index:start_index + SCRAP_END_INDEX]
    TPB = ticket_string.find('int">')
    TPE = ticket_string.find('</sp')
    # since this is PoW reward which is 60% of the total reward, then the vote reward which is
    # 30% is going to be half of it.
    pow_reward = ticket_string[TPB + len('int">'):TPE]
    ticket_reward = float('{0:.2f}'.format(float(pow_reward) / 2))

    global IS_TICKET_REWARD_REAL
    IS_TICKET_REWARD_REAL = True

    return ticket_reward


br = acquire_real_time_ticket_reward()
print(br)
