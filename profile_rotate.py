#!/usr/bin/python3
""" Randomize Twitter pfp, name, and bio """
import datetime as dt
from numbers import Number
import os
from pathlib import Path
import random
import typing
import twitter
import yaml

ARTIST_PLACEHOLDER = "@ARTISTNAMEHERE!"
IMG_EXTS = ['.png', '.jpg', '.jpeg', '.gif']
KEYS_PATH = "./keys.yaml"
CONFIG_PATH = "./config.yaml"
NAME_LIMIT = 50
BIO_LIMIT = 160
DEBUG_MODE = True


class InvalidConfig(Exception):
    """
    Exception raised when there's some issue with the configuration
    Takes the attribute "invalid_setting" and prints an error message
    explaining which setting caused an error to occur.
    """

    def __init__(self, invalid_setting: str,
                 message="This setting is defined incorrectly"):
        self.invalid_setting = invalid_setting
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} : {self.invalid_setting}"


def load_keys() -> dict:
    """ Load Twitter API keys """
    with open(KEYS_PATH, 'r', encoding='utf-8') as keys_file:
        keys = yaml.load(keys_file, yaml.FullLoader)
    return keys


def load_config() -> dict:
    """ Load the config file """
    with open(CONFIG_PATH, 'r', encoding='utf-8') as configuration_file:
        config = yaml.load(configuration_file, yaml.FullLoader)
    return config


def generate_bio(settings: dict, artist_name=None) -> str:
    """ Generates a bio to give to the Twitter API """
    if settings['use_file']:
        with open(settings['file_name'], 'r', encoding='utf-8') as bio_file:
            bio_string = bio_file.read()
    elif settings['bio_text']:
        bio_string = settings['bio_text']
    else:
        raise InvalidConfig("bio", ("The bio setting is enabled, but no bio "
                                    "was defined."))
    bio_string = bio_string.replace(ARTIST_PLACEHOLDER, artist_name)
    if not settings.get('length_override') and len(bio_string) > BIO_LIMIT:
        raise InvalidConfig("bio", f"The generated bio is > {BIO_LIMIT} chars")
    return bio_string


def save_run_data(artist_name: str):
    """ Saves data about the current run to a yaml file """
    run_data = {'timestamp': dt.datetime.now(), 'artist_name': artist_name}
    with open('./last_run.yaml', 'w', encoding='utf-8') as save_file:
        yaml.dump(run_data, save_file)


def load_run_data() -> tuple:
    """ Loads data about the last time the script ran """
    try:
        with open('./last_run.yaml', 'r', encoding='utf-8') as run_data_file:
            run_data = yaml.load(run_data_file, yaml.FullLoader)
    except OSError:
        print("The last_run file doesn't exist, using default values.")
        return None, dt.datetime.min
    try:
        return run_data['artist_name'], run_data['timestamp']
    except KeyError:
        raise InvalidConfig('last_run', 'The file was incorrectly formatted.')


def generate_name(settings: dict) -> str:
    """ Generates a username to give to the Twitter API """
    if not settings['name']:
        raise InvalidConfig("name", "No name was specified.")
    name = settings['name']
    if settings['punctuation'].get("enabled"):
        try:
            marks = settings['punctuation']['marks']
        except KeyError:
            raise InvalidConfig("punctuation", "Marks were not defined")
        mark_weights = settings['punctuation'].get('weights')
        if mark_weights is not None and len(mark_weights) == len(marks):
            chosen_mark = random.choices(marks, weights=mark_weights, k=1)[0]
        elif mark_weights is None:
            chosen_mark = random.choice(marks)
        else:
            raise InvalidConfig("punctuation", "Wrong number of weights.")
        name += chosen_mark
    if settings['spice'].get("enabled"):
        try:
            with open(settings['spice']['spice_file'], 'r',
                      encoding='utf-8') as spice_file:
                lines = spice_file.read().splitlines()
                selection = random.choice(lines).strip()
                name += f' ({selection})'
        except OSError:
            raise InvalidConfig("spice", "The given path is invalid")
    if not settings.get('length_override') and len(name) > NAME_LIMIT:
        raise InvalidConfig("name", "The generated name was too long.")
    return name


def select_image(settings: dict, previous_artist=None) -> tuple:
    """ Selects a random image from the given directories """
    if settings.get('allow_repeats'):
        previous_artist = None
    image_base_dir = settings.get('image_directory')
    images: typing.List[tuple] = []
    image_weights: typing.List[Number] = []
    for current_pool in settings['pools'].values():
        if not current_pool.get('artist_account'):
            raise InvalidConfig('images', ('No artist specified for '
                                           f'{current_pool}'))
        pool_artist = current_pool['artist_account']
        pool_directory = current_pool.get('subdirectory')
        if pool_artist == previous_artist:
            pool_weight = 0
        elif current_pool.get('weight') is not None:
            pool_weight = current_pool.get('weight')
        else:
            pool_weight = 1
        pool_path = Path(f'{image_base_dir}{pool_directory}')
        if not os.path.exists(pool_path):
            raise InvalidConfig('images', f'The path for {current_pool}, '
                                f'"{pool_path}", is invalid.')
        pool_images = [p for p in pool_path.rglob('*') if p.suffix in IMG_EXTS]
        for current_image in pool_images:
            images.append((current_image, pool_artist))
            image_weights.append(pool_weight)
    selected_image = random.choices(images, weights=image_weights, k=1)[0]
    return selected_image


def main():
    """ Main logic """
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    keys = load_keys()
    config = load_config()
    api = twitter.Api(consumer_key=keys['consumer_key'],
                      consumer_secret=keys['consumer_secret'],
                      access_token_key=keys['access_token_key'],
                      access_token_secret=keys['access_token_secret'])
    saved_data = load_run_data()
    if dt.datetime.now() - saved_data[1] < dt.timedelta(minutes=5):
        print("Note - the script has already run within the last 5 minutes.")
    new_name = generate_name(config['display_name'])
    selected_image = select_image(config['images'], saved_data[0])
    new_bio = generate_bio(config['bio'], artist_name=selected_image[1])
    if DEBUG_MODE:
        print(new_name)
        print(new_bio)
        print(selected_image)
    else:
        api.UpdateProfile(name=new_name, description=new_bio)
        api.UpdateImage(selected_image[0])
    save_run_data(selected_image[1])


if __name__ == "__main__":
    main()
