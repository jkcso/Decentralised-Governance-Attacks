from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from urllib.request import Request, urlopen
import csv
import json
import os
import ssl
import math
import pdfkit

# global variables are defined here once for clarity and duplication-free coding
DASH_MN_COLLATERAL = 1000
MIN_COINBASE_RANKING = MIN_EXP = ONE_MN = 1
MAX_COINBASE_RANKING = 20
COINBASE_API_KEY = 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
MIN_PRICE = MIN_CIRCULATION = MIN_BUDGET = MIN_REMAINING = MIN_CONTROL = MIN_TARGET = 0
OS = 0  # Output Start, used mostly for long floats, strings and percentages
OE = 4  # Output End
PERCENTAGE = 100
MAX_SUPPLY = 18900000
NET_10_PERCENT = 1.1
MIN_10_PERCENT = 0.1
INVERSE = -1
DEF_EXP = -13  # corresponds to number 8 from 1-10 scale which is medium to slow exponential increase
DEF_INFLATION = math.pow(math.e, DEF_EXP)
MAX_EXP = 11
SANITISE = 5
SIXTY_PERCENT = 0.6
MALICIOUS_NET_MAJORITY = 55
IS_MASTERNODES_NUMBER_REAL = IS_COIN_PRICE_REAL = IS_CIRCULATION_REAL = False
ADAPTOR = 2
DEF_FILENAME = 'default'
RT = '(real time value)'
UD = '(user defined value)'
DEF = '(default exponential)'
NL = '<br>'  # new line character for html
PDF_REPORT = ''  # global variable to hold the current state of pdf report; to be edited along the way
PDF_REPORT_HEADER = '''
<html>
<head></head>
<body><p>
'''
PDF_REPORT_INTRO = '''
REPORT <br><br>
Dash Decentralised Governance Attack Simulation <br><br>
'''
PDF_REPORT_FOOTER = '''
</p></body>
</html>
'''

# the dictionary that then becomes the .csv file for Kibana
# initially has some global variables useful for the dashboard
kibana_dict = {'Collateral': DASH_MN_COLLATERAL,
               'MaxSupply': MAX_SUPPLY}


def acquire_real_time_masternodes():

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    mn_stats = 'https://stats.masternode.me/network-report/latest/json'
    req_stats = Request(mn_stats, headers={'User-Agent': 'Mozilla/5.0'})
    stats = json.loads(urlopen(req_stats).read().decode("utf-8"))

    global IS_MASTERNODES_NUMBER_REAL
    IS_MASTERNODES_NUMBER_REAL = True
    return stats['raw']['mn_count']


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
                if data['data'][i]['name'] == 'Dash':
                    real_time_price = data['data'][i]['quote']['GBP']['price']

            global IS_COIN_PRICE_REAL
            IS_COIN_PRICE_REAL = True
            return float('{0:.2f}'.format(real_time_price))

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


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
                if data['data'][i]['name'] == 'Dash':
                    real_time_circulation = data['data'][i]['circulating_supply']

            global IS_CIRCULATION_REAL
            IS_CIRCULATION_REAL = True
            return int(real_time_circulation)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


def create_csv(filename):

    with open(filename + '.csv', 'w') as f:
        w = csv.DictWriter(f, kibana_dict.keys())
        w.writeheader()
        w.writerow(kibana_dict)


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
def attack_phase_1(filename, budget, coin_price, exp_incr, active_mn, coins, mn_controlled, mn_target):

    global PDF_REPORT
    PDF_REPORT += 'test for attack phase 1' + NL

    print('\n')
    print('FILES TO BE GENERATED:', '\n')
    print(filename + '.csv,', filename + '.html,', filename + '.pdf', '\n', '\n')

    print('VALUES PROCEEDING WITH', '\n')
    print('Attack budget (£): unspecified (cost estimated in phase two)') \
        if budget == MIN_BUDGET \
        else print('Attack budget (£):', budget, UD)
    print('Dash price (£):', coin_price, RT if IS_COIN_PRICE_REAL else UD)
    print('Inflation rate:', str(exp_incr)[OS:OE], DEF if exp_incr == DEF_INFLATION else UD)
    print('Total of honest masternodes:', active_mn, RT if IS_MASTERNODES_NUMBER_REAL else UD)
    print('Coins in circulation:', coins, RT if IS_CIRCULATION_REAL else UD)
    print('Honest masternodes already under control or bribe:', mn_controlled)

    cost = float(MIN_PRICE)
    new_price = coin_price
    budget_mn = MIN_BUDGET

    # if budget is set, exchange it from GBP to DASH and perform inflation estimation for the new price and cost
    if budget > MIN_BUDGET:
        budget_to_dash = math.floor(budget / coin_price)  # amount of dash exchanged from budget
        for i in range(MIN_PRICE, budget_to_dash):
            new_price += exp_incr

        budget_mn = math.floor(int(budget_to_dash // DASH_MN_COLLATERAL))
        new_price = float("{0:.2f}".format(new_price))

        # the global value of adaptor is used towards the median new coin price which is necessary for the inclusion
        # of both low and high coin values for when inflated. The initial form (commented) of cost prediction without
        # optimisation would be the following which is however over estimated due to only using the new coin price:
        # cost = float("{0:.3f}".format(budget_mn * DASH_MN_COLLATERAL * new_price))
        cost = float('{0:.3f}'.format(
            budget_mn * DASH_MN_COLLATERAL * (coin_price +
                                              (budget_to_dash / (
                                                      budget_to_dash - budget_to_dash / ADAPTOR) * exp_incr))))

    # the amount of masternodes required to launch the infamous 55% governance attack
    malicious_net_10 = int(math.ceil(active_mn * NET_10_PERCENT)) + ONE_MN
    kibana_dict.update({'MaliciousNet': malicious_net_10})

    # when budget is set, the number of mn to acquire should correspond to the budget but also
    # when both budget and a target number of mn is set, then the budget is what matters in estimation
    if budget > MIN_BUDGET and mn_target >= MIN_TARGET:
        mn_target = budget_mn
        print('Target total masternodes:', mn_target, '(capped due to budget)')

    # when user provides budget and already controlled nodes, the target should be based on budget and the following
    # operation is there to erase the subtraction specifying that master nodes to buy are those not already controlled
    if budget > MIN_BUDGET and mn_target == budget_mn and mn_controlled > MIN_CONTROL:
        mn_target += mn_controlled
        print('Total masternodes including already controlled or bribed:', mn_target)

    # when the budget is not set but a target number of mn to acquire is provided
    elif budget == MIN_BUDGET and mn_target > MIN_TARGET:
        mn_target = mn_target
        print('Target total masternodes:', mn_target, UD)

    # when neither budget nor mn target is set, the metric defaults to a malicious net 10% majority
    elif budget == MIN_BUDGET and mn_target == MIN_TARGET:
        mn_target = malicious_net_10
        print('Target total masternodes: unspecified (defaults to net 10% over honest)')

    # based on the above conditions, the number of masternodes to purchase is determined here
    num_mn_for_attack = mn_target - mn_controlled

    print('\n')
    print('ATTACK PHASE ONE: PLANNING AND REASONING', '\n')
    print('Masternodes required for net 10% over honest:', malicious_net_10)

    # budget defaults to malicious net 10%
    if budget == MIN_BUDGET and mn_target == MIN_TARGET:
        print('Attack budget: cost of purchase net 10%')

    # budget is set but target dominates
    elif budget > MIN_BUDGET and mn_target > MIN_TARGET:
        print('Attack budget (£):', budget, '(enough to acquire:', budget_mn,
              'masternodes)' if budget_mn > ONE_MN else 'masternode)')
        # even if the budget is enough to acquire much more of what is needed to be sucessful, cap it to just enough
        # to save budget
        if budget_mn >= malicious_net_10:
            budget_mn = malicious_net_10
            mn_target = budget_mn
            num_mn_for_attack = mn_target - mn_controlled

    # budget is set to enough to accommodate the target
    elif budget == MIN_BUDGET and mn_target > MIN_TARGET:
        print('Attack budget (£): cost of realise target of', mn_target,
              'masternodes' if mn_target > ONE_MN else 'masternode')

    print('Therefore, target total masternodes:', mn_target if budget == MIN_BUDGET else budget_mn)
    print('Excluding those already under control or bribe, total:', mn_controlled)
    print('Finalised total of masternodes to acquire:', num_mn_for_attack)

    # calls the following method to proceed in attempting the purchase
    attack_phase_2(budget, coin_price, exp_incr, active_mn, coins, mn_controlled, num_mn_for_attack, cost, new_price)


'''
Proceeds to the purchase of X Master Nodes and then analyses the newly created situation,
providing also possible scenarios on how attackers and defenders might proceed.
Example:
    We purchase X=10 Master Nodes.  Each requires a collateral of 1K DASH, therefore
    we would need 10K DASH.  If 1 DASH costs £300, then the final cost of investment
    due to the dynamic price increase would be £3000559.71 and the new DASH price will
    increase to £300.11.
    Then we generate statistics on how successful the attacker can be by controlling this
    X amount of Master Nodes and we provide further options on how to proceed that are able
    to help both attacking and defending parties for one step forward, always ethically.
'''


def attack_phase_2(budget, coin_price, exp_incr, active_mn, coins, mn_controlled, num_mn_for_attack, cost, new_price):

    global PDF_REPORT
    PDF_REPORT += 'test for attack phase 2' + NL

    frozen_coins = DASH_MN_COLLATERAL * active_mn
    unfrozen_coins = coins - frozen_coins
    possible_mn = math.floor(int(unfrozen_coins // DASH_MN_COLLATERAL))
    percentage_poss_total = str(float((possible_mn / math.floor(int(coins // DASH_MN_COLLATERAL))) * PERCENTAGE))[0:4]

    kibana_dict.update({'FrozenBef': frozen_coins,
                        'PurchaseBef': num_mn_for_attack,
                        'PurchaseAft': MIN_TARGET})  # placeholder for a potential unsuccessful first purchase attempt

    # attempts to purchase initial required amount no matter if impossible as this number is later capped to possible
    print('\n')
    print('ATTACK PHASE TWO: EXECUTION', '\n')
    print('FIRST PURCHASE ATTEMPT FOR', num_mn_for_attack, 'MASTER NODES', '\n')
    print("Dash Price before purchase: £" + str(coin_price))
    print("Active Master Nodes before purchase:", active_mn)
    print("Coins in circulations before purchase:", coins)
    print("From which coins frozen for required collateral:", frozen_coins)
    print("Therefore, coins remaining unfrozen:", unfrozen_coins)
    print("These are enough to get us more Master Nodes, actually up to this number:", possible_mn)
    print("Which as percentage out of the total possible Master Nodes is:", str(percentage_poss_total) + '%')

    # when budget is not set it means that what is required is to a dynamic cost for purchasing masternodes only.
    if budget == MIN_BUDGET:
        cost = float(MIN_PRICE)
        new_price = coin_price
        for i in range(MIN_PRICE, num_mn_for_attack * DASH_MN_COLLATERAL):
            cost += new_price
            new_price += exp_incr
        cost = float("{0:.3f}".format(cost))
        new_price = float("{0:.2f}".format(new_price))

    new_num_frozen = frozen_coins + num_mn_for_attack * DASH_MN_COLLATERAL
    new_remaining = coins - new_num_frozen
    new_num_mn = active_mn + num_mn_for_attack
    new_possible_mn = math.floor(int(new_remaining // DASH_MN_COLLATERAL))
    total_malicious = num_mn_for_attack + mn_controlled
    percentage_malicious = str(float((total_malicious / new_num_mn) * PERCENTAGE))[0:4]
    percentage_mn_left = str(float((new_possible_mn / math.floor(int(coins // DASH_MN_COLLATERAL))) * PERCENTAGE))[0:4]

    kibana_dict.update({'Cost': cost,
                        'PriceAft': new_price,
                        'FrozenAft': new_num_frozen,
                        'PossibleAft': new_possible_mn,  # possible masternodes based on remaining unfrozen coins
                        'ActiveAft': new_num_mn,  # new total masternodes including both honest and malicious
                        'Malicious': total_malicious})  # total malicious masternodes

    p = 'POSSIBLE!'
    im = 'IMPOSSIBLE!'
    attack_outcome = p if new_remaining >= MIN_REMAINING else im
    print()
    print('PURCHASE OUTCOME:', attack_outcome, '\n')
    if attack_outcome == im:
        print(
            "WHY: Because the remaining coins in circulation are not enough for " + str(num_mn_for_attack) + " master\n"
            "     nodes but for a maximum amount of",
            possible_mn, "still able to cause cyber sabotage")
    print("New Dash Price after this investment: £" + str(new_price))
    print("Estimated cost of purchase (including dynamic price increase): £" + str(cost))
    # if budget was set then provide the remaining budget to the user
    if budget > MIN_BUDGET:
        remaining_budget = float("{0:.3f}".format(budget - cost))
        print("Therefore remaining budget equals: £" + str(remaining_budget))
    print("Coins in circulation after purchase:", coins)
    print("From which coins frozen for required collateral:", new_num_frozen) if attack_outcome == p else print(
        "From which coins frozen for required collateral:", new_num_frozen, "<------ (Problematic Result)")

    print("Therefore, coins remaining unfrozen:", "{0:.3f}".format(new_remaining),
          "<------ (Problematic Result)") if attack_outcome == im \
        else print("Therefore, coins remaining unfrozen:", new_remaining,
                   "\nWhich are enough to acquire more Master Nodes, actually:", new_possible_mn, "Master Nodes",
                   "\nWhich as a percentage, takes this share from the total possible to buy master nodes: " +
                   percentage_mn_left + "%",
                   "\nRemember that 55% is the perfect percentage which guarantees success in any governance attack")

    print("Active Master Nodes after purchase:", new_num_mn) if new_num_mn <= possible_mn \
        else print("Potential Active Master Nodes after purchase:", new_num_mn)
    print("From which malicious:",
          num_mn_for_attack, "+ " + str(mn_controlled) + " = " + str(num_mn_for_attack + mn_controlled)
          if mn_controlled > MIN_CONTROL else "", "(" + percentage_malicious + "% of Total)")

    print("The available coin supply was enough to buy this amount of Master Nodes:", possible_mn,
          "\nThe purchase attempted was for: ", num_mn_for_attack, "Master Nodes", "<------ (Problematic Result)"
          if num_mn_for_attack > possible_mn else "")

    # The initial attack was not realised due to the high number of masternodes attempted to purchase, therefore
    # a noisy and determined to succeed adversary can proceed to the purchase of the highest number possible
    # Impossibility of purchase occurs when the number of masternodes to acquire is greater than the possible amount
    # achievable that is constrained from the unfrozen circulation
    if attack_outcome == im:
        num_mn_for_attack = possible_mn
        attack_outcome = 'POSSIBLE!'
        print()
        print('SECOND PURCHASE ATTEMPT FOR', num_mn_for_attack, 'MASTER NODES', '\n')
        cost = float(MIN_PRICE)
        new_price = coin_price
        for i in range(MIN_PRICE, num_mn_for_attack * DASH_MN_COLLATERAL):
            cost += new_price
            new_price += exp_incr
        cost = float("{0:.3f}".format(cost))
        new_price = float("{0:.2f}".format(new_price))
        new_num_frozen = frozen_coins + num_mn_for_attack * DASH_MN_COLLATERAL
        new_remaining = coins - new_num_frozen
        new_num_mn = active_mn + num_mn_for_attack
        new_possible_mn = math.floor(int(new_remaining // DASH_MN_COLLATERAL))
        total_malicious = num_mn_for_attack + mn_controlled
        percentage_malicious = str(float((total_malicious / new_num_mn) * PERCENTAGE))[0:4]

        kibana_dict.update({'PurchaseAft': num_mn_for_attack,
                            'Cost': cost,
                            'PriceAft': new_price,
                            'FrozenAft': new_num_frozen,
                            'PossibleAft': new_possible_mn,  # possible masternodes based on remaining unfrozen coins
                            'ActiveAft': new_num_mn,  # new total masternodes including both honest and malicious
                            'Malicious': total_malicious})  # total malicious masternodes

        print('PURCHASE OUTCOME:', attack_outcome, '\n')
        print("Dash Price before purchase: £" + str(coin_price))
        print("New Dash Price after this investment: £" + str(new_price))
        print("Estimated cost of purchase (including dynamic price increase): £" + str(cost))
        print("Coins in circulation after purchase:", coins)
        print("From which coins frozen for required collateral:", new_num_frozen)
        print("Therefore, coins remaining unfrozen:", "{0:.3f}".format(new_remaining))
        print("Active Master Nodes before purchase:", active_mn)
        print("Active Master Nodes after purchase:", new_num_mn)
        print("From which malicious:",
              num_mn_for_attack, "+ " + str(mn_controlled) + " = " + str(num_mn_for_attack + mn_controlled)
              if mn_controlled > MIN_CONTROL else "", "(" + percentage_malicious + "% of Total)")

    # for a proposal to pass in an honest way even if the adversary maliciously downvotes, the following formula
    # should hold: positive votes - negative votes >= 10% of active masternodes
    anti_dos_poss = math.floor(num_mn_for_attack * NET_10_PERCENT) + ONE_MN \
        if num_mn_for_attack > new_num_mn * MIN_10_PERCENT \
        else math.ceil(new_num_mn * MIN_10_PERCENT + num_mn_for_attack)
    anti_dos_needed = math.ceil(possible_mn * NET_10_PERCENT) + ONE_MN
    approved_anw = math.ceil(num_mn_for_attack / NET_10_PERCENT) - ONE_MN \
        if num_mn_for_attack > new_num_mn * MIN_10_PERCENT \
        else math.floor(new_num_mn * MIN_10_PERCENT)
    avg_mn_votes = math.floor(active_mn * SIXTY_PERCENT)
    net_10_anw = math.floor(avg_mn_votes * NET_10_PERCENT) + ONE_MN
    negligence_out = "YES!" if num_mn_for_attack >= net_10_anw or (num_mn_for_attack + new_possible_mn) >= net_10_anw \
        else "NO!"
    total_rem = MAX_SUPPLY - coins
    total_rem_mn = math.floor(int(total_rem // DASH_MN_COLLATERAL))
    percentage_total_master_nodes = str(float((coins / MAX_SUPPLY) * PERCENTAGE))[0:4]
    c2019 = 8761092
    c2020 = 9486800
    c2021 = 10160671
    mn2019 = math.floor(int((c2019 - coins) // DASH_MN_COLLATERAL))
    mn2020 = math.floor(int((c2020 - coins) // DASH_MN_COLLATERAL))
    mn2021 = math.floor(int((c2021 - coins) // DASH_MN_COLLATERAL))

    kibana_dict.update({'MalDownvote': anti_dos_poss,  # downvote proposal hoping honest majority not achieved
                        # however note that anti_dos_poss hold the number of honest positive votes required to pass
                        'MalUpvote': approved_anw,  # upvote proposal hoping honest nodes will not manage to deny it
                        # via their honest negative voting; approved_anw holds the upper bound needed to achieve denial
                        'ExpVoters': avg_mn_votes,  # Expected to vote honestly to prevent a malicious action to occur
                        'ExpVotAtt': net_10_anw})  # Malicious Net 10% against the expected honest votes

    print()
    print('PROCEEDING TO PLAN B: WHAT PROBLEMS CAN WE CAUSE RIGHT NOW?', '\n')
    print("1) Prevent honest proposals to go through! (i.e: The salaries of Dash Core Developers)")
    print("Explanation: We vote 'no' for a proposal and we hope that net 10% can't be achieved!")

    if attack_outcome == p:
        print("The number of Master Nodes we acquired above is:", num_mn_for_attack, "Master Nodes")
        print("This means that for a proposal to get accepted, it would need this number of positive votes:",
              anti_dos_poss, "Master Nodes")

    print("Maximum possible amount of Master Nodes we can acquire due to coins in circulation is:", possible_mn,
          "Master Nodes")
    print("It means that for a proposal to get accepted, it would need these positive votes:", anti_dos_needed,
          "Master Nodes")
    print("WHY: Anything below the required amount of votes will cause a proposal rejection.")

    print("\n2) Acts of Negligence -- Achievable?", negligence_out)
    print("Explanation: We vote 'yes' for a proposal and we hope in a high % of voting abstention!")

    if attack_outcome == p:
        print("With this amount of Master Nodes under our control, which is:", num_mn_for_attack, "Master Nodes")
        print("A budget proposal will be approved even if this number of honest Master Node votes against:",
              approved_anw, "Master Nodes")

    print("Given that the maximum votes ever recorded for funding a proposal is: 2147 Master Nodes (44.47%)")
    print(
        "Assuming that a controversial proposal will drastically increase this,\nwe will consider a higher percentage "
        "of 60% voters, this means: ",
        avg_mn_votes, "Master Nodes")
    print("Which means that we would need this amount of Master Nodes to achieve net 10%:", net_10_anw, "Master Nodes")
    print("Maximum possible amount of Master Nodes we can acquire due to coins in circulation is:", possible_mn,
          "Master Nodes")

    if attack_outcome == p:
        print("Remember that the remaining coins are enough to acquire more Master Nodes, actually:", new_possible_mn,
              "Master Nodes")
        print("OUTCOME: If we acquire them, then we achieve net 10% in case that 60% of honest Master Node vote.")
        print("WHY: Total number of malicious Master Nodes will become:", num_mn_for_attack + new_possible_mn)
        print("     and we previously needed at least this amount for majority:", net_10_anw, "Master Nodes")

    print("\n3) Maintain a stealthy future")
    print("Current supply (% against total):", coins, "(" +
          percentage_total_master_nodes + "%)")
    print("Total (ever) coin supply:", MAX_SUPPLY)
    print("Remaining Supply/Possible new Master Nodes:", total_rem, "/", total_rem_mn)
    print("Below is the minimum number of coins expected per year along with (%) against total coin supply:")
    print("Expected minted coins until 04/2019(%)/Possible new Master Nodes:", c2019, "(46.3%)", "/", mn2019)
    print("Expected minted coins until 04/2020(%)/Possible new Master Nodes:", c2020, "(50.14%)", "/", mn2020)
    print("Expected minted coins until 04/2021(%)/Possible new Master Nodes:", c2021, "(53.7%)", "/", mn2021)
    print("Furthermore: 08/2029 (74.41%), 03/2043 (90.23%), 05/2073 (98.86%), 04/2150 (100%)")
    print('''SUGGESTED APPROACH:
A stealthy attacker can slowly increase his/her army assuming a percentage gain of
50% mined DASH => Master Nodes per year. Towards this DASH required, the attacker might
use Proof-of-Service rewards able to purchase 25 new Master Nodes per existing Master Nodes per year
(assuming 7.14% Return on Investment). An increase of 1K Master Nodes could take 4-5 years
to be achieved and does not guarantee success! Notice that in the long term, more
years would be needed to acquire further 1K Master Nodes!
''')


# This is the main method of the program, responsible for IO using the above methods.
def main():

    print('''
DASH DECENTRALISED GOVERNANCE ATTACK SIMULATOR
    ''')

    while True:
        filename = input('File name for report and dashboard: (press enter for default file name)  ')
        budget = input('Attack budget (£): (press enter for enough budget to be successful)  ')
        coin_price = input('Dash price (£): (press enter for real time price)  ')
        exp = input('Inflation rate (1-10)(1: Aggressive, 10: Slow): (press enter for default rate)  ')
        active_mn = input('Total of honest masternodes: (press enter for real time active masternodes)  ')
        coins = input('Coins in circulation: (press enter for real time circulation)  ')
        mn_controlled = input('Honest masternodes already under control or bribe: (press enter for none)  ')
        mn_target = input('Target total masternodes: (press enter for enough to be successful)  ')

        try:
            filename = str(filename) if filename else DEF_FILENAME
            budget = float(budget) if budget else MIN_BUDGET
            coin_price = float(coin_price) if coin_price else acquire_real_time_price()
            exp = float((int(exp) + SANITISE) * INVERSE) if exp and (MIN_EXP < int(exp) < MAX_EXP) else float(DEF_EXP)
            exp_incr = math.pow(math.e, exp)
            active_mn = int(active_mn) if active_mn else acquire_real_time_masternodes()
            coins = int(coins) if coins else acquire_real_time_circulation()
            mn_controlled = int(mn_controlled) if mn_controlled else MIN_CONTROL
            # number of masternodes possible for an adversary to control should equal the unfrozen coins in collateral
            num_possible_masternodes = math.floor(int((coins - (active_mn * DASH_MN_COLLATERAL)) // DASH_MN_COLLATERAL))
            # ensures target masternodes are greater than those already controlled and smaller than those possible
            mn_target = int(mn_target) \
                if mn_target and mn_controlled < int(mn_target) <= num_possible_masternodes else MIN_TARGET
            # budget, coin price and master node numbers related number should be all greater than zero
            if not (budget >= MIN_BUDGET and coin_price >= MIN_PRICE and active_mn >= MIN_REMAINING
                    and coins >= MIN_CIRCULATION and mn_controlled >= MIN_CONTROL and mn_target >= MIN_TARGET):
                print('\nError: all arithmetic parameters should be greater than or equal to zero, please try again')
                float(DEF_FILENAME)  # causes intentional exception and re-loop as values should be greater than zero
            break
        except ValueError:
            print()
            pass

    # dictionary is updated based on user choices
    kibana_dict.update({'Budget': budget,
                        'PriceBef': coin_price,
                        'ActiveBef': active_mn,  # total honest masternodes
                        'PossibleBef': num_possible_masternodes,  # possible man based on total remaining unfrozen coins
                        'Inflation': exp,
                        'Circulation': coins,
                        'Controlled': mn_controlled,
                        'Target': mn_target})

    global PDF_REPORT
    PDF_REPORT += PDF_REPORT_HEADER
    PDF_REPORT += PDF_REPORT_INTRO
    PDF_REPORT += 'Budget: ' + str(budget) + NL
    PDF_REPORT += 'PriceBef: ' + str(coin_price) + NL
    PDF_REPORT += 'ActiveBef: ' + str(active_mn) + NL
    PDF_REPORT += 'PossibleBef: ' + str(num_possible_masternodes) + NL
    PDF_REPORT += 'Inflation: ' + str(exp) + NL
    PDF_REPORT += 'Circulation: ' + str(coins) + NL
    PDF_REPORT += 'Controlled: ' + str(mn_controlled) + NL
    PDF_REPORT += 'Target: ' + str(mn_target) + NL + NL

    attack_phase_1(filename, budget, coin_price, exp_incr, active_mn, coins, mn_controlled, mn_target)
    create_csv(filename)
    create_pdf(filename)


main()
