#!/usr/bin/env python3
import argparse
import sys

import mylogging
import mythreads

def main():
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
            mythreads.q_targets)

        mythreads.launch_threads_resolve_subdomains_from_targets(
            logger,
            mythreads.all_threads,
            mythreads.q_targets,
            mythreads.subdomains
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
