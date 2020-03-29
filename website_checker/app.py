import logging
import time
import random
import requests

from dynaconf import settings
from twilio.rest import Client

log_format = "%(asctime)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
file_handler = logging.StreamHandler()
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def is_back_online(fetcher, url: str) -> bool:
    """
    Checks if the informed url is back online
    :param fetcher:
    :param url:
    :return:
    """
    is_back = False
    for _ in range(settings.TIMES_UNTIL_SURE):
        result = fetcher.get(url)
        if result.status_code < 500:
            is_back = True
            time.sleep(random.randint(30, 60))
        else:
            is_back = False
            break
    return is_back


def send_notification(message: str, broker: str = "whatsapp"):
    client = Client(settings.TWILIO_ACCOUNT, settings.TWILIO_TOKEN)
    client.messages.create(
        body=message,
        from_=f"{broker}:{settings.TELEPHONE_FROM}",
        to=f"{broker}:{settings.TELEPHONE_TO}",
    )


def run_checker():
    while not is_back_online(requests, settings.WEBSITE_URL):
        logger.info(f"The `{settings.WEBSITE_NAME}`s website still OFFLINE.")

        # Random time between 30 and 60 secs to retry
        time.sleep(random.randint(30, 60))

    logger.info(f"The `{settings.WEBSITE_NAME}`s website is back!")

    if settings.SEND_NOTIFICATION:
        send_notification(f"The `{settings.WEBSITE_NAME}`s website is back ONLINE!")
