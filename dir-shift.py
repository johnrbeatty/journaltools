import argparse

from journaltools import dirshift

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
                        action='store_true',
                        help="Show debug output",
                        )
    parser.add_argument('-o', '--output-file',
                        dest='destination',
                        type=str,
                        help='Output file. Default is input file.xslx',
                        )
    parser.add_argument('path',
                        type=str,
                        help="Import directory containing PDFs that need page shifting.",
                        )
    args = parser.parse_args()

    dirshift(args.path, args.verbose, args.debug, args.test)
