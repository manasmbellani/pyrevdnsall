#!/usr/bin/env python3

import re

"""Regex for domain"""
DOMAIN_REGEX = "^(?:[a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]{1,6}$"

"""Regex for IP"""
IP_REGEX = "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"

"""Regex for IP range"""
IP_RANGE_REGEX = "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$"


def is_domain(logger, val):
    """Confirm if value is a domain"""
    is_domain = False
    logger.debug(f"Checking if value: {val} is a domain IP")
    if is_ip(logger, val):
        is_domain = False
    else:
        if re.match(DOMAIN_REGEX, val):
            is_domain = True
    return is_domain

def is_ip(logger, val):
    """Confirms if value is an IP"""
    is_ip = False
    logger.debug(f"Checking if value: {val} is an IP")
    if re.match(IP_REGEX, val):
        is_ip = True
    return is_ip

def is_ip_range(logger, val):
    """Confirms whether we have provided an IP range as value"""
    is_ip_range = False
    logger.debug(f"Checking if value: {val} is an IP range")
    if re.match(IP_RANGE_REGEX, val):
        is_ip_range = True
    return is_ip_range

    
def is_subdomain(logger, val, domain):
    """Determines if value is sudomain of another domain"""
    if not domain.startswith("."):
        domain = "." + domain
    
    if val.endswith(domain):
        return True
    else:
        return False        