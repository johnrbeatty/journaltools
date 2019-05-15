import argparse
import os
import re

import journaltools


def processpdfnew(verbose, debug, pagetext):

    # Create lists for all values to be exported to CSV file. Each index value will correspond to the metadata
    # for one article across all lists. This code assumes that there will be no more than two authors on each article.
    title = []
    author1 = []
    author2 = []
    start_page = []
    start_pdf_page = []
    end_pdf_page = []
    page_number = 0

    # Process each page. Step through pages and attempt to find titles, authors, and page numbers in OCR text.
    # Store this metadata and the start and end pages of each article into lists.
    if verbose:
        print('Processing PDF pages')
    for page_number in range(0, len(pagetext)):
        if 1 < debug < 6:
            print('Processing PDF page number %d' % page_number)

        # look for an article title on this page, add lines to title_parts,
        # then add them together and title capitalize
        temp_title = ""
        # Look for all lines that consist only of three or more of the following characters on their own line:
        # all caps, spaces, hyphens and single quotes.
        title_parts = re.findall(r'(?<=\n)[A-Z][A-Za-z0-9 .,():"\'\-]{3,}\.(?=\s+By)|'
                                 r'By\s{1,2}[A-Za-z \-,&.]+\.',
                                 pagetext[page_number])
        if 1 < debug < 5 and title_parts:
            print('title parts: %s' % title_parts)

        # Join all returned lines together in temp_title. Strip extra spaces and use title capitalization.
        # Any word with an apostrophe comes out with a space before the apostrophe and the next letter
        # capitalized. Fix in a future version.
        for t in title_parts:
            temp_title = temp_title + " " + t
        temp_title = re.sub(r'\n', ' ', temp_title)
        temp_title = temp_title.strip()
        temp_title = re.sub(r' {2,}', " ", temp_title)
        temp_title = temp_title.title()
        temp_title = journaltools.capitalize_title(temp_title)
        # Print processed title at debug levels 1-4.
        if 0 < debug < 5 and temp_title:
            print('TITLE: %s' % temp_title)

        # If title is at least four characters long, append to title list. This should be enough to get rid of
        # garbage lines, but short enough to keep short ones. Look for original page number in OCR text, and
        # if found append to start_page list. If not, append placeholder string. Append the page number of the
        # PDF file to start_pdf_page list.
        if len(temp_title) > 5:
            title.append(temp_title)
            original_page_number = re.search(r'^[\d]{1,4}$', pagetext[page_number], re.MULTILINE)
            if original_page_number:
                start_page.append(original_page_number[0])
            else:
                start_page.append(" ")
            start_pdf_page.append(page_number)
            if 0 < debug < 5:
                if original_page_number:
                    print('Start page in PDF text: %s' % original_page_number[0])
                else:
                    print('No start page found in PDF text')

        # Find authors. If one or two lines
        # are returned, append them to temp_author. Append the current PDF file page to end_pdf_page.
        temp_author = re.findall(
            r'(?<=\n)[A-Z][A-Za-z]*\.? +[A-Z][A-Za-z]*\.? +[A-Za-z]+\.?[,. A-Za-z]{0,6}\*?(?=\n)|'
            r'(?<=\n)[A-Z][A-Za-z]+ +[A-Z][a-z]+[,. A-Za-z]{0,6}\*?(?=\n)|'
            r'(?<=\n)[A-Z][A-Za-z]*\.? *[A-Z][a-z]*\.? +[A-Za-z]+\.? +[A-Za-z]+\.?[,. A-Za-z]{0,6}\*?(?=\n)',
            pagetext[page_number])
        if temp_author:
            author1.append(temp_author[0])
            if len(temp_author) == 2:
                author2.append(temp_author[1])
            else:
                author2.append("")
            end_pdf_page.append(page_number)
        if 0 < debug < 5:
            print('Author: %s' % temp_author)
        if 1 < debug < 5:
            print(f'PDF start pages: {start_pdf_page}')
            print(f'PDF end pages: {end_pdf_page}')
    if len(start_pdf_page) > len(end_pdf_page):
        end_pdf_page.append(page_number)

    # Compare lists to see if they contain the same number of values. If not, then pad out the short lists with
    # empty values and throw a warning. Evaluation is in two groups: The values updated when a title is found,
    # and the values updated when an author is found.
    if len(title) > len(author1):
        print('WARNING! Missing authors and ending PDF pages')
        for r in range(len(author1), len(title)):
            author1.append('')
            author2.append('')
            end_pdf_page.append(0)
    elif len(author1) > len(title):
        print('WARNING! Missing titles, start pages, and starting PDF pages')
        for r in range(len(title), len(author1)):
            title.append('')
            start_page.append('')
            start_pdf_page.append(0)

    # Lots of debugging output
    # Print all of the lists; debug levels 2 & 4
    if debug == 2 or debug == 4:
        print('\n\nAll list values:')
        print(title)
        print(author1)
        print(author2)
        print(start_page)
        print(start_pdf_page)
        print(end_pdf_page)
    # step through each record and print all contents; debug level 6
    if debug == 6:
        print('\n\nAll records:')
        for r in range(0, len(title)):
            print(f'Record {r}: {title[r]}; {author1[r]}; {author2[r]}; {start_page[r]}; {start_pdf_page[r]};'
                  f' {end_pdf_page[r]}')

    # Return all collected metadata lists.
    return title, start_page, start_pdf_page, end_pdf_page, author1, author2


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

    # Split filename from extension before passing to the various functions. Use input filename for template
    # if no output filename specified.
    if args.destination:
        outputFile, outputExtension = os.path.splitext(args.destination)
    else:
        outputFile, outputExtension = os.path.splitext(args.filename)

    # If importCSV is specified, read that file and get StartPDFPage and EndPDFPage to pass to SplitPDFs
    # If no importCSV is selected, process args.filename
    if args.input_file:
        StartPDFPage, EndPDFPage = journaltools.importcsv(args.input_file, args.debug)
    else:
        # Fetch OCR page text from PDF file at args.filename.
        pageText = journaltools.getpdf(args.filename, 0, args.verbose, args.debug)
        # Process pages in pageText
        Title, StartPage, StartPDFPage, EndPDFPage, Author1, Author2 = processpdfnew(args.verbose, args.debug, pageText)
        # Export CSV file, or show what output would be if test flag is set
        journaltools.exportcsv(outputFile, args.verbose, args.debug, args.test, Title, StartPage, StartPDFPage,
                               EndPDFPage, Author1, Author2)

    # Split Original PDF into separate documents for each piece, unless test or csvOnly flags are set
    if not args.test and not args.csvOnly:
        journaltools.splitpdf(args.filename, args.verbose, args.debug, StartPDFPage, EndPDFPage, outputFile)
