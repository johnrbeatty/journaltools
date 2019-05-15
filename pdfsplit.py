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
        outputFile, outputExtension = os.path.splitext(args.destination)
    else:
        outputFile, outputExtension = os.path.splitext(args.filename)

    # Set input CSV filename. If no filename provided, use the input filename with CSV extension.
    if args.input_file:
        inputFile = args.input_file
    else:
        inputFile, inputExtension = os.path.splitext(args.filename)
        inputFile = inputFile + '.csv'

    # Read CSVfile and get StartPDFPage and EndPDFPage to pass to splitpdf
    if os.path.exists(inputFile):
        StartPDFPage, EndPDFPage = journaltools.importcsv(inputFile, args.debug)
        # Split Original PDF into separate documents for each piece, unless test flag is set
        if not args.test:
            journaltools.splitpdf(args.filename, args.verbose, args.debug, StartPDFPage, EndPDFPage, outputFile)
    else:
        print(f'{inputFile} not present. Please specify a valid CSV file to use for the split points.')
