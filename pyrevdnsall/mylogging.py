#!/usr/bin/env python3
import logging

DEFAULT_LOGGER_NAME = "pyrevdnsall"

def configure_logging(logging_type='basic', logger_name=DEFAULT_LOGGER_NAME):
    """Configure the logger and return it"""
    logger = None
    if logging_type == 'basic':
        logger = configure_basic_logging(logger_name=logger_name)
    return logger

def configure_basic_logging(logger_name=DEFAULT_LOGGER_NAME, 
    logging_level=logging.DEBUG):
    """Configure basic config logging, optionally with different logging level"""
    logger = logging.getLogger(logger_name)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging_level)
    logger.setLevel(logging_level)
    logger.addHandler(ch)
    return logger
