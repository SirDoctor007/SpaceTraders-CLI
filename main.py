import requests
import json
import configparser
from prettytable import PrettyTable


def check_game_status():
    response = requests.get("https://api.spacetraders.io/game/status")
    print(response.status_code)
    print(response.json())


def get_user_details():
    config = configparser.ConfigParser()
    config.read('config.ini')
    headers = {'Authorization': f'Bearer {config["DETAILS"]["token"]}'}

    response = requests.get(f'https://api.spacetraders.io/users/{config["DETAILS"]["username"]}', headers=headers)

    return response.json()


def view_marketplace():
    config = configparser.ConfigParser()
    config.read('config.ini')
    headers = {'Authorization': f'Bearer {config["DETAILS"]["token"]}'}

    user_details = get_user_details()
    current_locations = []

    for ship in user_details['user']['ships']:
        current_locations.append(ship['location'])

    if len(current_locations) == 1:
        view_location = current_locations[0]
    else:
        while True:
            for num, loc in enumerate(current_locations, 1):
                print(f'{num}) {loc}')
            try:
                ans = int(input('Select a location: '))
                if 0 < ans < len(current_locations) + 1:
                    view_location = current_locations[ans-1]
                    break
                else:
                    raise ValueError
            except ValueError:
                print('That is not a valid answer.')

    response = requests.get(f'https://api.spacetraders.io/game/locations/{view_location}/marketplace', headers=headers)
    results = response.json()

    if 'location' in results.keys():
        t = PrettyTable()
        t.field_names = ['Symbol', 'Volume/Unit', 'Price/Unit', 'Quantity Available']

        for item in results['location']['marketplace']:
            t.add_row([item['symbol'], item['volumePerUnit'], item['pricePerUnit'], item['quantityAvailable']])

        print(f'Location: {view_location}')
        print(t)
    elif 'error' in results.keys():
        print(f'There was an error: {results["error"]["message"]}')
        print(f'Code: {results["error"]["code"]}')
    else:
        print('Something Went wrong. Good Luck...')

    return 0


def view_locations():
    config = configparser.ConfigParser()
    config.read('config.ini')
    headers = {'Authorization': f'Bearer {config["DETAILS"]["token"]}'}
    response = requests.get('https://api.spacetraders.io/game/systems/OE/locations?type=MOON', headers=headers)
    results = response.json()

    t = PrettyTable()
    t.field_names = ['Symbol', 'Type', 'Name', 'Cords']

    for location in results['locations']:
        t.add_row([location['symbol'], location['type'], location['name'], f'{location["x"]}, {location["y"]}'])

    print(t)

    return 0


def create_flight_plan(ship_id, destination):
    data = {'shipId': ship_id, 'destination': destination}

    config = configparser.ConfigParser()
    config.read('config.ini')
    headers = {'Authorization': f'Bearer {config["DETAILS"]["token"]}'}
    response = requests.post(f'https://api.spacetraders.io/users/{config["DETAILS"]["username"]}/flight-plans',
                             headers=headers, data=data)
    results = response.json()
    print(results)

    return 0


def place_purchase_order(ship_id, good, quantity):
    config = configparser.ConfigParser()
    config.read('config.ini')
    headers = {'Authorization': f'Bearer {config["DETAILS"]["token"]}'}

    user_details = get_user_details()
    location = user_details["user"]["ships"][0]["location"]
    market_data = requests.get(f'https://api.spacetraders.io/game/locations/{location}/marketplace', headers=headers).json()

    t = PrettyTable()
    t.field_names = ['Index', 'Symbol', 'Volume/Unit', 'Price/Unit', 'Quantity Available']

    for pos, item in enumerate(market_data['location']['marketplace'], 1):
        t.add_row([pos, item['symbol'], item['volumePerUnit'], item['pricePerUnit'], item['quantityAvailable']])

    while True:
        # TODO Finish This
        print(f'Ship:\n'
              f'Location: {location}')
        print(t)

        try:
            ans = int(input('Enter the index number of the item you wold like to purchase.\n--> '))
            if 0 < ans <= len(market_data['location']['marketplace']):
                try:
                    quantity = int(input('Enter the quantity to purchase.\n--> '))
                    if 0 < quantity <= market_data['location']['marketplace'][ans-1]['quantityAvailable']:
                        break
                    else:
                        raise ValueError
                except ValueError:
                    print('That is not a valid answer.')
            else:
                raise ValueError
        except ValueError:
            print('That is not a valid answer.')

    item = market_data['location']['marketplace'][ans-1]['symbol']
    current_balance = user_details["user"]["credits"]
    cost_of_purchase = quantity * market_data['location']['marketplace'][ans-1]['pricePerUnit']
    print(f'Current Balance: {current_balance}\n'
          f'Cost of Purchase: {cost_of_purchase}\n'
          f'Balance after Purchase: {current_balance - cost_of_purchase}')
    print(f'This would have purchased "{quantity}" units of "{item}".')
    # response = requests.post(f'https://api.spacetraders.io/users/{config["DETAILS"]["username"]}/purchase-orders',
    #                          headers=headers, data=data)


def place_sell_order(ship_id, good, quantity):
    data = {'shipId': ship_id, 'good': good, 'quantity': quantity}

    config = configparser.ConfigParser()
    config.read('config.ini')
    headers = {'Authorization': f'Bearer {config["DETAILS"]["token"]}'}
    response = requests.post(f'https://api.spacetraders.io/users/{config["DETAILS"]["username"]}/sell-orders',
                             headers=headers, data=data)

    results = response.json()
    print(results)


def setup_config():

    username = input("Please enter your username: ")
    token = input("Please enter your token: ")

    config = configparser.ConfigParser()
    config['DETAILS'] = {'username': username,
                         'token': token}

    with open('config.ini', 'w') as f:
        config.write(f)


if __name__ == "__main__":

    while True:
        print('1) Get User Details')
        print('2) View Marketplace')
        print('3) View Locations')
        print('4) Place an Purchase Order')
        print('6) Place an Sell Order')


        ans = int(input("--> "))

        if ans == 1:
            print(get_user_details())
        elif ans == 2:
            view_marketplace()
        elif ans == 3:
            view_locations()
        elif ans == 4:
            place_purchase_order('ckmlw859a92827615s6rn13s6g7', 'SHIP_PARTS', '16')
        elif ans == 5:
            create_flight_plan('ckmlw859a92827615s6rn13s6g7', 'OE-PM-TR')
        elif ans == 6:
            place_sell_order('ckmlw859a92827615s6rn13s6g7', 'SHIP_PARTS', '16')
    # setup_config()
    # get_user_details()
    # view_marketplace()
    # view_locations()