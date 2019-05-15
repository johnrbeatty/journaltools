import argparse
import os
import re

from journaltools import getpdf

# for exportcsv
from journaltools import splitname
import csv


def processpdfnew(verbose, debug, page_text):
    # This is the main processing function. It looks through each page of the list passed to it and tries to pull
    # as much metadata as it can find.

    # The format of this journal is: the first page of each issue contains a header that has the journal name,
    # volume number, issue number, month and year, and then the article title in mixed case, then the author in all
    # caps. That will usually be followed by the first heading of the article. Subsequent articles will follow this
    # format without the header. Subsequent pages will feature a header containing the journal title, page number, and
    # alternating volume and years, in arabic numerals. Each piece of both headers is on its own line in the PDF.
    # The title will be broken into multiple lines, with blank lines between some lines. There seems to be no
    # rhyme or reason to the pattern of blank lines. The author is always last, so the algorithm takes everything
    # that it doesn't recognize as an author or a piece of a heading as a piece of the title.

    # Process each page. Step through pages and attempt to find titles, authors, and page numbers in OCR text.
    # Store this metadata and the start and end pages of each article into lists.
    if verbose:
        print(f'Processing PDF pages')

    title = ''
    volume = 0
    start_page = 0
    issue_number = 0
    year = ''
    month = ''
    author = []
    doc_type = ''

    for page_number in range(0, 3):

        if 0 < debug < 6:
            print('Processing PDF page number %d' % page_number)

        if page_number == 0:
            # Process first page. Split page into lines, then step through lines
            page_lines = page_text[page_number].splitlines()
            if 2 < debug < 5:
                print(f'{page_lines}')
            line = 0
            author_flag = 0
            header_flag = 0
            # Step through lines looking for metadata until all authors are found (author_flag == 2). The general
            # format of BLR for the first page of an issue is a header with the journal name, number, month and year,
            # then the article title, then authors. The remainder of the issue will not have the full issue header,
            # but may have a designation of "essay" or "comment." The lines of the titles may be interwoven with
            # the header. The only thing that is consistent is that the authors have always been last. So once the
            # authors appear, there is no more metadata to gather.
            while author_flag < 2:
                line += 1
                if 1 < debug < 5:
                    print(f'Line: {line}')
                    print(page_lines[line])
                # Check to make sure that we're not past the last line. If we're at the end of the page, then there
                # is either no author or the author wasn't found. Set the author_flag to 2 and end the loop so we
                # avoid throwing an error. But give the user a warning.
                if line == len(page_lines):
                    print('WARNING! No author found. Title probably incorrect (and very long).')
                    author_temp = '', '', '', ''
                    author.append(author_temp)
                    author_flag = 2
                    continue
                # Skip empty lines. If the author flag is set to 1 (at least one author has been found), then a blank
                # line should mean all the authors are found and the next line will be the start of the text or a
                # heading just before the text. Set the author_flag to 2 to end the loop and avoid pulling in an
                # all-caps heading as an author.
                if page_lines[line] == '' or page_lines[line] == ' ':
                    if author_flag == 0:
                        continue
                    elif author_flag == 1:
                        author_flag = 2
                # If the header_flag is set, look for the issue number, month and year, and volume number.
                if header_flag == 1:
                    if volume == 0:
                        volume_test = re.search(r'(?<=VOLUME )\d{1,3}', page_lines[line])
                        if volume_test is not None:
                            volume = volume_test[0]
                            continue
                    if issue_number == 0:
                        issue_test = re.search(r'(?<=NUMBER )\d', page_lines[line])
                        if issue_test is not None:
                            issue_number = issue_test[0]
                            continue
                    if year == '':
                        date_parts = re.search(r'([A-Z]+) (\d{4})', page_lines[line])
                        if date_parts is not None:
                            month = date_parts[1]
                            year = date_parts[2]
                            continue
                # If the line is the journal name, the issue header should be present. Set the header_flag.
                if re.match(r'Buffalo Law Review|BUFFALO LAW REVIEW', page_lines[line]):
                    header_flag = 1
                    continue
                # If the line is a document type header, set the doc_type, then move to the next loop cycle to
                # avoid adding the document type to the title.
                if re.match(r'ESSAY ?', page_lines[line]):
                    doc_type = 'essay'
                    continue
                if re.match(r'COMMENT ?', page_lines[line]):
                    doc_type = 'comment'
                    continue
                # Look for something that looks like an author. It will be in all caps and may have one or more
                # symbols at the end (designating the author's biographical information).
                author_search = re.search(r'([A-ZÁÄÀÉËÈÍÏÌÑÓÖÙ]+ [A-ZÁÄÀÉËÈÍÏÌÑÓÖÙ]+\.? ?[A-ZÁÄÀÉËÈÍÏÌÑÓÖÙ]*,? ?'
                                          r'[A-ZÁÄÀÉËÈÍÏÌÑÓÖÙ]*\.?)\W* ?$', page_lines[line])
                # If an author hasn't been found, then this must be part of the title. If the author_flag is still 0
                # (no authors have been found), add the line to the title, unless it's already 254 characters.
                # If the author flag is set to 1, then the whole title has been found already and this must be the
                # start of the paper. Set the author_flag to 2 to end the loop.
                if author_search is None:
                    if author_flag == 0:
                        if len(title) < 255:
                            title = title + page_lines[line]
                    elif author_flag == 1:
                        author_flag = 2
                else:
                    author_temp = author_search[1].title()
                    f_name, m_name, l_name, suffix = splitname(author_temp)
                    author_temp = f_name, m_name, l_name, suffix
                    author.append(author_temp)
                    author_flag = 1
            # Post-processing. Strip spaces from beginning and end of title. Set doc_type to article if it isn't
            # already set to something else. Look for the page number and set.
            title = title.strip()
            if doc_type == '':
                doc_type = 'article'
            original_page_number = re.search(r'^([\d]{1,4}) ?$', page_text[page_number], re.MULTILINE)
            if original_page_number:
                start_page = original_page_number[1]
        else:
            # If volume and year were not on the front page, look for them on the next two pages.
            # Process first page. Split page into lines, then step through lines
            try:
                page_lines = page_text[page_number].splitlines()
            except IndexError:
                continue
            if 2 < debug < 5:
                print(f'{page_lines}')
            for line in range(0,10):
                if 1 < debug < 3:
                    print(f'Line: {line}')
                    print(f'{page_lines[line]}')
                if volume == 0:
                    volume_test = re.search(r'(?<=Vol.) +([\dXVILC]{1,3})', page_lines[line])
                    if volume_test is not None:
                        volume = volume_test[0]
                if year == '':
                    year_test = re.search(r'^[\d]{4}[\-—–][\d]{4}|^[\d]{4}', page_lines[line])
                    if year_test is not None:
                        year = year_test[0]
                        if 1 < debug < 3:
                            print(f'Year: {year}, Line: {line}')

    if 0 < debug < 5:
        print(f'{volume}, {month}, {year}, {issue_number}, {author}, {title}, {start_page}, {doc_type}')

    return title, volume, start_page, issue_number, month, year, doc_type, author


def exportcsv(output_file, verbose, debug, test, title, volume, start_page, issue_number, month, year,
              document_type, author):
    # This takes a filename, creates that file and then basically just dumps all of the passed lists into the file.
    # It does also write column headers. They are not, strictly speaking, necessary. Especially because all of the
    # code here assumes that any file it uses was generated by it and pulls the data from hard-coded column numbers.
    # However, inclusion of column headers makes it easier for the user to edit the CSV file by hand to correct the
    # metadata using a spreadsheet program because the program is less likely to screw up the file when it saves the
    # changes if there are headers. LibreOffice is, anyway. If you're using Excel, all bets are off. Changing to
    # delimiter to tab might help Excel editing.

    # Also, the import code should probably check the headers and make sure it's pulling in the right columns.

    # Initialize empty author variables.
    for r in range(len(author), 4):
        author.append('')
    f_name1 = ''
    m_name1 = ''
    l_name1 = ''
    suffix1 = ''
    f_name2 = ''
    m_name2 = ''
    l_name2 = ''
    suffix2 = ''
    f_name3 = ''
    m_name3 = ''
    l_name3 = ''
    suffix3 = ''
    f_name4 = ''
    m_name4 = ''
    l_name4 = ''
    suffix4 = ''

    # Export collected metadata to CSV file. If test flag set, display metadata instead.
    if not test:

        # Set export filename. Replace pdf extension in processed file with csv extension.
        export_file = output_file + '.csv'

        # Check if file exists. If not, set a flag so that the header gets written.
        if os.path.isfile(export_file):
            header_flag = 1
        else:
            header_flag = 0

        # Open export file.
        with open(export_file, "a+", newline='\n') as csvfile:
            # Set options for CSV writer.
            data_writer = csv.writer(
                csvfile,
                delimiter=',',
                quotechar='"',
                doublequote=True,
                escapechar=" ",
                quoting=csv.QUOTE_MINIMAL)
            # Write column headers
            if header_flag == 0:
                data_writer.writerow(['title', 'volume', 'start_page', 'issue', 'month', 'year', 'document_type',
                                      'f_name1', 'm_name1', 'l_name1', 'suffix1', 'f_name2', 'm_name2', 'l_name2',
                                      'suffix2', 'f_name3', 'm_name3', 'l_name3', 'suffix3', 'f_name4', 'm_name4',
                                      'l_name4', 'suffix4'])
            # Step through each record and write to CSV
            # Split each author name into separate fields before write. Note that this call works without
            # clearing the values each time because SplitName returns blank strings if there is no value.
            # This could probably handle multiple authors better, but it's hard coded to four, like Digital Commons.
            if author[0]:
                f_name1, m_name1, l_name1, suffix1 = author[0]
            if author[1]:
                f_name2, m_name2, l_name2, suffix2 = author[1]
            if author[2]:
                f_name3, m_name3, l_name3, suffix3 = author[2]
            if author[3]:
                f_name4, m_name4, l_name4, suffix4 = author[3]
            if debug:
                print(f'{title}, {volume}, {start_page}, {issue_number}, {month}, {year}, {document_type}, {f_name1}, '
                      f'{m_name1}, {l_name1}, {suffix1}, {f_name2}, {m_name2}, {l_name2}, {suffix2}, {f_name3}, '
                      f'{m_name3}, {l_name3}, {suffix3}, {f_name4}, {m_name4}, {l_name4}, {suffix4}')
            data_writer.writerow(
                [title, volume, start_page, issue_number, month, year, document_type, f_name1, m_name1, l_name1,
                 suffix1, f_name2, m_name2, l_name2, suffix2, f_name3, m_name3, l_name3, suffix3, f_name4, m_name4,
                 l_name4, suffix4])
        csvfile.close()
        if verbose:
            print("Data written to file: %s" % export_file)
    else:
        # Show test export data
        print("\nTest export data:")
        if author[0]:
            f_name1, m_name1, l_name1, suffix1 = author[0]
        if author[1]:
            f_name2, m_name2, l_name2, suffix2 = author[1]
        if author[2]:
            f_name3, m_name3, l_name3, suffix3 = author[2]
        if author[3]:
            f_name4, m_name4, l_name4, suffix4 = author[3]
        print(f'{title}, {volume}, {start_page}, {issue_number}, {month}, {year}, {document_type}, {f_name1}, '
              f'{m_name1}, {l_name1}, {suffix1}, {f_name2}, {m_name2}, {l_name2}, {suffix2}, {f_name3}, {m_name3}, '
              f'{l_name3}, {suffix3}, {f_name4}, {m_name4}, {l_name4}, {suffix4}')


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
                        help='Use supplied filename as filename for the output csv file. Default is <input '
                             'filename>.csv',
                        )
    args = parser.parse_args()

    # Split filename from extension before passing to the various functions. Use input filename for template
    # if no output filename specified.
    if args.destination:
        outputFile, outputExtension = os.path.splitext(args.destination)
    else:
        outputFile, outputExtension = os.path.splitext(args.filename)

    # Fetch OCR page text from PDF file at args.filename.
    pageText = getpdf(args.filename, 3, args.verbose, args.debug)
    # Process pages in pageText
    title, volume, fpage, issue, month, year, document_type, authors = processpdfnew(args.verbose, args.debug,
                                                                                     pageText)
    # Export CSV file, or show what output would be if test flag is set
    exportcsv(outputFile, args.verbose, args.debug, args.test, title, volume, fpage, issue, month, year,
              document_type, authors)
