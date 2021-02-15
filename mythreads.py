#!/usr/bin/env python3
import os
import queue
import sys
import threading
import time

from queue import Queue

import myassets
import myvalidation

"""Queue used for reading input lines"""
q_stdin = Queue()

"""List of targets to expand"""
q_targets = Queue()

"""Output subdomains found from target"""
subdomains = {}

"""Keep track of all threads to be able to join"""
all_threads = []

"""Variables to kill threads"""
kill_thread_read_lines_from_stdin = False
kill_threads_process_input_to_targets = False
kill_threads_resolve_subdomains_from_targets = False

"""Number of threads for processing targets and resolving subdomains"""
DEFAULT_NUM_PROCESSING_THREADS = 1

"""Default time to block queues to read next input. If passed, then kill thread."""
DEFAULT_Q_TIMEOUT = 3

def read_lines(logger, q_stdin, file_to_read):
    """Function Reads the lines from stdin and adds it to a queue"""
    if not q_stdin:
        logger.error("in_queue empty - cannot read lines from input. Run configure"
                     " first.")
    else:
        if not os.path.isfile(file_to_read):
            logger.error(f"File: {file_to_read} does not exist.")
        else:
            with open(file_to_read, "r+") as f:
                try:
                    for l in f.readlines():
                        if not kill_thread_read_lines_from_stdin:
                            l_strip = l.strip()
                            logger.debug(f"Added input line: {l_strip}")
                            q_stdin.put(l_strip)
                        else:
                            break
                except KeyboardInterrupt:
                    logger.debug("Breaking loop to read input")
    
def launch_thread_read_lines(logger, all_threads, q_stdin, 
    file_to_read):
    """Start thread to Read the input lines which contains the target"""
    t = threading.Thread(target=read_lines, 
        args=(logger, q_stdin, file_to_read,))
    all_threads.append(t)
    t.start()
    return t

def process_input_to_targets(logger, q_stdin, targets):
    """Pull an asset from queue, convert it and put it in targets queue"""
    while True:
        inline = None
        try:
            inline = q_stdin.get(block=True, timeout=DEFAULT_Q_TIMEOUT)
        except queue.Empty:
            logger.debug("Killing thread: process_input_to_targets as no more input available")
            break
            
        if inline:
            if myvalidation.is_ip(logger, inline):
                ip = inline
                if ip and ip not in q_targets.queue:
                    logger.debug(f"Got input: {inline} as IP, adding to targets q")
                    q_targets.put(ip)

                ips = myassets.get_slash_24_ips_from_ip(logger, inline)
                if ips:
                    logger.debug(f"Extracting IP range from input: {inline} to "
                                 f"add to Q")
                    for ip in ips:
                        if ip and ip not in q_targets.queue:
                            q_targets.put(ip)

            elif myvalidation.is_domain(logger, inline):
                domain = inline
                ip = myassets.resolve_ip_from_domain(logger, domain)
                if ip and ip not in q_targets.queue:
                    logger.debug(f"Got input: {inline} as domain, adding to targets q")
                    q_targets.put(ip)

                    logger.debug(f"Extracting /24 IP range from IP: {ip} and adding new targets to q")
                    ips = get_slash_24_ips_from_ip(ip)
                    for ip in ips:
                        if ip and ip not in q_targets.queue:
                            q_targets.put(ip)

            elif myvalidation.is_ip_range(logger, inline):
                ip_range = inline
                ips = myassets.expand_ip_range(logger, ip_range)
                num_ips = len(ips)
                if ips:
                    logger.debug(f"Got input: {inline} as IP ranges, expanded to {num_ips} "
                                 f"and added to targets q")
                    for ip in ips:
                        if ip and ip not in q_targets.queue:
                            q_targets.put(ip)
            else:
                logger.error(f"Unknown asset type for asset: {inline}")

def launch_threads_process_input_to_targets(logger, all_threads, q_stdin, targets, 
    num_threads=DEFAULT_NUM_PROCESSING_THREADS):
    """Start thread to read the input lines which contains the target"""
    for i in range(0, num_threads):
        logger.debug(f"Launching thread i: {i} to process targets from input q" )
        t = threading.Thread(target=process_input_to_targets, 
            args=(logger, q_stdin, q_targets ))
        all_threads.append(t)
        t.start()

def resolve_subdomains_from_targets(logger, q_targets, subdomains, domain=""):
    """Resolve subdomains from targets"""
    while True:
        inline = None
        try:
            inline = q_targets.get(block=True, timeout=DEFAULT_Q_TIMEOUT)
        except queue.Empty:
            logger.debug("Killing thread: resolve_subdomains_from_targets as no more input available")
            break
        
        if inline:
            subdomain = myassets.resolve_domain_from_ip(logger, inline)

            if subdomain:
                if domain:
                    if myvalidation.is_subdomain(logger, subdomain, domain):
                        logger.debug(f"domain: {subdomain} is subdomain of domain")
                        if subdomain not in subdomains:
                            logger.info(f"subdomain: {subdomain} added to subdomains")
                            print(subdomain)
                            subdomains[subdomain] = '1'
                        else:
                            logger.debug(f"subdomain: {subdomain} already exists")
                else:
                    if myvalidation.is_domain(logger, subdomain):
                        logger.debug(f"No domain provided for filtering, so adding: {subdomain} "
                                    f"to subdomains list")
                        logger.info(f"subdomain: {subdomain} added to subdomains")
                        subdomains[subdomain] = '1'
                        print(subdomain)
                    else:
                        logger.debug(f"No subdomain provided. But, {subdomain} is not a domain. Not added.")

def launch_threads_resolve_subdomains_from_targets(logger, all_threads, q_targets, 
    subdomains, domain="", num_threads=DEFAULT_NUM_PROCESSING_THREADS):
    """Launching threads to resolve subdomains from targets"""
    for i in range(0, num_threads):
        logger.debug(f"Launching thread i: {i} to resolve subdomains from targets")
        t = threading.Thread(target=resolve_subdomains_from_targets, 
            args=(logger, q_targets, subdomains, domain))
        all_threads.append(t)
        t.start()
