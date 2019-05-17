import argparse
import os
import re

import journaltools

# This version of dsplit is set up to extract metadata from and split early Court of Appeals term case notes
# in the Buffalo Law Review. Those include a table of contents at the front. The code first pulls what it can from
# the table of contents, then tries to find the start and end PDF pages.
# This one is very specialized and may not be useful as a template for anything else.


def processpdfnew(verbose, debug, pagetext):

    # Create lists for all values to be exported to CSV file. Each index value will correspond to the metadata
    # for one article across all lists. This code assumes that there will be no more than two authors on each article.
    title = []
    author = []
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
        find_author = re.sub(r' {2,}', ' ', toc[r][3])
        find_author = re.split(r' and ', find_author, 2)
        if find_author:
            author_list = []
            for count in range(0, 4):
                try:
                    f_name, m_name, l_name, suffix = journaltools.splitname(find_author[count])
                    author_temp = f_name, m_name, l_name, suffix
                except IndexError:
                    author_temp = '', '', '', ''
                author_list.append(author_temp)
            author.append(author_list)
        start_page.append('')
        if 1 < debug < 5:
            print(f'{title[r]}, {author[r]}')

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
        print(author)
        print(start_page)
        print(start_pdf_page)
        print(end_pdf_page)
    # step through each record and print all contents; debug level 6
    if debug == 6:
        print('\n\nAll records:')
        for r in range(0, len(title)):
            print(f'Record {r}: {title[r]}; {author[r]}; {start_page[r]}; {start_pdf_page[r]};'
                  f' {end_pdf_page[r]}')

    # Return all collected metadata lists.
    return title, start_page, start_pdf_page, end_pdf_page, author


def main():
    parser = argparse.ArgumentParser(
        description='Function to extract metadata and split a PDF containing multiple journal articles. Set up for '
                    'early Buffalo Law Review Court of Appeals term case notes.'
    )
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
                        help="Set debug level (1-6). Levels 1-4 offer increasing levels of output. Level 5 displays "
                             "the PDF text. Level 6 prints all of the records.",
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
        output_file, output_extension = os.path.splitext(args.destination)
    else:
        output_file, output_extension = os.path.splitext(args.filename)

    # If importCSV is specified, read that file and get start_pdf_page and end_pdf_page to pass to SplitPDFs
    # If no importCSV is selected, process args.filename
    if args.input_file:
        start_pdf_page, end_pdf_page = journaltools.importcsv(args.input_file, args.debug)
    else:
        # Fetch OCR page text from PDF file
        page_text = journaltools.getpdf(args.filename, 0, args.verbose, args.debug)
        # Process pages
        title, start_page, start_pdf_page, end_pdf_page, author = processpdfnew(
            args.verbose, args.debug, page_text)
        # Export CSV file, or show what output would be if test flag is set
        journaltools.exportcsvnew(output_file, args.verbose, args.debug, args.test, title, start_page, start_pdf_page,
                                  end_pdf_page, author)

    # Split Original PDF into separate documents for each piece, unless test or csvOnly flags are set
    if not args.test and not args.csvOnly:
        journaltools.splitpdf(args.filename, args.verbose, args.debug, start_pdf_page, end_pdf_page, output_file)


if __name__ == '__main__':
    main()
