#!/usr/bin/env python3
import argparse
import sys

import mylogging
import mythreads

"""Number of threads to use"""
DEFAULT_NUM_THREADS = 10

"""Description for this script"""
DESCRIPTION = """
Script to perform reverse DNS lookup on provided IP address/range to identify
valid subdomains for an optionally given domain
"""

def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION, 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--domain", 
        help="Main Domain to use to identify valid subdomains")
    parser.add_argument("-t", "--threads", default=DEFAULT_NUM_THREADS,
        help="Number of threads to use for scanning")
    args = parser.parse_args()

    logger = mylogging.configure_basic_logging()

    try:
        mythreads.launch_thread_read_line_from_stdin(
            logger, 
            mythreads.all_threads,
            mythreads.q_stdin)

        mythreads.launch_threads_process_input_to_targets(
            logger, 
            mythreads.all_threads,
            mythreads.q_stdin, 
            mythreads.q_targets,
            num_threads=int(args.threads))

        mythreads.launch_threads_resolve_subdomains_from_targets(
            logger,
            mythreads.all_threads,
            mythreads.q_targets,
            mythreads.subdomains, 
            domain=args.domain,
            num_threads=int(args.threads)
        )

        logger.debug("Joining main to running threads in background")
        for t in mythreads.all_threads:
            t.join()

    except KeyboardInterrupt as e: 
        logger.debug("Setting flags to kill all running threads")
        mythreads.kill_thread_read_lines_from_stdin = True
        mythreads.kill_threads_process_input_to_targets = True
        mythreads.kill_threads_resolve_subdomains_from_targets = True

if __name__ == "__main__":
    sys.exit(main())
