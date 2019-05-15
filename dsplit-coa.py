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

    # Get titles and authors from first page--for original format publications
    toc = re.findall(r'([IVXL]{1,4}\.?)\s([A-Za-z0-9., ]+)\s(\(([A-Za-z ]{5,})\))?',
                     pagetext[0], re.DOTALL)
    # Clean up title. Then append titles and authors to title and Author lists. Append blank start page.
    for r in range(0, len(toc)):
        if 0 < debug < 3:
            print(f'Record {r}, {toc[r]}')
        temp_title = toc[r][1]
        temp_title = temp_title.strip()
        temp_title = re.sub(r' {2,}', " ", temp_title)
        temp_title = temp_title.title()
        temp_title = journaltools.capitalize_title(temp_title)
        title.append(temp_title)
        temp_author = re.sub(r' {2,}', ' ', toc[r][3])
        temp_author = re.split(r' and ', temp_author, 2)
        author1.append(temp_author[0])
        if len(temp_author) > 1:
            author2.append(temp_author[1])
        else:
            author2.append('')
        start_page.append('')
        if 1 < debug < 5:
            print(f'{title[r]}, {author1[r]}', author2[r])

    # Process each page. Step through pages and attempt to find titles, authors, and page numbers in OCR text.
    # Store this metadata and the start and end pages of each article into lists.
    if verbose:
        print('Processing PDF pages')

    for page_number in range(1, len(pagetext)):

        if 0 < debug < 6:
            print('Processing PDF page number %d' % page_number)

        # look for an article title on this page
        title_parts = re.search(r'(?<=\n)([XIVHLlixv]{1,4}\.)\s([A-Za-z0-9.,*\- ]*)\s(?=\n)', pagetext[page_number],
                                flags=0)
        if 1 < debug < 5 and title_parts:
            print('title parts: %s' % title_parts)

        # Append temp_title to title list. Don't look for original page number in OCR text, because they didn't come
        # through on these. Append placeholder string for original start page. Append the page number of the
        # PDF file to start_pdf_page list. For every page after the first, append the page number to end_pdf_page.
        # This will add a garbage page to articles that start a page, but there's no great way to determine if
        # the article starts the page.

        if title_parts:
            # OriginalPageNumber = re.search(r'^[\d]{1,4}$', pagetext[page_number], re.MULTILINE)
            # if OriginalPageNumber:
            #     start_page.append(OriginalPageNumber[0])
            # else:
            #     start_page.append(" ")
            start_pdf_page.append(page_number)
            if page_number > 1:
                end_pdf_page.append(page_number)

        if 1 < debug < 5:
            print(f'PDF start pages: {start_pdf_page}')
            print(f'PDF end pages: {end_pdf_page}')

    end_pdf_page.append(page_number)

    # Compare all lists to make sure they contain the same number of items. Add empty items to short lists.
    if len(start_pdf_page) < len(title):
        for r in range(len(start_pdf_page), len(title)):
            start_pdf_page.append(0)
        print('WARNING! Missing Start PDF Page(s)')
    if len(end_pdf_page) < len(title):
        for r in range(len(end_pdf_page), len(title)):
            end_pdf_page.append(0)
        print('WARNING! Missing End PDF Page(s)')

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
