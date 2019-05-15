import argparse
import os
import re
import journaltools


def processpdfnew(verbose, debug, pageText):

    # Create lists for all values to be exported to CSV file. Each index value will correspond to the metadata
    # for one article across all lists. This code assumes that there will be no more than two authors on each article.
    Title = []
    Author1 = []
    Author2 = []
    StartPage = []
    StartPDFPage = []
    EndPDFPage = []

    # Process each page. Step through pages and attempt to find titles, authors, and page numbers in OCR text.
    # Store this metadata and the start and end pages of each article into lists.
    if verbose:
        print(f'Processing PDF pages')

    for pageNumber in range (0, len(pageText)):

        if debug > 0 and debug <6:
            print('Processing PDF page number %d' % pageNumber)

        # look for an article title on this page, add lines to titleParts,
        # then add them together and title capitalize
        tempTitle = ""
        # Look for all lines that consist only of three or more of the following characters on their own line:
        # all caps, spaces, hyphens and single quotes.
        titleParts = re.findall(r'[A-Za-z .:"\'\-]{3,}\(', pageText[pageNumber], re.DOTALL)
        if debug > 1 and debug < 5 and titleParts:
            print('Title parts: %s' % titleParts)

        # Join all returned lines together in tempTitle. Strip extra spaces and use title capitalization.
        # Any word with an apostrophe comes out with a space before the apostrophe and the next letter
        # capitalized. Fix in a future version.
        for t in titleParts:
            tempTitle = tempTitle + " " + t
        tempTitle = tempTitle.strip()
        tempTitle = re.sub(r' {2,}', " ", tempTitle)
        tempTitle = tempTitle.title()
        # Print processed title at debug levels 1-4.
        if debug > 0 and debug < 5 and tempTitle:
            print('TITLE: %s' % tempTitle)

        # If title is at least four characters long, append to Title list. This should be enough to get rid of
        # garbage lines, but short enough to keep short ones. Look for original page number in OCR text, and
        # if found append to StartPage list. If not, append placeholder string. Append the page number of the
        # PDF file to StartPDFPage list.
        if len(tempTitle) > 5:
            Title.append(tempTitle)
            OriginalPageNumber = re.search(r'^[\d]{1,4}$', pageText[pageNumber], re.MULTILINE)
            if OriginalPageNumber:
                StartPage.append(OriginalPageNumber[0])
            else:
                StartPage.append(" ")
            StartPDFPage.append(pageNumber)
            if debug > 0 and debug < 5:
                if OriginalPageNumber:
                    print('Start page in PDF text: %s' % OriginalPageNumber[0])
                else:
                    print('No start page found in PDF text')

        # Find authors. If one or two lines
        # are returned, append them to tempAuthor. Append the current PDF file page to EndPDFPage.
        tempAuthor = re.findall(
            r'(?<=\n)[A-Z][A-Za-z]{0,}\.{0,1} {1,}[A-Z][a-z]{0,}\.{0,1} {1,}[A-Za-z]{1,}\.{0,1}[,. A-Za-z]{0,6}(?=\n)|'
            r'(?<=\n)[A-Z][A-Za-z]{1,} {1,}[A-Z][a-z]{1,}[,. A-Za-z]{0,6}(?=\n)|'
            r'(?<=\n)[A-Z][A-Za-z]{0,}\.{0,1} {1,}[A-Z][a-z]{0,}\.{0,1} {1,}[A-Za-z]{1,}\.{0,1} {1,}[A-Za-z]{1,}\.{0,1}'
            r'[,. A-Za-z]{0,6}(?=\n)',
            pageText[pageNumber])
        if tempAuthor:
            Author1.append(tempAuthor[0])
            if len(tempAuthor) == 2:
                Author2.append(tempAuthor[1])
            else:
                Author2.append("")
            EndPDFPage.append(pageNumber)
        if debug > 0 and debug < 5:
            print('Author: %s' % tempAuthor)
        if debug > 1 and debug < 5:
            print(f'PDF start pages: {StartPDFPage}')
            print(f'PDF end pages: {EndPDFPage}')

    # Compare lists to see if they contain the same number of values. If not, then pad out the short lists with
    # empty values and throw a warning. Evaluation is in two groups: The values updated when a title is found,
    # and the values updated when an author is found.
    if len(Title) > len(Author1):
        print('WARNING! Missing authors and ending PDF pages')
        for r in range(len(Author1), len(Title)):
            Author1.append('')
            Author2.append('')
            EndPDFPage.append(0)
    elif len(Author1) > len(Title):
        print('WARNING! Missing titles, start pages, and starting PDF pages')
        for r in range(len(Title), len(Author1)):
            Title.append('')
            StartPage.append('')
            StartPDFPage.append(0)

    # Lots of debugging output
    # Print all of the lists; debug levels 2 & 4
    if debug == 2 or debug == 4:
        print('\n\nAll list values:')
        print(Title)
        print(Author1)
        print(Author2)
        print(StartPage)
        print(StartPDFPage)
        print(EndPDFPage)
    # step through each record and print all contents; debug level 6
    if debug == 6:
        print('\n\nAll records:')
        for r in range(0, len(Title)):
            print(f'Record {r}: {Title[r]}; {Author1[r]}; {Author2[r]}; {StartPage[r]}; {StartPDFPage[r]}; {EndPDFPage[r]}')

    # Return all collected metadata lists.
    return Title, StartPage, StartPDFPage, EndPDFPage, Author1, Author2


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help='PDF file to analyze and split.',
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
    parser.add_argument('--write-csv-only',
                        action="store_true",
                        dest="csvOnly",
                        help="Write CSV file, but don't split PDFs. Test flag takes precedence.",
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
                        help="Import CSV file to be used for PDF splitting. Must be in same format as export.")
    args = parser.parse_args()

    print("DecisionSplitter version 0.2\n")

    if args.destination:
        outputFile, outputExtension = os.path.splitext(args.destination)
    else:
        outputFile, outputExtension = os.path.splitext(args.filename)

    # If importCSV is specified, read that file and get StartPDFPage and EndPDFPage to pass to SplitPDFs
    # If no importCSV is selected, process args.filename
    if args.input_file:
        StartPDFPage, EndPDFPage = journaltools.importcsv(args.input_file)
    else:
        # Fetch OCR page text from PDF file at args.filename.
        pageText = journaltools.getpdf(args.filename, args.verbose, args.debug)
        # Process pages in pageText
        Title, StartPage, StartPDFPage, EndPDFPage, Author1, Author2 = processpdfnew(args.verbose, args.debug, pageText)
        # Export CSV file, or show what output would be if test flag is set
        journaltools.exportcsv(outputFile, args.verbose, args.debug, args.test, Title, StartPage, StartPDFPage, EndPDFPage, Author1, Author2)

    # Split Original PDF into separate documents for each piece, unless test or csvOnly flags are set
    if not args.test and not args.csvOnly:
        journaltools.splitpdf(args.filename, args.verbose, args.debug, StartPDFPage, EndPDFPage, outputFile)

