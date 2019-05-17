import argparse
import os
import re

import journaltools

# This version of dsplit is set up to extract metadata from and split recent decisions in the Buffalo Law Review. Those
# book reviews have a title in all caps at the top, then whitespace, then the text, followed by more whitespace and
# the author. They're very similar to the book reviews, except for the all-caps title and less whitespace.
# It should be a good starting point for other similar journal segments.


def processpdfnew(verbose, debug, page_text):
    # This is the main processing function. It looks through each page of the list passed to it and tries to pull
    # as much metadata as it can find. This file is designed to be copied and rewritten for each type of source
    # that needs to be processed. As long as you don't need any more metadata than title, one or two authors, and start
    # page, only this file needs to be changed.

    # Create lists for all values to be exported to CSV file. Each index value will correspond to the metadata
    # for one article across all lists. This code assumes that there will be no more than two authors on each article.
    title = []
    author = []
    start_page = []
    start_pdf_page = []
    end_pdf_page = []

    # Process each page. Step through pages and attempt to find titles, authors, and page numbers in OCR text.
    # Store this metadata and the start and end pages of each article into lists.
    if verbose:
        print(f'Processing PDF pages')

    for page_number in range(0, len(page_text)):

        if 0 < debug < 6:
            print('Processing PDF page number %d' % page_number)

        # look for an article title on this page, add lines to title_parts,
        # then add them together and title capitalize
        temp_title = ""
        # Look for all lines that consist only of three or more of the following characters on their own line:
        # all caps, spaces, hyphens and single quotes.
        title_parts = re.findall(r'(?<=\n)[A-Z §.:"\'\-]{3,}(?=\n)', page_text[page_number], flags=0)
        if 1 < debug < 5 and title_parts:
            print('Title parts: %s' % title_parts)

        # Join all returned lines together in temp_title. Strip extra spaces and use title capitalization.
        # Any word with an apostrophe comes out with a space before the apostrophe and the next letter
        # capitalized. Fix in a future version.
        for t in title_parts:
            temp_title = temp_title + ' ' + t
        temp_title = temp_title.strip()
        temp_title = re.sub(r' {2,}', ' ', temp_title)
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
            original_page_number = re.search(r'^[\d]{1,4}$', page_text[page_number], re.MULTILINE)
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
        # are returned, append them to find_author. Append the current PDF file page to end_pdf_page.
        find_author = re.findall(
            r'(?<=\n)[A-Z][A-Za-z]*\.? +[A-Z][a-z]*\.? +[A-Za-z]+\.?[,. A-Za-z]{0,6}(?=\n)|'
            r'(?<=\n)[A-Z][A-Za-z]+ +[A-Z][a-z]+[,. A-Za-z]{0,6}(?=\n)|'
            r'(?<=\n)[A-Z][A-Za-z]*\.? +[A-Z][a-z]*\.? +[A-Za-z]+\.? +[A-Za-z]+\.?[,. A-Za-z]{0,6}(?=\n)',
            page_text[page_number])
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
            end_pdf_page.append(page_number)
        if 0 < debug < 5:
            print('Author: %s' % find_author)
        if 1 < debug < 5:
            print(f'PDF start pages: {start_pdf_page}')
            print(f'PDF end pages: {end_pdf_page}')

    # Compare lists to see if they contain the same number of values. If not, then pad out the short lists with
    # empty values and throw a warning. Evaluation is in two groups: The values updated when a title is found,
    # and the values updated when an author is found.
    if len(title) > len(author):
        print('WARNING! Missing authors and ending PDF pages')
        for r in range(len(author), len(title)):
            author.append([('', '', '', ''), ('', '', '', ''), ('', '', '', ''), ('', '', '', '')])
            end_pdf_page.append(0)
    elif len(author) > len(title):
        print('WARNING! Missing titles, start pages, and starting PDF pages')
        for r in range(len(title), len(author)):
            title.append('')
            start_page.append('')
            start_pdf_page.append(0)

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
                    'Buffalo Law Review recent decisions or case notes.'
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
