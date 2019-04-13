# *** RUN IT USING PYTHON >= 3.6 ***

from coinmarketcap import Market
from urllib.request import Request, urlopen
import json
import math

"""
CAPABILITIES:
    Using this simulator, an attacker is able to control the following parameters to make
    an attacking scenario against Dash Decentralised Governance fully customised, or proceed
    with the real time values of the following parameters:
        1) Dash Price($)
        2) Price Increase Factor
        3) Number of Active Master Nodes
        4) Coins in Circulation
        5) How many Master Nodes to control after purchasing them.
        
IMPORTANT:
    Here, what we are trying to achieve is a Proof of Concept regarding the attack
    discussed.  We therefore try to evaluate how likely it is at any given time, 
    and not how costly.
    Having said that, the dynamic price calculation is here to provide a more realistic
    environment, but abstracts away from necessary but uncontrolled parameters such as 
    the reasons on why a coin's price might fall, including government rumours about it.
"""


# Outputs the values we proceed during the simulation.
def report(price, exp_incr, mn, coins):
    print()
    print("    --  VALUES PROCEEDING WITH  --")
    print("Price: $" + str(price))
    print("Price Increase Factor (in Decimal):", exp_incr)
    print("Number of Active Master Nodes:", mn)
    print("Coins in circulation:", coins)


"""
Proceeds to the purchase of X Master Nodes and then analyses the newly created situation,
providing also possible scenarios on how attackers and defenders might proceed.
Example:
    We purchase X=10 Master Nodes.  Each requires a collateral of 1K DASH, therefore
    we would need 10K DASH.  If 1 DASH costs $300, then the final cost of investment
    due to the dynamic price increase would be $3000559.71 and the new DASH price will
    increase to $300.11.
    Then we generate statistics on how successful the attacker can be by controlling this
    X amount of Master Nodes and we provide further options on how to proceed that are able
    to help both attacking and defending parties for one step forward, always ethically.
"""


def buy_x_mn(num, coin_price, exp_incr, coins, mn):
    collateral_req = 1000
    frozen = collateral_req * mn
    remaining_coins = coins - frozen
    possible_mn = math.floor(int(remaining_coins // collateral_req))
    percentage_master_nodes = str(float((possible_mn / mn) * 100))[0:4]

    print("\n    --  PROCEEDING TO THE PURCHASE OF", num, "MASTER NODES  --")
    print("Dash Price before purchase: $" + str(coin_price))
    print("Active Master Nodes before purchase:", mn)
    print("Coins in circulations before purchase:", coins)
    print("From which coins frozen for required collateral:", frozen)
    print("Therefore, coins remaining unfrozen:", remaining_coins)
    print("These are enough to get us more Master Nodes, actually up to this number:", possible_mn)

    cost = float(0)
    new_price = coin_price
    for i in range(0, num * collateral_req):
        cost += new_price
        new_price += exp_incr
    new_num_frozen = frozen + num * collateral_req
    new_remaining = coins - new_num_frozen
    new_num_mn = mn + num
    total_supply = 18900000
    new_possible_mn = math.floor(int(new_remaining // collateral_req))
    percentage_malicious = str(float((num / new_num_mn) * 100))[0:4]

    p = "POSSIBLE!"
    im = "IMPOSSIBLE!"
    attack_outcome = p if new_remaining >= 0 else im
    print("\n    --  PURCHASE OUTCOME:", attack_outcome, " --")
    if attack_outcome == im:
        print(
            "WHY: The reason is because the coins required for this purchase are not enough as\n     they exceed the "
            "total available coin supply!")
    print("New Dash Price after this investment: $" + str(new_price)[0:8])
    print("Total Cost of Purchase (including dynamic price increase): $" + str(cost))
    print("Coins in circulations after purchase:", coins)
    print("From which coins frozen for required collateral:", new_num_frozen) if attack_outcome == p else print(
        "From which coins frozen for required collateral:", new_num_frozen, "<------ (Problematic Result)")
    print("Therefore, coins remaining unfrozen:", new_remaining,
          "<------ (Problematic Result)") if attack_outcome == im else print("Therefore, coins remaining unfrozen:",
                                                                             new_remaining,
                                                                             "\nWhich are enough to acquire more Master"
                                                                             " Nodes, actually:",
                                                                             new_possible_mn, "Master Nodes",
                                                                             "\nWhich as a percentage, takes this "
                                                                             "share from the total active Master Nodes:"
                                                                             + " " + percentage_master_nodes + "%",
                                                                             "\nThis percentage is high, but not "
                                                                             "enough to achieve a net 10% over honest "
                                                                             "Master Nodes")
    print("Active Master Nodes after purchase:", new_num_mn, "\nFrom which malicious:", num, "(" + percentage_malicious
          + "%)",
          "\nTherefore, the honest nodes have the net majority!") if attack_outcome == p else print(
        "The available coin supply was enough to buy this amount of Master Nodes:", possible_mn, "Master Nodes",
        "<------ (Problematic Result)", "\nBut we requested the purchase of", num, "Master Nodes",
        "<------ (Problematic Result)")

    anti_dos_poss = math.floor(num * 1.1) + 1
    anti_dos_needed = math.ceil(possible_mn * 1.1) + 1
    approved_anw = math.ceil(num / 1.1) - 1
    avg_mn_votes = math.floor(mn * 0.6)
    net_10_anw = math.floor(avg_mn_votes * 1.1) + 1
    negligence_out = "YES!" if num >= net_10_anw or (num + new_possible_mn) >= net_10_anw else "NO!"
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
        print("The number of Master Nodes we acquired above is:", num, "Master Nodes")
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
        print("With this amount of Master Nodes under our control, which is:", num, "Master Nodes")
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
        print("WHY: Total number of malicious Master Nodes will become:", num + new_possible_mn, "Master Nodes")
        print("     and we previously needed at least this amount for majority:", net_10_anw, "Master Nodes")

    print("\n3) Maintain a stealthy future")
    print("Current supply (% against total): ", coins, "(" + percentage_total_master_nodes + "%)")
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

    return cost, new_price


# This is the main method of the program, responsible for IO using the above methods.
def main():
    print("""
    --  DASH CORRUPTED GOVERNANCE ATTACK SIMULATOR  --
    --  Please provide customised information for any parameter OR
    --  Press enter to proceed with the real time values  --
    """)

    # Retrieves Dash real time data.
    cmc = Market()
    coins = cmc.ticker(limit=20)
    dash = ''
    for i in range(0, 20):
        if coins[i]['id'] == 'dash':
            dash = coins[i]
            break

    # Retrieves master nodes real time data.
    mn_stats = 'https://stats.masternode.me/network-report/latest/json'
    req_stats = Request(mn_stats, headers={'User-Agent': 'Mozilla/5.0'})
    stats = json.loads(urlopen(req_stats).read().decode("utf-8"))

    i = 1  # Keep looping with same questions unless data in correct form is provided.
    while True:
        price = input('Customised Price($): (press enter for real time price) ')
        exp = input('Price Increase Factor (1-10)(1: Aggressive, 10: Slow): (press enter for default factor) ')
        mn = input('Number of Active Master Nodes:  (press enter for real time active Master Nodes) ')
        coins = input('Coins in Circulation (in Millions):  (press enter for real time circulation) ')
        num_mn = input('How many master nodes you want to control?:  (press enter for net 10% malicious Master Nodes) ')

        try:
            price = float(price) if price else float(dash['price_usd'])
            exp = float((int(exp) + 5) * -1) if exp and (0 < int(exp) < 11) else float(-11.4)
            exp_incr = math.pow(math.e, exp)
            mn = int(mn) if mn else stats["raw"]["mn_count"]
            coins = float(coins * 1000000) if coins else float(dash['available_supply'])
            num_mn = int(num_mn) if num_mn else int((mn * 1.1) + 1)
            break
        except ValueError:
            pass

    while i <= price:
        ...
        i += 1

    report(price, exp_incr, mn, coins)
    cost, new_price = buy_x_mn(num_mn, price, exp_incr, coins, mn)
    print()


main()
