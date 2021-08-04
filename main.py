import instauto.api.actions.structs.profile as pr
import instauto.api.actions.structs.post as ps
import os

from instauto.api.client import ApiClient
from time import sleep
from random import sample, choices
from pytz import timezone
from datetime import datetime
from account import LOGIN, PASSWORD


CURRENT_PICTURE = None
PICTURE_WEIGHTS = [1, 1, 1, 3]


def main():
    # Try to login using cookies stored in .instauto.save file
    try:
        client = ApiClient.initiate_from_file('./.instauto.save')
    except Exception:
        client = login()

    # Change profile biography and picture every hour and automatically relogin when cookies expire
    while True:
        try:
            change_profile(client)
        except Exception as e:
            print(e)
            client = login()


def login():
    # Login user
    client = ApiClient(username=LOGIN, password=PASSWORD)
    client.log_in()

    # Update / Create cookies in .instauto.save file
    if os.path.isfile('./.instauto.save'):
        os.remove('./.instauto.save')

    # Save updated / created cookies
    client.save_to_disk('./.instauto.save')

    return client


def change_profile(client):
    # Calculate delay (next update time - current time + 2 seconds (for confidence))
    # Just using sleep(3600) doesn't work because sleep function isn't really sleeping exactly 3600 seconds (1 hour), but a bit longer.
    # So the next update time is moved further a little. After a few days running, the delay becomes really long (several minutes) and still grows.
    # That's why we need to calculate the delay before each profile update.
    current_time = datetime.utcnow()
    update_time = current_time.replace(hour=(current_time.hour + 1) % 24, minute=0, second=0, microsecond=0)
    delay = (update_time - current_time).seconds + 2
    
    # Change profile biography and picture
    change_biography(client)
    change_picture(client)
    
    # Wait one hour for next update
    sleep(delay)


def change_picture(client):
    global CURRENT_PICTURE

    # Get all pictures from profile_pics directory
    pictures = os.listdir('./profile_pics')
    if len(pictures) < 2:
        return
    
    # Choose one of them (but not the current one) randomly considering each picture weights and store it's relative path
    picture = choices(pictures, weights=PICTURE_WEIGHTS)[0]

    if picture == CURRENT_PICTURE:
        picture_index = picture.split('.')[0]
        new_picture_index = str((int(picture_index) + 1) % len(pictures))
        picture = picture.replace(picture_index, new_picture_index)
    
    path = os.path.join('./profile_pics', picture)
    
    # Code from 'https://github.com/stanvanrooy/instauto/blob/master/examples/api/profile/update_picture.py'
    # Updates profile picture with given picture path without any side effects
    post = ps.PostNull(path=path)
    resp = client.post_post(post, 80)

    upload_id = resp.json()['upload_id']
    p = pr.SetPicture(upload_id=upload_id)
    client.profile_set_picture(p)

    CURRENT_PICTURE = picture


def change_biography(client):
    # Update profile biography
    obj = pr.SetBiography(get_biography_text())
    client.profile_set_biography(obj)


def get_biography_text():
    # Biography is composed of user's birthday, about user and user's hobbies
    biography = f'{get_birthday_text()}\n⠀\n{get_about_text()}\n⠀\n{get_hobbies_text()}'
    
    return biography


def get_birthday_text():
    # Tired to comment things :)
    # Here we are just calculating time to wait untill user's next birthday
    birth_date = datetime.strptime('2005-11-10 0', '%Y-%m-%d %H')
    
    UA_timezone = timezone('Europe/Kiev')
    current_date = datetime.now(UA_timezone)
    
    past_new_year = not (
                    (current_date.month == birth_date.month and current_date.day >= birth_date.day)
                    or current_date.month > birth_date.month)
    birthday_num = current_date.year - birth_date.year if past_new_year else current_date.year - birth_date.year + 1
    
    next_birth_date = current_date.replace(year=(current_date.year if past_new_year else current_date.year + 1), month=birth_date.month, day=birth_date.day, hour=birth_date.hour, minute=0, second=0, microsecond=0)
    days_till = (next_birth_date - current_date).days
    hours_till = (24 + next_birth_date.hour - current_date.hour) % 24
    
    return f'{num_to_emoji(birthday_num)}{get_ordinal_suffix(birthday_num)} 🎂birthday🍰 in ⏳{num_to_emoji(days_till)} days {num_to_emoji(hours_till)} hours⌛'


def num_to_emoji(num):
    # 12345 -> '1️⃣2️⃣3️⃣4️⃣5️⃣'
    num_emojies = {
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣',
        '0': '0️⃣'
    }
    
    emojified = ''
    for digit in str(num):
        emojified += num_emojies[digit]
    
    return emojified


def get_ordinal_suffix(num):
    # Returns correct ordinal suffix for given number
    suffixes = {
        1: 'st',
        2: 'nd',
        3: 'rd'
    }
    
    return 'th' if num in [11, 12, 13] else suffixes.get(num % 10, 'th')


def get_about_text():
    # Just hardcoded text
    return 'Vladyslav Zarytskyi\nKyiv🏙 Ukraine🇺🇦'


def get_hobbies_text():
    # List of user's hobbies
    hobbies = [
        'Coding👨‍💻',
        'Kitesurfing🪁🏄‍♂️',
        'Football⚽',
        'Science🧪🔭🔬',
        'Tech💻🚀📱'
    ]
    
    # Return randomly shuffled hobbies each one on new line
    return '\n'.join(sample(hobbies, len(hobbies)))


if __name__ == '__main__':
    main()
