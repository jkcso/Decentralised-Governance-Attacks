# Run in Python3.6

from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from urllib.request import Request, urlopen
import json
import os
import ssl
import math

"""
CAPABILITIES:
    Using this simulator, an attacker is able to control the following parameters to make
    an attacking scenario against Dash Decentralised Governance fully customised, or proceed
    with the real time values of the following parameters:
        1) Attack Budget (£)
        2) Dash Price (£)
        3) Price Increase Factor
        4) Total of Active Master Nodes
        5) Coins in Circulation
        6) Number of Master Nodes already in possession
        
IMPORTANT:
    Here, what we are trying to achieve is a Proof of Concept regarding the attack
    discussed.  We therefore try to evaluate how likely it is at any given time, 
    and not how costly.
    Having said that, the dynamic price calculation is here to provide a more realistic
    environment, but abstracts away from necessary but uncontrolled parameters such as 
    the reasons on why a coin's price might fall, including government rumours about it.
"""


def intro():
    print("""
    --  DASH CORRUPTED GOVERNANCE ATTACK SIMULATOR  --
    --  Please provide customised information for any parameter OR
    --  Press enter to proceed with the real time values  --
    """)


def acquire_real_time_price():
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            'start': '1',
            'limit': '20',
            'convert': 'GBP'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)

            real_time_price = 0

            for i in range(1, 20):
                if data['data'][i]['name'] == 'Dash':
                    real_time_price = data['data'][i]['quote']['GBP']['price']
            return float("{0:.2f}".format(real_time_price))

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)
    except ValueError:
        pass


def acquire_real_time_circulation():
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
            'start': '1',
            'limit': '20',
            'convert': 'GBP'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'c5b33796-bb72-46c2-98eb-ac52807d08c9'
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)

            real_time_circulation = 0

            for i in range(1, 20):
                if data['data'][i]['name'] == 'Dash':
                    real_time_circulation = data['data'][i]['circulating_supply']
            return int(real_time_circulation)

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
def report(budget, coin_price, exp_incr, active_mn, coins, mn_controlled):
    print()
    print("    --  VALUES PROCEEDING WITH  --")
    print("Attack Budget: Equals total cost as estimated below") if budget == 0\
        else print("Attack Budget: £" + str(budget))
    print("Dash Price: £" + str(coin_price))
    print("Dash Price Increase Factor (in Decimal):", exp_incr)
    print("Number of Active Master Nodes:", active_mn)
    print("Coins in circulation:", coins)
    print("Master Nodes already under control or bribe:", mn_controlled)


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


def buy_x_mn(budget, coin_price, exp_incr, active_mn, coins, mn_controlled):
    num_mn = int(math.ceil(active_mn * 1.1)) + 1
    collateral_req = 1000
    frozen = collateral_req * active_mn
    remaining_coins = coins - frozen
    possible_mn = math.floor(int(remaining_coins // collateral_req))
    percentage_master_nodes = str(float((possible_mn / active_mn) * 100))[0:4]

    print("\n    --  ATTEMPTING TO PURCHASE", num_mn, "MASTER NODES  --")
    print("Dash Price before purchase: £" + str(coin_price))
    print("Active Master Nodes before purchase:", active_mn)
    print("Coins in circulations before purchase:", coins)
    print("From which coins frozen for required collateral:", frozen)
    print("Therefore, coins remaining unfrozen:", remaining_coins)
    print("These are enough to get us more Master Nodes, actually up to this number:", possible_mn)

    cost = float(0)
    new_price = coin_price
    for i in range(0, num_mn * collateral_req):
        cost += new_price
        new_price += exp_incr
    new_num_frozen = frozen + num_mn * collateral_req
    new_remaining = coins - new_num_frozen
    new_num_mn = active_mn + num_mn
    total_supply = 18900000
    new_possible_mn = math.floor(int(new_remaining // collateral_req))
    percentage_malicious = str(float((num_mn / new_num_mn) * 100))[0:4]

    p = "POSSIBLE!"
    im = "IMPOSSIBLE!"
    attack_outcome = p if new_remaining >= 0 else im
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
          "\nFrom which malicious:", num_mn, "(" + percentage_malicious + "%)",
          "\nTherefore, the honest nodes have the net majority!") if attack_outcome == p\
        else print("The available coin supply was enough to buy this amount of Master Nodes:", possible_mn,
                   "Master Nodes", "<------ (Problematic Result)", "\nBut we requested the purchase of", num_mn,
                   "Master Nodes", "<------ (Problematic Result)")

    anti_dos_poss = math.floor(num_mn * 1.1) + 1
    anti_dos_needed = math.ceil(possible_mn * 1.1) + 1
    approved_anw = math.ceil(num_mn / 1.1) - 1
    avg_mn_votes = math.floor(active_mn * 0.6)
    net_10_anw = math.floor(avg_mn_votes * 1.1) + 1
    negligence_out = "YES!" if num_mn >= net_10_anw or (num_mn + new_possible_mn) >= net_10_anw else "NO!"
    total_rem = total_supply - coins
    total_rem_mn = math.floor(int(total_rem // collateral_req))
    percentage_total_master_nodes = str(float((coins / total_supply) * 100))[0:4]
    c2019 = 8761092
    c2020 = 9486800
    c2021 = 10160671
    mn2019 = math.floor(int((c2019 - coins) // collateral_req))
    mn2020 = math.floor(int((c2020 - coins) // collateral_req))
    mn2021 = math.floor(int((c2021 - coins) // collateral_req))

    print("\n    --  PROCEEDING TO PLAN B: WHAT PROBLEMS CAN WE CAUSE RIGHT NOW?  --")
    print("1) Prevent honest proposals to go through! (i.e: The salaries of Dash Core Developers)")
    print("Explanation: We vote 'no' for a proposal and we hope that net 10% can't be achieved!")

    if attack_outcome == p:
        print("The number of Master Nodes we acquired above is:", num_mn, "Master Nodes")
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
        print("With this amount of Master Nodes under our control, which is:", num_mn, "Master Nodes")
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
        print("WHY: Total number of malicious Master Nodes will become:", num_mn + new_possible_mn, "Master Nodes")
        print("     and we previously needed at least this amount for majority:", net_10_anw, "Master Nodes")

    print("\n3) Maintain a stealthy future")
    print("Current supply (% against total): ", coins, "(" +
          percentage_total_master_nodes + "%)")
    print("Total (ever) coin supply:", total_supply)
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
        coins = input('Coins in Circulation (in Millions):  (press enter for real time circulation)  ')
        mn_controlled = input('How many Master Nodes already under control or bribe?:  (press enter for none)  ')

        try:
            budget = float(budget) if budget else 0
            coin_price = float(coin_price) if coin_price else acquire_real_time_price()
            exp = float((int(exp) + 5) * -1) if exp and (0 < int(exp) < 11) else float(-11.4)
            exp_incr = math.pow(math.e, exp)
            active_mn = int(active_mn) if active_mn else acquire_real_time_mn_number()
            coins = int(coins) if coins else acquire_real_time_circulation()
            mn_controlled = int(mn_controlled) if mn_controlled else 0
            break
        except ValueError:
            print()
            pass

    report(budget, coin_price, exp_incr, active_mn, coins, mn_controlled)
    buy_x_mn(budget, coin_price, exp_incr, active_mn, coins, mn_controlled)
    print()


main()
