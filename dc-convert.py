import os
import argparse

from journaltools import convertcsv

if __name__ == '__main__':
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
                        dest='debug',
                        type=int,
                        help="Set debug level (1-6).",
                        default=0,
                        )
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Output file. Default is input file.xslx',
                        )
    parser.add_argument('-i', '--input-file',
                        dest='input_file',
                        type=str,
                        help="Import CSV file to be used for PDF splitting. Must be in same format as export.")
    parser.add_argument('-p', '--template_file',
                        dest='template_file',
                        type=str,
                        help="Excel file to use as export template.")
    args = parser.parse_args()

    # Split filename from extension before passing to the various functions. Use input filename for template
    # if no output filename specified.
    if args.destination:
        output_file, output_extension = os.path.splitext(args.destination)
    else:
        output_file, output_extension = os.path.splitext(args.input_file)

    # If importCSV is specified, read that file and get StartPDFPage and EndPDFPage to pass to SplitPDFs
    # If no importCSV is selected, process args.filename
    if args.input_file:
        convertcsv(args.input_file, output_file, args.template_file, args.verbose, args.debug)
    else:
        print('No input file. Nothing to do.')
