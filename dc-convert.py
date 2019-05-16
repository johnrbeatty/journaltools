import os
import argparse

from journaltools import convertcsv

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export and convert CSV files generated by this suite of tools to an Excel file that can be '
                    'cut and pasted into a Digital Commons batch import file.'
    )
    parser.add_argument('input_file',
                        type=str,
                        help='Import CSV file to be used for PDF splitting. Only starting and ending PDF pages '
                             'are required.')
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Output Excel file. Default is <input file>.xslx',
                        )
    parser.add_argument('-p', '--template',
                        dest='template_file',
                        type=str,
                        help='Excel file to use as export template. Must be xlsx file. Digital Commons templates '
                             'must be converted.')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help='Print status messages.',
                        )
    parser.add_argument('-d', '--debug',
                        dest='debug',
                        action='store_true',
                        help='Show debugging output.',
                        default=0,
                        )
    args = parser.parse_args()

    # Split filename from extension before passing to the various functions. Use input filename for template
    # if no output filename specified.
    if args.destination:
        output_file, output_extension = os.path.splitext(args.destination)
    else:
        output_file, output_extension = os.path.splitext(args.input_file)

    # Read input file, convert to Excel using the columns specified in template_file if  present,
    # then write to output_file.
    convertcsv(args.input_file, output_file, args.template_file, args.verbose, args.debug)
