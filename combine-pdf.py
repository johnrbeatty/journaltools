import argparse
import os

import journaltools

from journaltools import getfilenames

if __name__ == '__main__':
    # Command-line parser for combinepdf/getfilenames. Add output file option.
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='Print status messages.',
                        )
    parser.add_argument('-t', '--test',
                        action='store_true',
                        help="Test only. Don't output any files. Use with debug options to see test output.",
                        )
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        help="Show debug output",
                        )
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Output file. Default is input file.xslx',
                        )
    parser.add_argument('filename',
                        type=str,
                        help="Import directory containing PDFs that need page shifting.",
                        )
    args = parser.parse_args()

    # If destination file specified, assign it to output_file. If not, then use input filename.
    if args.destination:
        output_file = args.destination
    else:
        output_file, output_extension = os.path.splitext(args.filename)
        output_file = output_file + "-NEW" + output_extension

    files = getfilenames(args.filename, args.debug)

    print(files)

    if not args.test:
        journaltools.combinepdf(files, output_file, args.verbose)
