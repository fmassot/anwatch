import logging.config


def setup_logging():
    logging.config.fileConfig('logging.conf')