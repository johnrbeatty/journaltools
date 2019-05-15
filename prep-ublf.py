import argparse
import os

import journaltools

# Command-line processor for PDF crop routine. Gather file names and pass to crop routine. Crop routine will
# check the page size and split any page wider than 700 points into two 8.5 x 11 pages.

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='Print status messages.',
                        )
    parser.add_argument('-t', '--test',
                        dest='test',
                        action='store_true',
                        help='Show test output',
                        )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        dest='debug',
                        help="Show debug output",
                        )
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Output file. Default is input file-NEW.pdf',
                        )
    parser.add_argument('filename',
                        type=str,
                        help="Import PDF file to have pages doubled.",
                        )
    args = parser.parse_args()

    # If destination file specified, assign it to output_file. If not, then use input filename.
    if args.destination:
        output_file = args.destination
    else:
        output_file, output_extension = os.path.splitext(args.filename)
        output_file = output_file + "-NEW" + output_extension

    if not args.test:
        journaltools.croppages(args.filename, output_file, args.verbose, args.debug)
