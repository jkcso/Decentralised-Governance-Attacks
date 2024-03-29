from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from urllib.request import Request, urlopen
import csv
import json
import os
import ssl
import math
import pdfkit

# Global variables are defined here once for clarity and duplication-free coding.
# Maximum number of tickets in Decred ticket_pool_size, in reality it is not restrictive.
MAX_TICKETS = 40960
EXPIRED_TICKETS_PER_BLOCK = 5
BIDDABLE_TICKETS_PER_BLOCK = 20
BLOCKS_PER_DAY = 288
BIDDABLE_TICKETS_PER_DAY = BLOCKS_PER_DAY * BIDDABLE_TICKETS_PER_BLOCK
MIN_NEW_POOL_TICKETS_PER_DAY = BLOCKS_PER_DAY * EXPIRED_TICKETS_PER_BLOCK
DASH_MN_COLLATERAL = 1000
MIN_COINBASE_RANKING = MIN_EXP = ONE_TICKET = 1
MAX_COINBASE_RANKING = 60
COINBASE_API_KEY = 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
MIN_PRICE = MIN_CIRCULATION = MIN_BUDGET = MIN_POOL_SIZE = MIN_CONTROL = MIN_TARGET = 0
# Output Start, used mostly for long floats, strings and percentages.
OS = 0
# Output End.
OE = 4
AVG_DAYS_FOR_REWARD = 28
ONE_DAY = 1
ONE_MONTH = 30.34
ONE_YEAR = 365
PERCENTAGE = 100
# 60% is net majority, however with 40.1% of votes against the proposal will not go through.
MIN_REJECTION = 0.401
DOUBLE = 2
ONE_DAY = 1
MAX_SUPPLY = 21000000
MIN_QUORUM_PERCENTAGE = 0.1
INVERSE = -1
# Defaults to 5 out of 10 from the exponential scale of how slow or aggressive inflation will be.
DEF_EXP = -9.5
DEF_INFLATION = math.pow(math.e, DEF_EXP)
MAX_EXP = 11
SANITISE = 5
SIXTY_PERCENT = 0.6
IS_COIN_PRICE_REAL = IS_CIRCULATION_REAL = IS_TICKET_PRICE_REAL = IS_TICKET_POOL_REAL = False
ADAPTOR = 2
DEF_FILENAME = 'decred-default'
RT = '(real time value)'
UD = '(user defined value)'
DEF = '(default exponential)'
# New line character for html.
NL = '<br>'
# Global variable to hold the current state of pdf report; to be edited along the way.
PDF_REPORT = ''
PDF_REPORT_HEADER = '''
<html>
<head></head>
<body><p>
'''
PDF_REPORT_INTRO = '''
REPORT FOR DECRED DECENTRALISED GOVERNANCE ATTACK SIMULATOR<br><br>
'''
PDF_REPORT_FOOTER = '''
</p></body>
</html>
'''

# The dictionary that then becomes the .csv file for Kibana
# initially has some global variables useful for the dashboard.
kibana_dict = {'Collateral': DASH_MN_COLLATERAL,
               'MaxSupply': MAX_SUPPLY}


# Real time ticket prices from Decred open source information.
def acquire_real_time_ticket_price():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    decred_stats = 'https://explorer.dcrdata.org'
    req = Request(decred_stats, headers={'User-Agent': 'Mozilla/5.0'})
    scrap_stats = urlopen(req).read().decode("utf-8")

    start_index = scrap_stats.find('Ticket Price')
    SCRAP_END_INDEX = 332
    ticket_string = scrap_stats[start_index:start_index + SCRAP_END_INDEX]
    TPB = ticket_string.find('int">')
    TPE = ticket_string.find('</span>')
    ticket_price = ticket_string[TPB:TPE]

    global IS_TICKET_PRICE_REAL
    IS_TICKET_PRICE_REAL = True
    return float(ticket_price[len('int">'):ticket_price.find('</span')])


# Real time ticket pool size from Decred open source information.
def acquire_real_time_ticket_pool_size():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    decred_stats = 'https://explorer.dcrdata.org'
    req = Request(decred_stats, headers={'User-Agent': 'Mozilla/5.0'})
    scrap_stats = urlopen(req).read().decode("utf-8")

    start_index = scrap_stats.find('Ticket Pool Size')
    SCRAP_END_INDEX = 332
    ticket_string = scrap_stats[start_index:start_index + SCRAP_END_INDEX]
    TPB = ticket_string.find('.poolSize">')
    TPE = ticket_string.find('</span>')
    ticket_price = ticket_string[TPB:TPE]

    global IS_TICKET_POOL_REAL
    IS_TICKET_POOL_REAL = True
    return int(' '.join(ticket_price[len('.poolSize">'):ticket_price.find('</span>')].splitlines()[1].split()).
               replace(',', ''))


# Real time ticket reward from Decred open source information.
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


# Real time coin price from Decred open source information.
def acquire_real_time_price():
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            'start': str(MIN_COINBASE_RANKING),
            'limit': str(MAX_COINBASE_RANKING),
            'convert': 'GBP'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINBASE_API_KEY
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)

            real_time_price = MIN_PRICE

            for i in range(MIN_COINBASE_RANKING, MAX_COINBASE_RANKING):
                if data['data'][i]['name'] == 'Decred':
                    real_time_price = data['data'][i]['quote']['GBP']['price']

            global IS_COIN_PRICE_REAL
            IS_COIN_PRICE_REAL = True
            return float('{0:.2f}'.format(real_time_price))

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


# Real time circulation from Decred open source information.
def acquire_real_time_circulation():
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            'start': str(MIN_COINBASE_RANKING),
            'limit': str(MAX_COINBASE_RANKING),
            'convert': 'GBP'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': COINBASE_API_KEY
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)

            real_time_circulation = MIN_CIRCULATION

            for i in range(MIN_COINBASE_RANKING, MAX_COINBASE_RANKING):
                if data['data'][i]['name'] == 'Decred':
                    real_time_circulation = data['data'][i]['circulating_supply']

            global IS_CIRCULATION_REAL
            IS_CIRCULATION_REAL = True
            return int(real_time_circulation)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


# Creates a .csv file to be input to Kibana for visualisation.
def create_csv(filename):
    with open(filename + '.csv', 'w') as f:
        w = csv.DictWriter(f, kibana_dict.keys())
        w.writeheader()
        w.writerow(kibana_dict)


# Creates a comprehensive .pdf report.
def create_pdf(filename):
    global PDF_REPORT
    PDF_REPORT += PDF_REPORT_FOOTER
    html_file = filename + '.html'
    f = open(html_file, 'w')
    f.write(PDF_REPORT)
    f.close()
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'quiet': ''
    }
    pdf_file = filename + '.pdf'
    pdfkit.from_file(html_file, pdf_file, options=options)


# Outputs the values we proceed during the simulation.
def attack_phase_1(filename, budget, coin_price, ticket_price, exp_incr, coins, ticket_pool_size, tickets_controlled,
                   tickets_target, ticket_reward):
    global PDF_REPORT
    PDF_REPORT += PDF_REPORT_HEADER
    PDF_REPORT += PDF_REPORT_INTRO

    print('\n')
    s1 = 'FILES TO BE GENERATED'
    print(s1, '\n')
    PDF_REPORT += s1 + NL + NL

    print(filename + '.csv,', filename + '.html,', filename + '.pdf', '\n', '\n')
    PDF_REPORT += filename + '.csv, ' + filename + '.html, ' + filename + '.pdf' + NL + NL

    s2 = 'VALUES PROCEEDING WITH'
    print(s2, '\n')
    PDF_REPORT += s2 + NL + NL

    s3 = 'Attack budget (£): unspecified (cost estimated in attack phase two)'
    s4 = 'Attack budget (£):'
    s5 = 'Decred price (£):'
    s26 = 'Decred ticket price (in DCR):'
    s6 = 'Inflation rate:'
    s7 = 'Coins in circulation:'
    s8 = 'Ticket pool size:'
    s9 = 'Tickets already under control or bribe:'

    print(s3) if budget == MIN_BUDGET else print(s4, budget, UD)
    PDF_REPORT += s3 + NL if budget == MIN_BUDGET else s4 + ' ' + str(budget) + ' ' + UD + NL

    print(s5, coin_price, RT if IS_COIN_PRICE_REAL else UD)
    PDF_REPORT += s5 + ' ' + str(coin_price) + ' ' + RT + NL \
        if IS_COIN_PRICE_REAL \
        else s5 + ' ' + str(coin_price) + ' ' + UD + NL

    print(s26, ticket_price, RT if IS_TICKET_PRICE_REAL else UD)
    PDF_REPORT += s26 + ' ' + str(ticket_price) + ' ' + RT + NL \
        if IS_TICKET_PRICE_REAL \
        else s26 + ' ' + str(ticket_price) + ' ' + UD + NL

    print(s6, str(exp_incr)[OS:OE], DEF if exp_incr == DEF_INFLATION else UD)
    PDF_REPORT += s6 + ' ' + str(exp_incr)[OS:OE] + ' ' + DEF + NL \
        if exp_incr == DEF_INFLATION \
        else s6 + ' ' + str(exp_incr)[OS:OE] + ' ' + UD + NL

    print(s7, coins, RT if IS_CIRCULATION_REAL else UD)
    PDF_REPORT += s7 + ' ' + str(coins) + ' ' + RT + NL \
        if IS_CIRCULATION_REAL \
        else s7 + ' ' + str(coins) + ' ' + UD + NL

    print(s8, ticket_pool_size, RT if IS_TICKET_POOL_REAL else UD)
    PDF_REPORT += s8 + ' ' + str(ticket_pool_size) + ' ' + RT + NL \
        if IS_TICKET_POOL_REAL \
        else s8 + ' ' + str(ticket_pool_size) + ' ' + UD + NL

    print(s9, tickets_controlled)
    PDF_REPORT += s9 + ' ' + str(tickets_controlled) + NL

    cost = float(MIN_PRICE)
    new_coin_price = coin_price
    new_ticket_price = ticket_price
    budget_tickets = MIN_BUDGET

    malicious_60 = int(math.ceil(ticket_pool_size * SIXTY_PERCENT))
    kibana_dict.update({'MaliciousNet': malicious_60})

    # If budget is set, exchange it from GBP to Decred and perform inflation estimation for the new price and cost.
    if budget > MIN_BUDGET:
        # Amount of decred exchanged from budget.
        budget_to_decred = math.floor(budget / coin_price)
        budget_tickets = math.floor(budget_to_decred / ticket_price)
        # Even if budget is much more, it should be capped to purchase just enough to stay stealthy and save money.
        budget_tickets = budget_tickets if budget_tickets <= malicious_60 else malicious_60

        for i in range(MIN_PRICE, budget_tickets):
            new_coin_price += exp_incr
            new_ticket_price += exp_incr

        new_coin_price = float('{0:.2f}'.format(new_coin_price))
        new_ticket_price = float('{0:.2f}'.format(new_ticket_price))

        # The global value of adaptor is used towards the median new coin price which is necessary for the inclusion
        # of both low and high coin values for when inflated. The initial form (commented) of cost prediction without
        # optimisation would be the following which is however over estimated due to only using the new coin price:
        cost = float('{0:.3f}'.format(
            budget_tickets * ticket_price * (coin_price + (
                    budget_to_decred / (budget_to_decred - budget_to_decred / ADAPTOR) * exp_incr))))

    # When budget is set, the number of tickets to acquire should correspond to the budget but also
    # when both budget and a target number of mn is set, then the budget is what matters in estimation.
    if budget > MIN_BUDGET and tickets_target >= MIN_TARGET:
        tickets_target = budget_tickets
        s10 = 'Target total tickets:'
        s11 = '(capped due to budget)'
        print(s10, tickets_target, s11)
        PDF_REPORT += s10 + ' ' + str(tickets_target) + ' ' + s11 + NL

    # When user provides budget and already controlled tickets, the target should be based on budget and the following
    # operation is there to erase the subtraction specifying that tickets to buy are those not already controlled.
    if budget > MIN_BUDGET and tickets_target == budget_tickets and tickets_controlled > MIN_CONTROL:
        tickets_target += tickets_controlled
        s12 = 'Total tickets including already controlled or bribed:'
        print(s12, tickets_target)
        PDF_REPORT += s12 + ' ' + str(tickets_target) + NL

    # When the budget is not set but a target number of tickets is provided.
    elif budget == MIN_BUDGET and tickets_target > MIN_TARGET:
        tickets_target = tickets_target if tickets_target <= MAX_TICKETS else MAX_TICKETS
        s13 = 'Target total tickets:'
        print(s13, tickets_target, UD)
        PDF_REPORT += s13 + ' ' + str(tickets_target) + ' ' + UD + NL

    # When neither budget nor ticket target is set, the metric defaults to a malicious 60% of ticket pool size.
    elif budget == MIN_BUDGET and tickets_target == MIN_TARGET:
        tickets_target = malicious_60
        s14 = 'Target total tickets: unspecified (defaults to 60% over honest tickets)'
        print(s14)
        PDF_REPORT += s14 + NL

    # Based on the above conditions, the number of masternodes to purchase is determined here.
    num_tickets_for_attack = tickets_target - tickets_controlled

    s29 = 'Ticket reward per block:'
    print(s29, ticket_reward)
    PDF_REPORT += s29 + ' ' + str(ticket_reward) + NL

    s15 = 'ATTACK PHASE ONE: PRE-PURCHASE ANALYSIS'
    print('\n')
    print(s15, '\n')
    PDF_REPORT += NL
    PDF_REPORT += s15 + NL + NL

    s16 = 'Ticket pool size before purchase:'
    s17 = 'Tickets required for malicious 60% over honest tickets:'
    print(s16, ticket_pool_size)
    print(s17, malicious_60)
    PDF_REPORT += s16 + ' ' + str(ticket_pool_size) + NL
    PDF_REPORT += s17 + ' ' + str(malicious_60) + NL

    # Budget defaults to malicious net 10%.
    if budget == MIN_BUDGET and tickets_target == MIN_TARGET:
        s18 = 'Attack budget: cost of purchase 60% of ticket pool size'
        print(s18)
        PDF_REPORT += s18 + NL

    # Budget is set but target dominates.
    elif budget > MIN_BUDGET and tickets_target > MIN_TARGET:
        print('Attack budget (£):', budget, '(enough to acquire', budget_tickets,
              'tickets)' if budget_tickets > ONE_TICKET else 'ticket)')
        PDF_REPORT += 'Attack budget (£): ' + str(budget) + ' (enough to acquire ' + str(budget_tickets) + \
                      ' tickets)' + NL \
            if budget_tickets > ONE_TICKET \
            else 'Attack budget (£): ' + str(budget) + ' (enough to acquire ' + str(budget_tickets) + ' ticket)' + NL

        # Even if the budget is enough to acquire much more of what is needed to be successful, cap it to just enough
        # to save budget.
        if budget_tickets >= malicious_60:
            budget_tickets = malicious_60
            tickets_target = budget_tickets
            num_tickets_for_attack = tickets_target - tickets_controlled

    # Budget is not set so we accommodate the target.
    elif budget == MIN_BUDGET and tickets_target > MIN_TARGET:
        print('Attack budget (£): cost of realise target of', tickets_target,
              'tickets' if tickets_target > ONE_TICKET else 'ticket')
        PDF_REPORT += 'Attack budget (£): cost of realise target of ' + str(tickets_target) + ' tickets' + NL \
            if tickets_target > ONE_TICKET \
            else 'Attack budget (£): cost of realise target of ' + str(tickets_target) + ' ticket' + NL

    print('Therefore, target total tickets:', tickets_target if budget == MIN_BUDGET else budget_tickets)
    PDF_REPORT += 'Therefore, target total tickets: ' + str(tickets_target) + NL \
        if budget == MIN_BUDGET \
        else 'Therefore, target total tickets: ' + str(budget_tickets) + NL

    s19 = 'Excluding tickets already under control or bribe, total:'
    print(s19, tickets_controlled)
    PDF_REPORT += s19 + ' ' + str(tickets_controlled) + NL

    s20 = 'Finalised total of tickets to acquire:'
    print(s20, num_tickets_for_attack)
    PDF_REPORT += s20 + ' ' + str(num_tickets_for_attack) + NL + NL

    frozen_coins = int(ticket_price * ticket_pool_size)
    unfrozen_coins = int(coins - frozen_coins)
    new_frozen_needed_for_sixty_percent = int((ticket_pool_size * SIXTY_PERCENT) * ticket_price)
    # Check limitations on whether unfrozen coins are enough to bid on new openings for tickets.
    possible_tickets = MAX_TICKETS \
        if new_frozen_needed_for_sixty_percent <= (unfrozen_coins + MIN_NEW_POOL_TICKETS_PER_DAY) \
        else math.floor(unfrozen_coins // ticket_price)

    kibana_dict.update({'ExpiredPerBlock': EXPIRED_TICKETS_PER_BLOCK,
                        'BiddablePerBlock': BIDDABLE_TICKETS_PER_BLOCK,
                        'BlocksPerDay': BLOCKS_PER_DAY,
                        'NewOpeningsPerDay': MIN_NEW_POOL_TICKETS_PER_DAY,
                        'BiddablePerDay': BIDDABLE_TICKETS_PER_DAY,
                        'FrozenBef': frozen_coins,
                        'PurchaseBef': num_tickets_for_attack,
                        # Placeholder for a potential unsuccessful first purchase attempt.
                        'PurchaseAft': MIN_TARGET})

    s21 = 'Coins in circulation before purchase:'
    s22 = 'From which coins frozen for tickets:'
    s23 = 'Therefore, coins remaining available to acquire and freeze:'
    s24 = 'These are enough for this number of tickets:'
    s29 = 'While this attack will proceed with purchasing:'
    s27 = 'However, this amount is high to be purchased straight away'
    s28 = 'as there exist constraints in tickets supply analysed below.'

    print()
    print(s21, coins)
    print(s22, frozen_coins)
    print(s23, unfrozen_coins)
    print(s24, possible_tickets)
    print(s29, num_tickets_for_attack)
    if num_tickets_for_attack > DOUBLE * MIN_NEW_POOL_TICKETS_PER_DAY:
        print(s27)
        print(s28)

    PDF_REPORT += s21 + ' ' + str(coins) + NL
    PDF_REPORT += s22 + ' ' + str(frozen_coins) + NL
    PDF_REPORT += s23 + ' ' + str(unfrozen_coins) + NL
    PDF_REPORT += s24 + ' ' + str(possible_tickets) + NL
    PDF_REPORT += s29 + ' ' + str(num_tickets_for_attack) + NL
    if num_tickets_for_attack > DOUBLE * MIN_NEW_POOL_TICKETS_PER_DAY:
        PDF_REPORT += s27 + ' ' + s28 + NL

    # Calls the following method to proceed in attempting the purchase.
    attack_phase_2(budget, coin_price, ticket_price, exp_incr, coins, ticket_pool_size, tickets_controlled,
                   num_tickets_for_attack, cost, new_coin_price, new_ticket_price, malicious_60, ticket_reward)


def attack_phase_2(budget, coin_price, ticket_price, exp_incr, coins, ticket_pool_size, tickets_controlled,
                   num_tickets_for_attack, cost, new_coin_price, new_ticket_price, malicious_60, ticket_reward):

    global PDF_REPORT

    # When budget is not set it means that what is required is to a dynamic cost for purchasing decred to freeze it.
    if budget == MIN_BUDGET:
        cost = float(MIN_PRICE)
        new_coin_price = coin_price
        new_ticket_price = ticket_price

        for i in range(MIN_PRICE, num_tickets_for_attack):
            new_coin_price += exp_incr
            new_ticket_price += exp_incr
            one_ticket_cost_in_pounds = new_coin_price * new_ticket_price
            cost += one_ticket_cost_in_pounds

        cost = float("{0:.3f}".format(cost))
        new_coin_price = float("{0:.2f}".format(new_coin_price))
        new_ticket_price = float("{0:.2f}".format(new_ticket_price))

    new_num_frozen = int(ticket_pool_size * new_ticket_price)
    new_remaining = coins - new_num_frozen
    new_num_tickets = ticket_pool_size + num_tickets_for_attack \
        if ticket_pool_size + num_tickets_for_attack < MAX_TICKETS \
        else MAX_TICKETS
    new_possible_tickets = int(MAX_TICKETS - new_num_tickets) \
        if int(MAX_TICKETS - new_num_tickets) < MAX_TICKETS \
        else MIN_CONTROL
    total_malicious = num_tickets_for_attack + tickets_controlled
    percentage_malicious = str(float((total_malicious / ticket_pool_size) * PERCENTAGE))[OS:OE]

    kibana_dict.update({'Cost': cost,
                        'CoinPriceAft': new_coin_price,
                        'TicketPriceAft': new_ticket_price,
                        'FrozenAft': new_num_frozen,
                        # Possible tickets based on remaining pool.
                        'PossibleAft': new_possible_tickets,
                        # New total masternodes including both honest and malicious.
                        'ActiveAft': new_num_tickets,
                        # Total malicious masternodes.
                        'Malicious': total_malicious})

    # Attempts to purchase initial required amount no matter if impossible as this number is later capped to possible.
    s26 = 'ATTACK PHASE TWO: EXECUTION'
    print('\n')
    print(s26, '\n')
    PDF_REPORT += NL + s26 + NL + NL

    print('PURCHASE ATTEMPT FOR', num_tickets_for_attack,
          'TICKETS' if num_tickets_for_attack > ONE_TICKET else 'TICKET', '\n')
    PDF_REPORT += 'PURCHASE ATTEMPT FOR ' + str(num_tickets_for_attack) + ' TICKETS' + NL + NL \
        if num_tickets_for_attack > ONE_TICKET \
        else 'PURCHASE ATTEMPT FOR ' + str(num_tickets_for_attack) + ' TICKET' + NL + NL

    min_days_to_purchase_tickets = math.ceil(num_tickets_for_attack // MIN_NEW_POOL_TICKETS_PER_DAY)
    # Even if just some hours would be required to purchase the amount of tickets targeted, or even 5 minutes,
    # in reality what is needed is a whole day so that tickets can 'mature' by leaving the initial pool of
    # immature tickets to join the normal one.
    if min_days_to_purchase_tickets < ONE_DAY:
        min_days_to_purchase_tickets = ONE_DAY
    attack_overhead_in_days = str(min_days_to_purchase_tickets) + ' DAYS' \
        if min_days_to_purchase_tickets > ONE_DAY \
        else str(min_days_to_purchase_tickets) + ' DAY'

    s27 = 'PURCHASE OVERHEAD ESTIMATION:'
    print(s27, attack_overhead_in_days, '\n')
    PDF_REPORT += s27 + ' ' + attack_overhead_in_days + NL + NL

    # Number of remaining possible tickets for someone to control equals the difference between the maximum
    # ticket pool size which is 40,960 and the current ticket pool size, however, it is often noticed that
    # the pool size is bigger than the maximum because the maximum is not strictly defined, rather it is an
    # ideal indication/metric provided necessary to represent the whole coin holders.  Therefore, in the usual
    # case where current pool is bigger than 40,960, the adversary needs to constantly bid for the 20 tickets
    # per block. Blocks are found in the rate of 5 minutes each, the amount of 5 minutes (therefore blocks per
    # day are 288. This means that there exist 288 * 20 = 5,760 new biddable tickets per day while the pool is
    # throwing away 5 tickets every block therefore every 5 minutes. This means that the pool is throwing away
    # 288 * 5 = 1,440 per day to accept this number out of 5,760 possible.
    # For this purpose, our tactic will be to bid high enough for at least 1,440 new tickets per day to ensure
    # that new tickets will be ours and once a good amount of ticket gets mature and concentrated in the pool
    # then we can initiate malicious actions against the governance proposals and particularly those related to
    # consensus rules.

    s82 = 'Because 5 (honest) tickets per block will be used to vote and immediately'
    s96 = 'expire which leads to 5 new spots for malicious tickets to take over.'
    s83 = 'While this is the case for on-chain votes that vote towards PoW block'
    s84 = 'validity, this is not to be confused with off-chain votes for proposals'
    s97 = 'and consensus rules which is our focus in this simulation. Luckily, the'
    s85 = 'right to vote for governance proposals remains valid during the entire'
    s86 = 'voting window as long as tickets were part of the initial proposal quorum'
    s98 = '(contextually: snapshot of ticket pool at the time where the voting started).'
    s87 = 'The number of days required is because Decred blocks are solved every five'
    s88 = 'minutes which equals 288 blocks per day, therefore 1,440 expired tickets per'
    s89 = 'day able to be replaced by 20 biddable tickets per block that equals 5,760'
    s90 = 'tickets as candidates to replace those 1,440.'

    print('REASON', '\n')
    print(s82)
    print(s96)
    print(s83)
    print(s84)
    print(s97)
    print(s85)
    print(s86)
    print(s98, '\n')
    print(s87)
    print(s88)
    print(s89)
    print(s90, '\n')

    PDF_REPORT += 'REASON' + NL + NL
    PDF_REPORT += s82 + ' ' + s96 + ' ' + s83 + ' ' + s84 + ' ' + s97 + ' ' + s85 + s86 + s98 + NL + NL
    PDF_REPORT += s87 + ' ' + s88 + ' ' + s89 + ' ' + s90 + NL + NL

    s28 = 'HYPOTHETICAL REALISATION'

    s29 = 'Decred coin price before attack initiation (£):'
    s30 = 'Estimated coin price after purchase (£):'
    s91 = 'Decred ticket price before attack initiaton (in DCR):'
    s92 = 'Estimated ticket price after purchase (in DCR):'
    s31 = 'Estimated total cost with inflation (£):'
    s99 = 'Cost includes competent bidding with high transaction fees to increase'
    s100 = 'chances of ticket bids being picked by miners and placed in ticket pool.'

    print(s28, '\n')

    print(s29, coin_price)
    print(s30, new_coin_price)
    print(s91, ticket_price)
    print(s92, new_ticket_price)
    print(s31, cost)
    print(s99)
    print(s100)

    PDF_REPORT += s28 + NL + NL

    PDF_REPORT += s29 + ' ' + str(coin_price) + NL
    PDF_REPORT += s30 + ' ' + str(new_coin_price) + NL
    PDF_REPORT += s91 + ' ' + str(ticket_price) + NL
    PDF_REPORT += s92 + ' ' + str(new_ticket_price) + NL
    PDF_REPORT += s31 + ' ' + str(cost) + NL
    PDF_REPORT += s99 + ' ' + str(s100) + NL

    # If budget was set then provide the remaining budget to the user.
    if budget > MIN_BUDGET:
        s32 = 'Therefore remaining budget equals (£):'
        remaining_budget = float('{0:.3f}'.format(budget - cost))
        print(s32, remaining_budget)
        PDF_REPORT += s32 + ' ' + str(remaining_budget) + NL

    print()
    s33 = 'Coins in circulation after purchase:'
    print(s33, coins)
    PDF_REPORT += NL
    PDF_REPORT += s33 + ' ' + str(coins) + NL

    s93 = 'From which coins frozen for tickets:'
    print(s93, new_num_frozen)
    PDF_REPORT += s93 + ' ' + str(new_num_frozen) + NL

    s94 = 'Therefore, coins remaining available to acquire:'
    print(s94, new_remaining)
    PDF_REPORT += s94 + ' ' + str(new_remaining) + NL

    s95 = 'Ticket pool size after purchase:'
    print(s95, new_num_tickets)
    PDF_REPORT += s95 + ' ' + str(new_num_tickets) + NL

    print('From which malicious:',
          num_tickets_for_attack,
          '+ ' + str(tickets_controlled) + ' = ' + str(num_tickets_for_attack + tickets_controlled)
          if tickets_controlled > MIN_CONTROL else '', '(' + percentage_malicious + '% of total tickets)')
    PDF_REPORT += 'From which malicious: ' + str(num_tickets_for_attack) + ' + ' + str(tickets_controlled) + ' = ' \
                  + str(num_tickets_for_attack + tickets_controlled) + ' (' + percentage_malicious \
                  + '% of total tickets)' + NL + NL if tickets_controlled > MIN_CONTROL \
        else 'From which malicious: ' + str(num_tickets_for_attack) + ' (' + percentage_malicious \
             + '% of total tickets)' + NL + NL

    # One block reward every nine days as Return on Investment.
    daily_earn_decred = float('{0:.2f}'.format(((ticket_reward * ONE_DAY) / AVG_DAYS_FOR_REWARD) * total_malicious))
    daily_earn_gbp = float('{0:.2f}'.format(new_coin_price * daily_earn_decred))

    monthly_earn_decred = float('{0:.2f}'.format(((ticket_reward * ONE_MONTH) / AVG_DAYS_FOR_REWARD) * total_malicious))
    monthly_earn_gbp = float('{0:.2f}'.format(new_coin_price * monthly_earn_decred))

    yearly_earn_decred = float('{0:.2f}'.format(((ticket_reward * ONE_YEAR) / AVG_DAYS_FOR_REWARD) * total_malicious))
    yearly_earn_gbp = float('{0:.2f}'.format(new_coin_price * yearly_earn_decred))

    print('\n')
    print('RETURN ON INVESTMENT', '\n')
    PDF_REPORT += 'RETURN ON INVESTMENT' + NL + NL

    s87 = 'Money invested in this attack are not lost, just exchanged from GBP to Decred.'
    s82 = 'Daily Decred expected from ticket block reward:'
    s83 = 'Monthly Decred expected from ticket block reward:'
    s84 = 'Yearly Decred expected from ticket block reward:'
    s85 = 'Estimated profits should also take into consideration any potential increase'
    s86 = 'in the highly volatile original coin price with which tickets were acquired.'

    print(s87)
    print(s82, daily_earn_decred, '(£' + str(daily_earn_gbp) + ')')
    print(s83, monthly_earn_decred, '(£' + str(monthly_earn_gbp) + ')')
    print(s84, yearly_earn_decred, '(£' + str(yearly_earn_gbp) + ')')
    print(s85)
    print(s86)

    PDF_REPORT += s87 + NL
    PDF_REPORT += s82 + ' ' + str(daily_earn_decred) + ' (£' + str(daily_earn_gbp) + ')' + NL
    PDF_REPORT += s83 + ' ' + str(monthly_earn_decred) + ' (£' + str(monthly_earn_gbp) + ')' + NL
    PDF_REPORT += s84 + ' ' + str(yearly_earn_decred) + ' (£' + str(yearly_earn_gbp) + ')' + NL
    PDF_REPORT += s85 + ' ' + s86 + NL + NL

    kibana_dict.update({'DailyDash': daily_earn_decred,
                        'DailyGBP': daily_earn_gbp,
                        'MonthlyDash': monthly_earn_decred,
                        'MonthlyGBP': monthly_earn_gbp,
                        'YearlyDash': yearly_earn_decred,
                        'YearlyGBP': yearly_earn_gbp})

    print('\n')
    print('SUMMARY', '\n')
    PDF_REPORT += 'SUMMARY' + NL + NL

    s37 = 'Number of tickets required for malicious majority:'
    s38 = 'This will take this number of days to be realised:'
    s39 = 'Estimated total cost with inflation (£):'
    s40 = 'Ticket pool size:'

    print(s37, malicious_60)
    PDF_REPORT += s37 + ' ' + str(malicious_60) + NL

    print(s38, attack_overhead_in_days)
    PDF_REPORT += s38 + ' ' + str(attack_overhead_in_days) + NL

    print(s39, cost)
    PDF_REPORT += s39 + ' ' + str(cost) + NL

    print(s40, new_num_tickets)
    PDF_REPORT += s40 + ' ' + str(new_num_tickets) + NL

    print('From which malicious:', str(total_malicious) + ' (' + percentage_malicious + '% of total tickets)')
    PDF_REPORT += 'From which malicious: ' + str(total_malicious) + ' (' + percentage_malicious \
                  + '% of total tickets)' + NL + NL

    # For a proposal to pass in an honest way even if the adversary maliciously downvotes, the following formula
    # should hold: positive votes - negative votes >= 10% of active masternodes.
    anti_dos_for_less_than_possible = math.ceil(ticket_pool_size * SIXTY_PERCENT)

    print('\n')

    s52 = 'INSIGHTS: WHAT PROBLEMS CAN WE CAUSE RIGHT NOW?'
    print(s52, '\n')
    PDF_REPORT += s52 + NL + NL

    s53 = '(1) PREVENT HONEST PROPOSALS TO GO THROUGH'
    print(s53, '\n')
    PDF_REPORT += s53 + NL + NL

    print('EXAMPLE', '\n')
    PDF_REPORT += 'EXAMPLE' + NL + NL
    s54 = 'Downvote key consensus changes that would make the coin more scalable'
    print(s54, '\n')
    PDF_REPORT += s54 + NL + NL

    print('DESIGN VULNERABILITY', '\n')
    PDF_REPORT += 'DESIGN VULNERABILITY' + NL + NL
    s55 = 'Decred tries to be cencorship-free and fully guided from its community,'
    s56 = 'therefore all decisions are respected and final, without asking anything.'
    print(s55)
    print(s56, '\n')
    PDF_REPORT += s55 + ' ' + s56 + NL + NL

    print('SUCCESS LIKELIHOOD: HIGH', '\n')
    PDF_REPORT += 'SUCCESS LIKELIHOOD: HIGH' + NL + NL
    s57 = 'Since the dominant motivation of ticket owners is profit from'
    s58 = 'PoS rewards and not the coin development, it was noticed that'
    s101 = 'governance proposals do not attract more than half of pool size'
    s102 = 'votes therefore there exists high voting abstention which makes'
    s103 = 'this attack very possible to happen.'
    print(s57)
    print(s58)
    print(s101)
    print(s102)
    print(s103)
    PDF_REPORT += s57 + ' ' + s58 + ' ' + s101 + ' ' + s102 + ' ' + s103 + NL + NL

    print()
    print('METHODOLOGY', '\n')
    PDF_REPORT += 'METHODOLOGY' + NL + NL
    s59 = 'By down-voting proposals so that 60% margin is not achieved'
    print(s59, '\n')
    PDF_REPORT += s59 + NL + NL

    print('EXPLOITATION', '\n')
    PDF_REPORT += 'EXPLOITATION' + NL + NL

    s60 = 'Total votes from malicious tickets:'
    s61 = 'Least honest votes required for net majority:'
    s106 = 'While ticket pool has a size of:'
    print(s60, total_malicious)
    print(s61, anti_dos_for_less_than_possible, '(60% of ticket pool)')
    print(s106, ticket_pool_size, '\n')
    PDF_REPORT += s60 + ' ' + str(total_malicious) + NL
    PDF_REPORT += s61 + ' ' + str(anti_dos_for_less_than_possible) + ' ' + '(60% of ticket pool)' + NL
    PDF_REPORT += s106 + ' ' + str(ticket_pool_size) + NL + NL

    # Least honest ticket votes required for a malicious proposal to not have net 60% and do not go through.
    if total_malicious == int(math.ceil(ticket_pool_size * SIXTY_PERCENT)):
        approved_anw_for_less_than_possible = math.ceil(ticket_pool_size * MIN_REJECTION)
    else:
        approved_anw_for_less_than_possible = math.ceil(total_malicious * MIN_REJECTION)

    s64 = '(2) MALICIOUS PROPOSAL PASSES BY NEGLIGENCE'
    print(s64, '\n')
    PDF_REPORT += s64 + NL + NL

    print('EXAMPLE', '\n')
    PDF_REPORT += 'EXAMPLE' + NL + NL
    s65 = 'Malicious proposal up-voted from malicious tickets that had net majority prior to'
    s104 = 'the start of voting window or even if they had not they can still dominate when'
    s105 = 'voting abstention is high as it is in 99 out of 100 cases.'
    print(s65)
    print(s104)
    print(s105, '\n')
    PDF_REPORT += s65 + ' ' + s104 + ' ' + s105 + NL + NL

    print('DESIGN VULNERABILITY', '\n')
    PDF_REPORT += 'DESIGN VULNERABILITY' + NL + NL
    s66 = 'Votes are never questioned therefore if a proposal is accepted, no censorship exists.'
    print(s66, '\n')
    PDF_REPORT += s66 + NL + NL

    print('SUCCESS LIKELIHOOD: MEDIUM', '\n')
    PDF_REPORT += 'SUCCESS LIKELIHOOD: MEDIUM' + NL + NL
    s67 = 'The controversy of a malicious proposal is expected to unite honest owners.'
    print(s67, '\n')
    PDF_REPORT += s67 + NL + NL

    print('METHODOLOGY', '\n')
    PDF_REPORT += 'METHODOLOGY' + NL + NL
    s68 = 'Malicious proposal starts to be up-voted as close as possible to the closing window.'
    print(s68, '\n')
    PDF_REPORT += s68 + NL + NL

    print('EXPLOITATION', '\n')
    PDF_REPORT += 'EXPLOITATION' + NL + NL

    # Vice-versa case of malicious denial of service.
    s69 = 'Total votes from malicious tickets:'
    s70 = 'Least honest votes required for proposal rejection (40.1%):'
    s107 = 'Which does not satisfy the minimum total vote requirements of 10% pool size:'

    print(s69, total_malicious)
    if num_tickets_for_attack < MIN_QUORUM_PERCENTAGE * ticket_pool_size:
        print(s107, math.ceil(MIN_QUORUM_PERCENTAGE * ticket_pool_size))
    else:
        print(s70, approved_anw_for_less_than_possible)
    print(s106, ticket_pool_size)

    PDF_REPORT += s69 + ' ' + str(total_malicious) + NL
    if num_tickets_for_attack < MIN_QUORUM_PERCENTAGE * ticket_pool_size:
        PDF_REPORT += s107 + str(math.ceil(MIN_QUORUM_PERCENTAGE * ticket_pool_size))
    else:
        PDF_REPORT += s70 + ' ' + str(approved_anw_for_less_than_possible) + NL
    PDF_REPORT += s106 + ' ' + str(ticket_pool_size) + NL

    # Downvote proposal hoping honest majority.
    kibana_dict.update({'MalDownvote': anti_dos_for_less_than_possible,
                        # Not achieved, variable holds the number of honest positive votes required to pass.
                        # Upvote proposal hoping honest nodes will # not achieve denial via honest negative vote.
                        # variable holds the upper bound needed for denial.
                        'MalUpvote': approved_anw_for_less_than_possible})


# This is the main method of the program, responsible for IO using the above methods.
def main():
    print('''
DECRED (DCR) DECENTRALISED GOVERNANCE ATTACK SIMULATOR
    ''')

    while True:
        filename = input('File name for report and dashboard: (press enter for default file name)  ')
        budget = input('Attack budget (£): (press enter for enough budget to be successful)  ')
        coin_price = input('Decred coin price (£): (press enter for real time coin price)  ')
        ticket_price = input('Decred ticket price (in DCR): (press enter for real time ticket price)  ')
        exp = input('Inflation rate (1-10)(1: Aggressive, 10: Slow): (press enter for default rate)  ')
        coins = input('Coins in circulation: (press enter for real time circulation)  ')
        ticket_pool_size = input('Ticket pool size: (press enter for real time ticket pool size)  ')
        tickets_controlled = input('Tickets already under control or bribe: (press enter for none)  ')
        tickets_target = input('Target total tickets: (press enter for enough to be successful)  ')
        ticket_reward = input('Ticket reward per block: (press enter for real time value)  ')

        try:
            filename = str(filename) if filename else DEF_FILENAME
            budget = float(budget) if budget else MIN_BUDGET
            coin_price = float(coin_price) if coin_price else acquire_real_time_price()
            ticket_price = float(ticket_price) if ticket_price else acquire_real_time_ticket_price()
            exp = float((int(exp) + SANITISE) * INVERSE) if exp and (MIN_EXP < int(exp) < MAX_EXP) else float(DEF_EXP)
            exp_incr = math.pow(math.e, exp)
            coins = int(coins) if coins else acquire_real_time_circulation()
            ticket_pool_size = int(ticket_pool_size) if ticket_pool_size else acquire_real_time_ticket_pool_size()
            tickets_controlled = int(tickets_controlled) if tickets_controlled else MIN_CONTROL

            # Ensures target tickets are greater than those already controlled and smaller than those possible.
            if tickets_target and tickets_controlled < int(tickets_target) <= MAX_TICKETS:
                tickets_target = int(tickets_target)
            elif tickets_target and tickets_controlled >= int(tickets_target):
                print('\nError: Target total tickets should be greater than tickets already controlled, please try'
                      ' again!')
                float(DEF_FILENAME)
            else:
                tickets_target = MIN_TARGET

            ticket_reward = float(ticket_reward) if ticket_reward else acquire_real_time_ticket_reward()

            # Budget, coin price and master node numbers related number should be all greater than zero.
            if not (budget >= MIN_BUDGET and coin_price >= MIN_PRICE and ticket_pool_size >= MIN_POOL_SIZE
                    and coins >= MIN_CIRCULATION and tickets_controlled >= MIN_CONTROL
                    and tickets_target >= MIN_TARGET):
                print('\nError: all arithmetic parameters should be greater than or equal to zero, please try again!')
                # Causes intentional exception and re-loop as values should be greater than zero.
                float(DEF_FILENAME)
            break
        except ValueError:
            print()
            pass

    # Dictionary is updated based on user choices.
    kibana_dict.update({'Budget': budget,
                        'PriceBef': coin_price,
                        'TicketPriceBef': ticket_price,
                        'Inflation': exp,
                        'Circulation': coins,
                        'TicketPoolSize': ticket_pool_size,
                        'Controlled': tickets_controlled,
                        'Target': tickets_target,
                        'TicketRew': ticket_reward})

    attack_phase_1(filename, budget, coin_price, ticket_price, exp_incr, coins, ticket_pool_size, tickets_controlled,
                   tickets_target, ticket_reward)
    create_csv(filename)
    create_pdf(filename)


main()
