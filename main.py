import code
import pycurl
from io import BytesIO
import json
import datetime
import time
import requests


session = requests.Session()
currenttime = format(datetime.datetime.now(), '%Y-%m-%d %H:%M')


TELEGRAM_API_TOKEN = "7109667763:AAHLcr8o_5r6BGEojFZrDBG_adGie_07sY8"
TELEGRAM_CHAT_ID = "1891905805"
# File to store offers data
DATA_FILE = "offers1.json"
# Function to perform the login
# Define a constant for the time interval (in seconds) between cookie validity checks
COOKIE_CHECK_INTERVAL = 25 * 60  # 25 minutes


def perform_login(login_url, login_post_data, cookie_file):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, login_url)
    c.setopt(c.COOKIEJAR, cookie_file)
    c.setopt(c.POSTFIELDS, login_post_data)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.perform()
    # Set a longer timeout (e.g., 30 seconds)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)

    # Retry up to 3 times
    retries = 3
    while retries > 0:
        try:
            c.perform()
            break  # Successful connection, exit the loop
        except pycurl.error as e:
            errno, errmsg = e.args
            print(f"Connection failed: {errmsg}. Retrying...")
            retries -= 1
            if retries == 0:
                print("Maximum retries reached. Exiting.")
                raise
    c.close()

# Function to retrieve offers data


def get_offers(offers_url, cookie_file):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, offers_url)
    c.setopt(c.COOKIEFILE, cookie_file)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.perform()
    c.close()
    response = buffer.getvalue().decode("utf-8")
    return json.loads(response).get("offer", [])

# Function to check if the PHPSESSID cookie is expired


def check_cookie_expiry(cookie_file):
    with open(cookie_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        fields = line.strip().split('\t')
        if len(fields) >= 7:
            if fields[5] == "PHPSESSID":
                expiry_timestamp = int(fields[4])
                current_timestamp = datetime.datetime.now().timestamp()
                if expiry_timestamp > current_timestamp:
                    return True
                else:
                    return False
    return False


# Function to save offers data to a JSON file
def save_offers_to_file(offers_data, filename):
    with open(filename, 'w') as f:
        json.dump(offers_data, f, indent=4)


# Function to load offers data from a JSON file
def load_offers_from_file(DATA_FILE):
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise ValueError(f"Failed to send Telegram message: {response.text}")


# Main function
def main():
    # Login details
    login_url = "https://offres.passlogement.com/account/auth/login"
    login_data = {"username": "mrrguigreda@gmail.com", "password": "DkvesSE4"}
    login_post_data = "&".join(
        [f"{k}={v}" for k, v in login_data.items()]).encode('utf-8')

    # File to store cookies
    cookie_file = "cookies.txt"

    # Perform login if necessary
    if check_cookie_expiry(cookie_file):
        print("Using existing cookies for the connection.")
        login_required = False
    else:
        print("Cookies expired. Performing new login.")
        perform_login(login_url, login_post_data, cookie_file)

    # URL to retrieve offers
    offers_url = "https://offres.passlogement.com/account/offer/listing/json"

    # Initial time for cookie check
    next_cookie_check_time = time.time() + COOKIE_CHECK_INTERVAL
    print("time : ", time.time())
    # print("111111111111_next_cookie_check_time", next_cookie_check_time)
    while True:
        # Check if it's time to check the validity of cookies
        if time.time() >= next_cookie_check_time:
            print("Checking if cookies are still valid...")
            if not check_cookie_expiry(cookie_file):
                print("Cookies expired. Performing new login.")
                perform_login(login_url, login_post_data, cookie_file)
            else:
                print("Cookies are still valid.")

            # Update the time for the next cookie check
            next_cookie_check_time += COOKIE_CHECK_INTERVAL
        print("22222222222222next_cookie_check_time", next_cookie_check_time)
        print("Checking for new offers...")

        # Load old offers from file
        old_offers = load_offers_from_file(DATA_FILE)
        print("old offers structure", type(old_offers))

        # Get the latest offers
        latest_offers = get_offers(offers_url, cookie_file)

        print("latest offers structure", type(latest_offers))
        # print("\n\n\n\n\n\nLatest offers:", latest_offers)

        # Extract IDs from old offers
        old_offer_ids = set(offer['id'] for offer in old_offers)

        # Check for new offers
        new_offers = [
            offer for offer in latest_offers if offer['id'] not in old_offer_ids]

        # Print IDs of new offers
        if new_offers:
            print("len(latest_offers) : ", len(latest_offers))
            print("New offer IDs:", new_offers)
            print(str(currenttime) + " Nouvelles offres trouvées !")
            for offer in new_offers:
                locations = offer['city']
                zipcodes = offer['zipcode']
                dalo_status = "Oui" if offer['dalo'] == "1" else "Non"
                message = f"""
                      -----
                      Special ID: {offer['specialId']}
                      Type: {offer['accommodationTypeLabel']}
                      Surface: {offer['surface']} m2
                      Rental Price: {offer['rentalPrice']} €
                      Description: {offer['description']}
                      Address: {offer['address']}
                      Zipcode: {offer['zipcode']}
                      City: {offer['city']}
                      Nb de candidats : {offer['numberCandidatesOnOffer']}
                      Dalo : {dalo_status}
                      Valid Until: {offer['dateValidity']}
                      Partner: {offer['partnerLabel']}
                      Date Created: {offer['dateCreated']}
                      Date Updated: {offer['dateUpdated']}
                      -----
                      """
                message = "**Nouvelle offre de logement à** " + \
                    locations + " " + zipcodes + "\n\n" + message
                send_telegram_message(message)
                print("Notification Telegram envoyée avec succès.")
            # Update saved offers data
            save_offers_to_file(latest_offers, DATA_FILE)
        else:
            print("No new offers found.")

        print("Offers checked at:",
              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("\n\n")

        # Sleep for 3 minute
        time.sleep(3 * 60)  # 3 minute


if __name__ == "__main__":
    main()
