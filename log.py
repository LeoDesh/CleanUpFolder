from collections import namedtuple
from random import sample
import logging
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    "sample_" + str(datetime.datetime.now())[0:8] + ".log", mode="w"
)
formatter = logging.Formatter(
    "%(asctime)s:%(funcName)s:%(levelname)s:%(name)s:%(message)s"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def main():
    Color = namedtuple("Color", ["red", "blue", "yellow"])
    some_color = Color(10, 15, 20)
    red = Color(255, 0, 0)
    blue = Color(0, 255, 0)
    logger.info("Red: {}".format(red))
    logger.debug("Blue: {}".format(blue))
    logger.warning(f"some_mix: {some_color}")


if __name__ == "__main__":
    main()
