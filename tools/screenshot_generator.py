#! /usr/bin/env python

import os
import sys
import logging
import argparse
import pickle

from logging import handlers

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from webloader.phantomjs_loader import PhantomJSLoader


def main():
    logging.info('========== SCREENSHOT GENERATOR LAUNCHED ==========')

    # make url list
    urls = []
    if args.url_file:
        with open(args.url_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line != '': urls.append(line.strip())
        f.closed
    if args.load_pages:
        urls += args.load_pages

    if len(urls) == 0:
        logging.getLogger(__name__).error('No URLs were specified.')
        sys.exit(-1)

    # load pages and save screenshots
    if len(urls) > 0:
        loader = PhantomJSLoader(outdir=args.outdir, user_agent=args.useragent,\
            num_trials=args.numtrials, restart_on_fail=True, save_screenshot=True,\
            retries_per_trial=3)
        loader.load_pages(urls)
        
        # pickle load results
        try:
            with open(os.path.join(args.outdir, 'screenshot_generator_results.pickle'), 'w') as f:
                pickle.dump(loader, f)
            f.closed
        except:
            logging.exception('Error saving pickled results.')



if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Web page profiler.')
    parser.add_argument('-l', '--load_pages', nargs='+', help='URL(s) to load (to load multiple pages, separate URLs with spaces). A HAR will be generated for each page in outdir.')
    parser.add_argument('-f', '--url_file', default=None, help='Generate HARs for the URLs in the specified file (one URL per line)')
    parser.add_argument('-o', '--outdir', default='.', help='Destination directory for HAR files.')
    parser.add_argument('-n', '--numtrials', default=1, type=int, help='Number of times to load each URL.')
    parser.add_argument('-u', '--useragent', default=None, help='Custom user agent. If None, use browser default.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    parser.add_argument('-g', '--logfile', default=None, help='Path for log file.')
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        try:
            os.makedirs(args.outdir)
        except Exception as e:
            logging.getLogger(__name__).error('Error making output directory: %s' % args.outdir)
            sys.exit(-1)
    
    # set up logging
    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logfmt = "%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s"
    config = {
        'format' : logfmt,
        'level' : level
    }
    logging.basicConfig(**config)
    #if args.logfile:
    #    config['filename'] = args.logfile
    if args.logfile:
        handler = handlers.RotatingFileHandler(args.logfile,\
            maxBytes=10*1024*1024, backupCount=3)
        logging.getLogger('').addHandler(handler)
        handler.setFormatter(logging.Formatter(fmt=logfmt))
        handler.setLevel(level)

    main()
