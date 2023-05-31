#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2022 Philipp Wolfer
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
import json
import os.path
import sys
import urllib3


LANGUAGE_MAP = {
    'ms_MY': 'ms',
    'nb': 'nb_NO',
    'zh_TW': 'zh_Hant',
}


def parse_args():
    parser = argparse.ArgumentParser(description="Upload translation files to Weblate Glossary")
    parser.add_argument("-i", "--input", action='store', nargs='*', required=True,
                        help="translation files to upload", dest='files')
    parser.add_argument("-t", "--token", action='store', required=True,
                        help="Weblate API token")
    parser.add_argument("-H", "--host", action='store', default='hosted.weblate.org',
                        help="Weblate host token")
    parser.add_argument("-c", "--component", action='store', required=True,
                        help="The glossary component as {project}/{component_name}")
    args, unparsed_args = parser.parse_known_args()
    return args


def upload_translation(args):
    http = urllib3.PoolManager()
    r = http.request(
        'GET',
        f'https://{args.host}/api/components/{args.component}/',
        headers={
            'Authorization': f'Token {args.token}'
        })
    try:
        component = json.loads(r.data.decode('utf-8'))
    except json.JSONDecodeError:
        print(f'Failed loading {args.component}: {r.status}')
        raise

    if not component['is_glossary']:
        print(f'Component {args.component} is not a glossary')
        sys.exit(1)

    print(f'Using component {component["web_url"]}')

    for path in args.files:
        filename = os.path.basename(path)
        lang, _ext = os.path.splitext(filename)
        lang = LANGUAGE_MAP.get(lang, lang).replace('-', '_')
        print(f'Processing {path} (language {lang})...')
        with open(path) as f:
            file_data = f.read()
        try:
            r = http.request(
                'POST',
                f'https://{args.host}/api/components/{args.component}/translations/',
                headers={
                    'Authorization': f'Token {args.token}',
                    'Content-Type': 'application/json'
                },
                body=json.dumps({'language_code': lang}).encode('utf-8'))
            if r.status in (200, 201):
                print(f'Created language {lang} for component {args.component}')
            else:
                print(f'Failed creating language {lang} for component {args.component}: {r.status}')
                print(r.data)
        except:
            print(f'Failed creating language {lang} for component {args.component}: {r.status}')
            pass
        r = http.request(
            'POST',
            f'https://{args.host}/api/translations/{args.component}/{lang}/file/',
            headers={
                'Authorization': f'Token {args.token}'
            },
            fields={
                'file': (filename, file_data),
                'conflicts': 'ignore',
                'method': 'add',
            })
        print(f'Uploaded file {filename} (add): {r.status}; {r.data}')
        r = http.request(
            'POST',
            f'https://{args.host}/api/translations/{args.component}/{lang}/file/',
            headers={
                'Authorization': f'Token {args.token}'
            },
            fields={
                'file': (filename, file_data),
                'conflicts': 'ignore',
                'method': 'translate',
            })
        print(f'Uploaded file {filename} (translate): {r.status}; {r.data}')


if __name__ == "__main__":
    args = parse_args()
    upload_translation(args)
