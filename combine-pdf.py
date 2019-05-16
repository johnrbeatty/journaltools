import argparse
import os

from journaltools import combinepdf
from journaltools import getfilenames

if __name__ == '__main__':
    # Command-line parser for combinepdf using getfilenames to build the file list.
    parser = argparse.ArgumentParser(
        description='Combines consecutive PDF files named in Hein-style sequence.'
    )
    parser.add_argument('filename',
                        type=str,
                        help="File name of the first file in the group that needs to be combined. Files should be "
                             "standard Hein names",
                        )
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='Print status messages.',
                        )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="Show debug output",
                        )
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Output file. Default is <input file>-NEW.<ext>',
                        )
    args = parser.parse_args()

    # If destination file specified, assign it to output_file. If not, then use input filename.
    if args.destination:
        output_file = args.destination
    else:
        output_file, output_extension = os.path.splitext(args.filename)
        output_file = output_file + "-NEW" + output_extension

    files = getfilenames(args.filename, args.debug)

    if args.verbose:
        print(files)

    if not args.test:
        combinepdf(files, output_file, args.verbose)
