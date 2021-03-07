import os

from instauto.api.actions import profile
from instauto.api.client import ApiClient
from time import sleep
from datetime import datetime
from account import LOGIN, PASSWORD

def main():
    if os.path.isfile('./.instauto.save'):
        client = ApiClient.initiate_from_file('./.instauto.save')
    else:
        client = ApiClient(user_name=LOGIN, password=PASSWORD)
        client.login()
        client.save_to_disk('./.instauto.save')

    while True:
        change_biography(client)


def change_biography(client):
    current_time = datetime.utcnow()
    wait_time = current_time.replace(hour=(current_time.hour+1)%24, minute=0, second=0, microsecond=0)
    delay = (wait_time - current_time).seconds + 2

    p = profile.SetBiography(time_lived())
    client.profile_set_biography(p)
    print(datetime.utcnow(), delay)
    sleep(delay)


def time_lived():
    format = "%Y-%m-%d %H"
    birthday = "2005-11-10 00"
    birth_date = datetime.strptime(birthday, format)

    current_date = datetime.strptime(datetime.utcnow().strftime(format), format)
    last_birth_date = datetime.strptime(f"{current_date.year - 1}{birthday[4:]}", format)

    years = current_date.year - birth_date.year - 1
    if (current_date.month == 11 and current_date.day > 9) or current_date.month > 11:
        years += 1

    days = (current_date - last_birth_date).days
    days %= 366 if current_date.year % 4 == 0 and (current_date.year % 100 != 0 or current_date.year % 400 == 0) else 365

    hours = current_date.hour + 2
    if 10 > current_date.month > 3:
        hours += 1
    elif (current_date.month == 10 and current_date.day < 25) or (current_date.month == 3 and current_date.day > 28):
        hours += 1
    hours %= 24

    facts = {
        "0": "It's my birthday today!☺️ 🎈",
        "96": "Happy Valentine's Day!💘 L🦋",
        "118": "International Women's Day March 8 congratulations! 🌸🌹🦋", # 0 chars left
        "364": "Wow💥, my page bio is being changed automatically!🤖💻😎 ", # 1 char left
        "365": "This year is a leap year!"
    }

    try:
        print(days)
        daily_quote = str(facts[str(days)]) + "\n"
    except Exception:
        daily_quote = ""

    hobbies = "Coding👨💻\nKitesurfing 🏄\nFootball⚽\nMath🔢🤔\nChemistry \nPhysics ⚛\nSkiing⛷"

    return f"Alive for: {years}y {days}d {hours}h\n{daily_quote}{hobbies}"


if __name__ == '__main__':
    main()
