import argparse
import os

import journaltools

# Command line interface for shiftpage. Take in two filenames to pass to shiftpage, which will copy the first page
# of input_file2 and add it to the end of input_file1.

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='Print status messages.',
                        )
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Use supplied filename as filename template for output files.',
                        )
    parser.add_argument('input_file1',
                        type=str,
                        help="Import CSV file to be used for PDF splitting. Must be in same format as export.",
                        )
    parser.add_argument('input_file2',
                        type=str,
                        help="Import CSV file to be used for PDF splitting. Must be in same format as export.",
                        )
    args = parser.parse_args()

    # Separate filename from extension. Add '-NEW' to output filename.
    if args.destination:
        output_file = args.destination
    else:
        output_file, output_extension = os.path.splitext(args.input_file1)
        output_file = output_file + "-NEW" + output_extension

    journaltools.shiftpage(args.input_file1, args.input_file2, output_file, args.verbose)
