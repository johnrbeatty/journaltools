import argparse
import os

import journaltools

# Command line front end for pdf splitting function in journaltools.py.
# This function takes a PDF file and a corresponding CSV file containing start and end pages for each segment of
# the PDF and splits the PDF file into those segments. The command-line requires only the PDF file, but input
# CSV file and output filename templates can be set. If not provided, the code will default to the PDF filename,
# replacing the extension with .csv for the input file.


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='PDF file to split.',
                        type=str,
                        )
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
                        help='Use supplied filename as filename template for output files.',
                        )
    parser.add_argument('-i', '--input-file',
                        dest='input_file',
                        type=str,
                        help="Import CSV file to be used for PDF splitting. Must be in same format as export. "
                             "Default is filename with .csv extension.")
    args = parser.parse_args()

    # Split filename from extension before passing to the various functions. Use input filename for template
    # if no output filename specified.
    if args.destination:
        output_file, output_extension = os.path.splitext(args.destination)
    else:
        output_file, output_extension = os.path.splitext(args.filename)

    # Set input CSV filename. If no filename provided, use the input filename with CSV extension.
    if args.input_file:
        input_file = args.input_file
    else:
        input_file, input_extension = os.path.splitext(args.filename)
        input_file = input_file + '.csv'

    # Read CSVfile and get starting and ending PDF pages to pass to splitpdf
    if os.path.exists(input_file):
        start_pdf_page, end_pdf_page = journaltools.importcsv(input_file, args.debug)
        # Split Original PDF into separate documents for each piece, unless test flag is set
        if not args.test:
            journaltools.splitpdf(args.filename, args.verbose, args.debug, start_pdf_page, end_pdf_page, output_file)
    else:
        print(f'{input_file} not present. Please specify a valid CSV file to use for the split points.')
