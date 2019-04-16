from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from urllib.request import Request, urlopen
import json
import os
import ssl
import math

DASH_MN_COLLATERAL = 1000
MIN_COINBASE_RANKING = ONE_MN = 1
MAX_COINBASE_RANKING = 20
COINBASE_API_KEY = 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
MIN_PRICE = MIN_CIRCULATION = MIN_BUDGET = MIN_REMAINING = MIN_MN = 0
PERCENTAGE = 100
TOTAL_SUPPLY = 18900000
NET_10_PERCENT = 1.1
INVERSE = -1
DEF_EXP = -11.4
MAX_EXP = 11
SANITISE = 5
SIXTY_PERCENT = 0.6


def intro():
    print("""
    --  DASH CORRUPTED GOVERNANCE ATTACK SIMULATOR  --
    --  Please provide customised information for any parameter OR
    --  Press enter to proceed with the real time values  --
    """)


def acquire_real_time_data():
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
            real_time_circulation = MIN_CIRCULATION

            for i in range(MIN_COINBASE_RANKING, MAX_COINBASE_RANKING):
                if data['data'][i]['name'] == 'Dash':
                    real_time_price = data['data'][i]['quote']['GBP']['price']
                    real_time_circulation = data['data'][i]['circulating_supply']
            return float("{0:.2f}".format(real_time_price)), int(real_time_circulation)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


# Retrieves master nodes real time data.
def acquire_real_time_mn_number():
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    mn_stats = 'https://stats.masternode.me/network-report/latest/json'
    req_stats = Request(mn_stats, headers={'User-Agent': 'Mozilla/5.0'})
    stats = json.loads(urlopen(req_stats).read().decode("utf-8"))

    return stats["raw"]["mn_count"]


# Outputs the values we proceed during the simulation.
def report(budget, coin_price, exp_incr, active_mn, coins, mn_controlled, mn_target):
    print()
    print("    --  INPUT VALUES PROCEEDING WITH  --")
    print("Attack Budget: Not specified therefore equals the total cost as estimated below") \
        if budget == MIN_BUDGET \
        else print("Attack Budget: £" + str(budget))
    print("Dash Price: £" + str(coin_price))
    print("Dash Price Increase Factor (Exponential):", exp_incr)
    print("Number of Active Master Nodes:", active_mn)
    print("Coins in circulation:", coins)
    print("Master Nodes already under control or bribe:", mn_controlled)

    malicious_net_10 = int(math.ceil(active_mn * NET_10_PERCENT)) + ONE_MN
    budget_mn = math.floor(int(budget // (coin_price * DASH_MN_COLLATERAL)))
    mn_target = budget_mn if budget > MIN_BUDGET else malicious_net_10

    print("Target Total Master Nodes: Not specified therefore equals the Malicious Net 10%") \
        if mn_target == malicious_net_10 \
        else print("Target Total Master Nodes:", mn_target if budget == MIN_BUDGET else budget_mn, "due to budget")

    num_mn_for_attack = mn_target - mn_controlled if budget == MIN_BUDGET else budget_mn

    print()
    print("    --  ATTACK PHASE ZERO  --")
    print("Total Master Nodes needed for Malicious Net 10%:", malicious_net_10)
    print("Attack Budget: Not specified therefore equals the total cost as estimated below") \
        if budget == MIN_BUDGET \
        else print("Attack Budget: £" + str(budget), "able to acquire:", budget_mn, "Master Nodes")
    print("Target Total Master Nodes:", mn_target if budget == MIN_BUDGET else budget_mn)
    print("Master Nodes already under control or bribe:", mn_controlled)
    print("Therefore, Master Nodes to acquire:", num_mn_for_attack)

    buy_x_mn(budget, coin_price, exp_incr, active_mn, coins, mn_controlled, num_mn_for_attack)


"""
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
"""


def buy_x_mn(budget, coin_price, exp_incr, active_mn, coins, mn_controlled, num_mn_for_attack):
    frozen = DASH_MN_COLLATERAL * active_mn
    remaining_coins = coins - frozen
    possible_mn = math.floor(int(remaining_coins // DASH_MN_COLLATERAL))
    percentage_master_nodes = str(float((possible_mn / active_mn) * PERCENTAGE))[0:4]

    print("\n    --  ATTEMPTING TO PURCHASE", num_mn_for_attack, "MASTER NODES  --")
    print("Dash Price before purchase: £" + str(coin_price))
    print("Active Master Nodes before purchase:", active_mn)
    print("Coins in circulations before purchase:", coins)
    print("From which coins frozen for required collateral:", frozen)
    print("Therefore, coins remaining unfrozen:", remaining_coins)
    print("These are enough to get us more Master Nodes, actually up to this number:", possible_mn)

    cost = float(MIN_PRICE)
    new_price = coin_price
    for i in range(MIN_PRICE, num_mn_for_attack * DASH_MN_COLLATERAL):
        cost += new_price
        new_price += exp_incr
    new_num_frozen = frozen + num_mn_for_attack * DASH_MN_COLLATERAL
    new_remaining = coins - new_num_frozen
    new_num_mn = active_mn + num_mn_for_attack
    new_possible_mn = math.floor(int(new_remaining // DASH_MN_COLLATERAL))
    percentage_malicious = str(float((num_mn_for_attack / new_num_mn) * PERCENTAGE))[0:4]

    p = "POSSIBLE!"
    im = "IMPOSSIBLE!"
    attack_outcome = p if new_remaining >= MIN_REMAINING else im
    print("\n    --  PURCHASE OUTCOME:", attack_outcome, " --")
    if attack_outcome == im:
        print(
            "WHY: The reason is because the coins required for this purchase are not enough as\n     "
            "they exceed the total available coin supply!")
    print("New Dash Price after this investment: £" + "{0:.2f}".format(new_price))
    print("Total Cost of Purchase (including dynamic price increase): £" + "{0:.3f}".format(cost))
    print("Coins in circulations after purchase:", coins)
    print("From which coins frozen for required collateral:", new_num_frozen) if attack_outcome == p else print(
        "From which coins frozen for required collateral:", new_num_frozen, "<------ (Problematic Result)")

    print("Therefore, coins remaining unfrozen:", "{0:.3f}".format(new_remaining),
          "<------ (Problematic Result)") if attack_outcome == im \
        else print("Therefore, coins remaining unfrozen:", new_remaining,
                   "\nWhich are enough to acquire more Master Nodes, actually:", new_possible_mn, "Master Nodes",
                   "\nWhich as a percentage, takes this share from the total active Master Nodes: " +
                   percentage_master_nodes + "%",
                   "\nThis percentage is high, but not enough to achieve a net 10% over honest Master Nodes")

    print("Active Master Nodes after purchase:", new_num_mn,
          "\nFrom which malicious:", num_mn_for_attack, "(" + percentage_malicious + "%)",
          "\nTherefore, the honest nodes have the net majority!") if attack_outcome == p \
        else print("The available coin supply was enough to buy this amount of Master Nodes:", possible_mn,
                   "Master Nodes", "<------ (Problematic Result)", "\nBut we requested the purchase of",
                   num_mn_for_attack, "Master Nodes", "<------ (Problematic Result)")

    anti_dos_poss = math.floor(num_mn_for_attack * NET_10_PERCENT) + ONE_MN
    anti_dos_needed = math.ceil(possible_mn * NET_10_PERCENT) + ONE_MN
    approved_anw = math.ceil(num_mn_for_attack / NET_10_PERCENT) - ONE_MN
    avg_mn_votes = math.floor(active_mn * SIXTY_PERCENT)
    net_10_anw = math.floor(avg_mn_votes * NET_10_PERCENT) + ONE_MN
    negligence_out = "YES!" if num_mn_for_attack >= net_10_anw or (num_mn_for_attack + new_possible_mn) >= net_10_anw \
        else "NO!"
    total_rem = TOTAL_SUPPLY - coins
    total_rem_mn = math.floor(int(total_rem // DASH_MN_COLLATERAL))
    percentage_total_master_nodes = str(float((coins / TOTAL_SUPPLY) * PERCENTAGE))[0:4]
    c2019 = 8761092
    c2020 = 9486800
    c2021 = 10160671
    mn2019 = math.floor(int((c2019 - coins) // DASH_MN_COLLATERAL))
    mn2020 = math.floor(int((c2020 - coins) // DASH_MN_COLLATERAL))
    mn2021 = math.floor(int((c2021 - coins) // DASH_MN_COLLATERAL))

    print("\n    --  PROCEEDING TO PLAN B: WHAT PROBLEMS CAN WE CAUSE RIGHT NOW?  --")
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
    print("Current supply (% against total): ", coins, "(" +
          percentage_total_master_nodes + "%)")
    print("Total (ever) coin supply:", TOTAL_SUPPLY)
    print("Remaining Supply/Possible new Master Nodes:", total_rem, "/", total_rem_mn)
    print("Below is the minimum number of coins expected per year along with (%) against total coin supply:")
    print("Expected minted coins until 04/2019(%)/Possible new Master Nodes:", c2019, "(46.3%)", "/", mn2019)
    print("Expected minted coins until 04/2020(%)/Possible new Master Nodes:", c2020, "(50.14%)", "/", mn2020)
    print("Expected minted coins until 04/2021(%)/Possible new Master Nodes:", c2021, "(53.7%)", "/", mn2021)
    print("Furthermore: 08/2029 (74.41%), 03/2043 (90.23%), 05/2073 (98.86%), 04/2150 (100%)")
    print("""SUGGESTED APPROACH:
A stealthy attacker can slowly increase his/her army assuming a percentage gain of
50% mined DASH => Master Nodes per year. Towards this DASH required, the attacker might
use Proof-of-Service rewards able to purchase 25 new Master Nodes per existing Master Nodes per year
(assuming 7.14% Return on Investment). An increase of 1K Master Nodes could take 4-5 years
to be achieved and does not guarantee success! Notice that in the long term, more
years would be needed to acquire further 1K Master Nodes!
""")


# This is the main method of the program, responsible for IO using the above methods.
def main():
    intro()

    while True:
        budget = input('Attack Budget (£):  (press enter for enough budget to be successful)  ')
        coin_price = input('Dash Price (£):  (press enter for real time price)  ')
        exp = input('Price Increase Factor (1-10)(1: Aggressive, 10: Slow):  (press enter for default factor)  ')
        active_mn = input('Total of Active Master Nodes:  (press enter for real time active Master Nodes)  ')
        coins = input('Coins in Circulation:  (press enter for real time circulation)  ')
        mn_controlled = input('Master Nodes already under control or bribe?:  (press enter for none)  ')
        mn_target = input('Target Total Master Nodes:  (press enter for enough to be successful)  ')

        try:
            real_time_data = acquire_real_time_data()
            real_time_price = real_time_data[0]
            real_time_circulation = real_time_data[1]
            budget = float(budget) if budget else MIN_BUDGET
            coin_price = float(coin_price) if coin_price else real_time_price
            exp = float((int(exp) + SANITISE) * INVERSE) if exp and (MIN_PRICE < int(exp) < MAX_EXP) else float(DEF_EXP)
            exp_incr = math.pow(math.e, exp)
            active_mn = int(active_mn) if active_mn else acquire_real_time_mn_number()
            coins = int(coins) if coins else real_time_circulation
            mn_controlled = int(mn_controlled) if mn_controlled else MIN_MN
            number_of_possible_masternodes = math.floor(int(coins // DASH_MN_COLLATERAL))
            mn_target = int(mn_target) \
                if mn_target and mn_controlled < int(mn_target) <= number_of_possible_masternodes \
                else int(math.ceil(active_mn * NET_10_PERCENT)) + ONE_MN
            break
        except ValueError:
            print()
            pass

    report(budget, coin_price, exp_incr, active_mn, coins, mn_controlled, mn_target)
    print()


main()
