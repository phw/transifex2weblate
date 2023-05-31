#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2021 Philipp Wolfer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import csv
from collections import defaultdict
import os
import os.path


def parse_args():
    parser = argparse.ArgumentParser(description="Convert Transifex CSV to TBX files")
    parser.add_argument("-f", "--file", action='store', required=True,
                        help="CSV file to parse")
    parser.add_argument("-o", "--out-dir", action='store', required=True,
                        help="Output directory")
    args, unparsed_args = parser.parse_known_args()
    return args


class GlossaryCsvWriter():
    def __init__(self):
        # define the header
        self.rows = [(
            'location',
            'source',
            'target',
            'id',
            'fuzzy',
            'context',
            'translator_comments',
            'developer_comments',
        )]

    def append(self, row):
        self.rows.append(row)

    def write(self, filepath):
        with open(filepath, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quoting=csv.QUOTE_ALL)
            writer.writerows(self.rows)

    def is_empty(self):
        for row in self.rows:
            if row[2]:
                return False
        return True


class LanguageColumnSpecs:
    def __init__(self):
        self.term = None
        self.comment = None


class ColumnSpecs:
    def __init__(self):
        self.term = None
        self.comment = None
        self.pos = None
        self.translations = defaultdict(LanguageColumnSpecs)


def analyze_header(headers):
    specs = ColumnSpecs()

    for column, header in enumerate(headers):
        if header == "term":
            specs.term = column
        elif header == "notes":
            specs.comment = column
        elif header == "pos":
            specs.pos = column
        elif header.startswith("translation_"):
            language = header[12:]
            specs.translations[language].term = column
        elif header.startswith("notes_"):
            language = header[6:]
            specs.translations[language].comment = column

    return specs


def split_csv(filepath, outdir):
    with open(filepath, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        header = next(reader)
        column_specs = analyze_header(header)
        language_writers = defaultdict(GlossaryCsvWriter)
        for row in reader:
            for lang, lang_spec in column_specs.translations.items():
                print(lang, lang_spec.term, lang_spec.comment)
                writer = language_writers[lang]
                comment = '; '.join(c for c in (row[column_specs.pos], row[column_specs.comment]) if c)
                lang_row = (
                    '',  # location
                    row[column_specs.term].strip(),  # source
                    row[lang_spec.term].strip(),  # target
                    '',  # id
                    'False',  # fuzzy
                    row[column_specs.term].strip(),  # context
                    row[lang_spec.comment],  # translator_comments
                    comment,  # developer_comments
                )
                writer.append(lang_row)

        os.makedirs(outdir, exist_ok=True)
        for lang, _ in column_specs.translations.items():
            writer = language_writers[lang]
            outfile_csv = os.path.join(outdir, f"{lang}.csv")
            if not writer.is_empty():
                writer.write(outfile_csv)


if __name__ == "__main__":
    args = parse_args()
    print(f"Reading {args.file}...")
    split_csv(args.file, args.out_dir)