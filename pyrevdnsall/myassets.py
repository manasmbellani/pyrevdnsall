#!/usr/bin/env python3

import ipaddress
import socket

def expand_ip_range(logger, ip_range):
    """Expand IP range to individual IPs"""
    logger.debug(f"Expanding IP range: {ip_range} to individual IPs")
    r = IPv4Network(ip_range)
    return [str(ip) for ip in ip_range]

def get_slash_24_ips_from_ip(logger, ip):
    """Get the /24 IP range from IP"""
    logger.debug(f"Getting the IP range from IP: {ip}")
    ip_range_str = '.'.join(ip.split('.')[0:3])
    ip_range_str += ".0/24"
    ips = expand_ip_range(logger, ip_range_str)
    return ips

def resolve_domain_from_ip(logger, ip):
    """Getting the domain via reverse IP"""
    logger.debug(f"Obtain the domain name from reverse ip: {ip}")
    domain = ''
    try:
        domain, __, __ = socket.gethostbyaddr(ip)
        logger.debug(f"{ip} -> {domain}")
    except Exception as e:
        logger.warning(f"Error resolving domain from ip: {ip}. "
                       f"Error: {e.__class__}, {e}")
    return domain

def resolve_ip_from_domain(logger, domain):
    """Resolve the IP from domain"""
    logger.debug(f"Obtain the ip address from domain: {domain}")
    ip = ''
    try:
        ip = socket.gethostbyname(name)
    except Exception as e:
        logger.warning(f"Error resolving domain to ip: {ip}. "
                       f"Error: {e.__class__}, {e}")
    return ip

