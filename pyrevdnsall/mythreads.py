#!/usr/bin/env python3
import queue
import sys
import threading

from queue import Queue

import myassets
import myvalidation

"""Queue used for reading input lines"""
q_stdin = Queue()

"""List of targets to expand"""
q_targets = {}

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

"""Default time to block queues to read next input"""
DEFAULT_Q_TIMEOUT = 1

def read_lines_from_stdin(logger, q_stdin):
    """Function Reads the lines from stdin and adds it to a queue"""
    if not q_stdin:
        logger.error("in_queue empty - cannot read lines from input. Run configure"
                     " first.")
    else:
        try:
            for l in sys.stdin:
                if not kill_thread_read_lines_from_stdin:
                    l_strip = l.strip()
                    logger.debug(f"Added input line: {l_strip} for processing")
                    q_stdin.put(l_strip)
                else:
                    break
        except KeyboardInterrupt:
            logger.debug("Breaking loop to read input")


def launch_thread_read_line_from_stdin(logger, all_threads, q_stdin):
    """Start thread to Read the input lines which contains the target"""
    t = threading.Thread(target=read_lines_from_stdin, args=(logger,q_stdin,))
    all_threads.append(t)
    t.start()
    return t

def process_input_to_targets(logger, q_stdin, targets):
    """Pull an asset from queue, convert it and put it in targets queue"""
    while not kill_threads_process_input_to_targets:
        try:
            inline = q_stdin.get(block=True, timeout=DEFAULT_Q_TIMEOUT)
        except Queue.empty:
            pass
            
        if inline:
            if myvalidation.is_ip(inline):
                ip = inline
                if ip and ip not in q_targets.queue:
                    logger.debug(f"Got input: {inline} as IP, adding to targets q")
                    q_targets.put(ip)

                ips = get_slash_24_ips_from_ip(inline)
                if ips:
                    logger.debug(f"Extracting IP range from input: {inline} to "
                                 f"add to Q")
                    for ip in ips:
                        if ip and ip not in q_targets.queue:
                            q_targets.put(ip)

            elif myvalidation.is_domain(inline):
                domain = inline
                ip = myassets.resolve_ip_from_domain(logger, domain)
                if ip and ip not in q_targets.queue:
                    logger.debug(f"Got input: {inline} as domain, adding to targets q")
                    q_targets.put(ip)

            elif myvalidation.is_ip_range(inline):
                ip_range = inline
                ips = expand_ip_range(logger, ip_range)
                num_ips = len(ips)
                if ips:
                    logger.debug(f"Got input: {inline} as IP ranges, expanded to {num_ips} "
                                 f"and added to targets q")
                    for ip in ips:
                        if ip and ip not in q_targets.queue:
                            q_targets.put(ip)
            else:
                logger.error(f"Unknown asset type for asset: {inline}")
    
    logger.debug("Killed thread: process_input_to_targets")

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
    while not kill_threads_resolve_subdomains_from_targets:
        try:
            inline = q_targets.get(block=True, timeout=DEFAULT_Q_TIMEOUT)
        except Queue.empty:
            pass
            
        subdomain = myassets.resolve_domain_from_ip(logger, ip)

        if domain:
            if myvalidation.is_subdomain(logger, subdomain, domain):
                logger.debug(f"domain: {subdomain} is subdomain of domain")
                if subdomain not in subdomains:
                    logger.debug(f"subdomain: {subdomain} added to subdomains")
                    subdomains[subdomain] = '1'
                else:
                    logger.debug(f"subdomain: {subdomain} already exists")
        else:
            logger.debug(f"No domain provided for filtering, so adding: {subdomain}"
                         f"to subdomains list")
            subdomains[subdomain] = '1'
    
    logger.debug("Killed thread: resolve_subdomains_from_targets")

def launch_threads_resolve_subdomains_from_targets(logger, all_threads, q_targets, 
    subdomains, domain="", num_threads=DEFAULT_NUM_PROCESSING_THREADS):
    """Launching threads to resolve subdomains from targets"""
    for i in range(0, num_threads):
        logger.debug(f"Launching thread i: {i} to resolve subdomains from targets")
        t = threading.Thread(target=resolve_subdomains_from_targets, 
            args=(logger, q_targets, subdomains))
        all_threads.append(t)
        t.start()

            

