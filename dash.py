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
        3) Number of Active Masternodes
        4) Coins in Circulation
        5) How many masternodes to control after purchasing them.
        
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
    print("Number of Active Masternodes:", mn)
    print("Coins in circulation:", coins)


"""
Proceeds to the purchase of X Masternodes and then analyses the newly created situation,
providing also possible scenarios on how attackers and defenders might proceed.
Example:
    We purchase X=10 Masternodes.  Each requires a collateral of 1K DASH, therefore
    we would need 10K DASH.  If 1 DASH costs $300, then the final cost of investment
    due to the dynamic price increase would be $3000559.71 and the new DASH price will
    increase to $300.11.
    Then we generate statistics on how successful the attacker can be by controlling this
    X amount of Masternodes and we provide further options on how to proceed that are able
    to help both attacking and defending parties for one step forward, always ethically.
"""


def buy_X_MN(num, coin_price, exp_incr, coins, mn):
    collateral_req = 1000
    freezed = collateral_req * mn
    remaining_coins = coins - freezed
    possible_mn = math.floor(int(remaining_coins // collateral_req))
    perc_mn = str(float((possible_mn / mn) * 100))[0:4]

    print("\n    --  PROCEEDING TO THE PURCHASE OF", num, "MN  --")
    print("Dash Price before purchase: $" + str(coin_price))
    print("Active Masternodes before purchase:", mn)
    print("Coins in circulations before purchase:", coins)
    print("From which coins frozen for required collaterals:", freezed)
    print("Therefore, coins remaining unfrozen:", remaining_coins)
    print("These are enough to get us more MN, actually up to this number:", possible_mn)

    cost = float(0)
    new_price = coin_price
    for i in range(0, num * collateral_req):
        cost += new_price
        new_price += exp_incr
    new_num_freezed = freezed + num * collateral_req
    new_remaining = coins - new_num_freezed
    new_num_mn = mn + num
    total_supply = 18900000
    new_possible_mn = math.floor(int(new_remaining // collateral_req))
    perc_mal = str(float((num / new_num_mn) * 100))[0:4]

    p = "POSSIBLE!"
    im = "IMPOSSIBLE!"
    attack_outcome = p if new_remaining >= 0 else im
    print("\n    --  PURCHASE OUTCOME:", attack_outcome, " --")
    if attack_outcome == im: print(
        "WHY: The reason is because the coins required for this purchase are not enough as\n     they exceed the "
        "total available coin supply!")
    print("New Dash Price after this investment: $" + str(new_price)[0:8])
    print("Total Cost of Purchase (including dynamic price increase): $" + str(cost))
    print("Coins in circulations after purchase:", coins)
    print("From which coins frozen for required collaterals:", new_num_freezed) if attack_outcome == p else print(
        "From which coins frozen for required collaterals:", new_num_freezed, "<------ (Problematic Result)")
    print("Therefore, coins remaining unfrozen:", new_remaining,
          "<------ (Problematic Result)") if attack_outcome == im else print("Therefore, coins remaining unfrozen:",
                                                                             new_remaining,
                                                                             "\nWhich are enough to acquire more MN, "
                                                                             "actually:",
                                                                             new_possible_mn, "MN",
                                                                             "\nWhich as a percentage, takes this "
                                                                             "share from the total active MN: " +
                                                                             perc_mn + "%",
                                                                             "\nThis percentage is high, but not "
                                                                             "enough to achieve a net 10% over honest "
                                                                             "masternodes")
    print("Active Masternodes after purchase:", new_num_mn, "\nFrom which malicious:", num, "(" + perc_mal + "%)",
          "\nTherefore, the honest nodes have the net majority!") if attack_outcome == p else print(
        "The available coin supply was enough to buy this amount of MN:", possible_mn, "MN",
        "<------ (Problematic Result)", "\nBut we requested the purchase of", num, "MN", "<------ (Problematic Result)")

    anti_dos_poss = math.floor(num * 1.1) + 1
    anti_dos_needed = math.ceil(possible_mn * 1.1) + 1
    approved_anw = math.ceil(num / 1.1) - 1
    avg_mn_votes = math.floor(mn * 0.6)
    net_10_anw = math.floor(avg_mn_votes * 1.1) + 1
    negligence_out = "YES!" if num >= net_10_anw or (num + new_possible_mn) >= net_10_anw else "NO!"
    total_rem = total_supply - coins
    total_rem_mn = math.floor(int(total_rem // collateral_req))
    perc_total_mn = str(float((coins / total_supply) * 100))[0:4]
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
        print("The number of MN we acquired above is:", num, "MN")
        print("This means that for a proposal to get accepted, it would need this number of positive votes:",
              anti_dos_poss, "MN")

    print("Maximum possible amount of MN we can acquire due to coins in circulation is:", possible_mn, "MN")
    print("It means that for a proposal to get accepted, it would need these positive votes:", anti_dos_needed, "MN")
    print("WHY: Anything below the required amount of votes will cause a proposal rejection.")

    print("\n2) Acts of Negligence -- Achievable?", negligence_out)
    print("Explanation: We vote 'yes' for a proposal and we hope in a high % of voting absention!")

    if attack_outcome == p:
        print("With this amount of MN under our control, which is:", num, "MN")
        print("A budget proposal will be approved even if this number of honest MN votes against:", approved_anw, "MN")

    print("Given that the maximum votes ever recorded for funding a proposal is: 2147 MN (44.47%)")
    print(
        "Assuming that a controversial proposal will drastically increase this,\nwe will consider a higher percentage "
        "of 60% voters, this means: ",
        avg_mn_votes, "MN")
    print("Which means that we would need this amount of MN to achieve net 10%:", net_10_anw, "MN")
    print("Maximum possible amount of MN we can acquire due to coins in circulation is:", possible_mn, "MN")

    if attack_outcome == p:
        print("Remember that the remaining coins are enough to acquire more MN, actually:", new_possible_mn, "MN")
        print("OUTCOME: If we acquire them, then we achieve net 10% in case that 60% of honest MN vote.")
        print("WHY: Total number of malicious masternodes will become:", num + new_possible_mn, "MN")
        print("     and we previously needed at least this amount for majority:", net_10_anw, "MN")

    print("\n3) Maintain a stealthy future")
    print("Current supply (% against total): ", coins, "(" + perc_total_mn + "%)")
    print("Total (ever) coin supply:", total_supply)
    print("Remaining Supply/Possible new MN:", total_rem, "/", total_rem_mn)
    print("Below is the minimum number of coins expected per year along with (%) against total coin supply:")
    print("Expected minted coins until 04/2019(%)/Possible new MN:", c2019, "(46.3%)", "/", mn2019)
    print("Expected minted coins until 04/2020(%)/Possible new MN:", c2020, "(50.14%)", "/", mn2020)
    print("Expected minted coins until 04/2021(%)/Possible new MN:", c2021, "(53.7%)", "/", mn2021)
    print("Furthermore: 08/2029 (74.41%), 03/2043 (90.23%), 05/2073 (98.86%), 04/2150 (100%)")
    print("""SUGGESTED APPROACH:
A stealthy attacker can slowly increase his/her army assuming a percentage gain of
50% mined DASH => MN per year. Towards this DASH required, the attacker might
use Proof-of-Service rewards able to purchase 25 new MN per existing MN per year
(assuming 7.14% Return on Investment). An increase of 1K MN could take 4-5 years
to be achieved and does not guarantee success! Notice that in the long term, more
years would be needed to acquire further 1K MN!
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
        mn = input('Number of Active Masternodes:  (press enter for real time active MN) ')
        coins = input('Coins in Circulation (in Millions):  (press enter for real time circulation) ')
        num_mn = input('How many masternodes you want to control?:  (press enter for net 10% malicious MN) ')

        try:
            price = float(price) if price else float(dash['price_usd'])
            exp = float((int(exp) + 5) * -1) if exp and (int(exp) > 0 and int(exp) < 11) else float(-11.4)
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
    cost, new_price = buy_X_MN(num_mn, price, exp_incr, coins, mn)
    print()


main()
