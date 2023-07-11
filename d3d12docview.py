# d3d12doc.py
"""
The script fetches D3D12 documentation and displays it to standard output
"""

import sys
import urllib
import urllib.request
import re

def parse_d3d12_md_file(file):
    """Parses fetched .md file and returns two containers with parsed information"""

    h2pattern = re.compile(r'(\s*##\s*-)(description|remarks|see-also|enum-fields|struct-fields|inheritance|parameters|returns)')
    h3pattern = re.compile(r'(\s*###\s*-)(param|field)(\s*\w+)')
    href_pattern = re.compile(r'\s*href=\"[\/\w-]+\"')
    mref_pattern = re.compile(r'\((\/{0,1}[\w-]*)+(.md)*\)') #re.compile(r'\([\/*[\w-]+]+\)')
    aref_pattern = re.compile(r'\<\s*a\s*id\s*=\s*\"\w+\"\s*\>\s*\<\s*\/\s*a\s*\>')
    h2_docs = {}
    h3_docs = {}
    key_h2 = None
    key_h3 = None
    for line in file.readlines():
        string = line.decode('utf-8').strip()
        h2match = h2pattern.match(string)
        if h2match:
            key_h2 = h2match.group(2).upper().replace('-', ' ')
            key_h3 = None
        else:
            h3match = h3pattern.match(string)
            if h3match:
                key_h3 = h3match.group(3)
            elif string != '' and key_h2:
                # remove html references 'href="/path/"' for readability
                string = href_pattern.sub('', string)
                # remove markdown references (/path/) for readability
                string = mref_pattern.sub('', string)
                # remove anchors like < a id = "something" > < / a > for readability
                string = aref_pattern.sub('', string)
                if key_h3:
                    if not key_h2 in h3_docs:
                        h3_docs[key_h2] = {}
                    if not key_h3 in h3_docs[key_h2]:
                        h3_docs[key_h2][key_h3] = []
                    h3_docs[key_h2][key_h3].append(string)
                else:
                    if not key_h2 in h2_docs:
                        h2_docs[key_h2] = []
                    h2_docs[key_h2].append(string)
    return (h2_docs, h3_docs)

def print_line_list(prefix, linelist):
    """Merges the list of lines and prints them"""

    print(prefix + ('\n' + prefix).join(linelist), end='\n\n')

DOC_PATH = "https://raw.githubusercontent.com/MicrosoftDocs/sdk-api/docs/sdk-api-src/content/d3d12/"
DOC_ARGS = {
    ("enum", 3) : "ne",
    ("struct", 3) : "ns",
    ("interface", 3) : "nn",
    ("interface", 4) : "nf"
}

def main() -> int:
    """main function"""

    kind = DOC_ARGS[sys.argv[1], len(sys.argv)] if len(sys.argv) >= 3 else None

    if kind:
        path = DOC_PATH + kind + '-d3d12-' + sys.argv[2].lower()
        path += '' if len(sys.argv) == 3 else '-' + sys.argv[3].lower()
        path += '.md'

        try:
            file = urllib.request.urlopen(path)
            with file:
                # parse d3d12 documentation file
                (h2_docs, h3_docs) = parse_d3d12_md_file(file)

                # print most of sections
                for (key, docs) in h2_docs.items():
                    print(key + ':')
                    print_line_list('\t', docs)

                # print parameters/fields
                for (key1, groupdocs) in h3_docs.items():
                    print(key1 + ':')
                    for (key2, elemdocs) in groupdocs.items():
                        print('\t' + key2 + ':')
                        print_line_list('\t\t', elemdocs)

        except urllib.request.HTTPError:
            print("Can't find requested documentation")

    else: # len(sys.argv) >= 3:
        print('Usage:')
        print('\td3d12docview.py enum <enum_name>')
        print('\td3d12docview.py struct <struct_name>')
        print('\td3d12docview.py interface <interface_name> <optional_method_name>')
    return 0

if __name__ == '__main__':
    sys.exit(main())
