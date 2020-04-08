# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Subset for web fonts."""

__authors__ = [
    'roozbeh@google.com (Roozbeh Pournader)',
    'm.foley.88@gmail.com (Marc Foley)'
]

import sys
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from nototools import subset


def read_charlist(filename):
    """Returns a list of characters read from a charset text file."""
    with open(filename) as datafile:
        charlist = []
        for line in datafile:
            if '#' in line:
                line = line[:line.index('#')]
            line = line.strip()
            if not line:
                continue
            if line.startswith('U+'):
                line = line[2:]
            char = int(line, 16)
            charlist.append(char)
        return charlist


def touchup_for_web(ttfont):
    """Apply fixes needed for web fonts."""

    # set vertical metrics to old values
    hhea = ttfont['hhea']
    hhea.ascent = 1900
    hhea.descent = -500

    os2 = ttfont['OS/2']
    os2.sTypoAscender = 1536
    os2.sTypoDescender = -512
    os2.sTypoLineGap = 102
    os2.usWinAscent = 1946
    os2.usWinDescent = 512

    roman = instantiateVariableFont(ttfont, {"ital": 0.0})
    italic = instantiateVariableFont(ttfont, {"ital": 1.0})
    dir_name = os.path.dirname(ttfont.reader.file.name)
    roman_filename = os.path.join(dir_name, "Roboto[wdth,wght].ttf")
    italic_filename = os.path.join(dir_name, "Roboto-Italic[wdth,wght].ttf")
    roman.save(roman_filename)
    italic.save(italic_filename)
    ttfont.save(ttfont.reader.file.name)


def main(argv):
    """Subset the first argument to second, dropping unused parts of the font.
    """
    charlist = read_charlist(os.path.join(os.path.dirname(__file__), 'web_subset.txt'))
    # Add private use characters for legacy reasons
    charlist += [0xEE01, 0xEE02, 0xF6C3]

    features_to_keep = [
        'c2sc', 'ccmp', 'cpsp', 'dlig', 'dnom', 'frac', 'kern', 'liga', 'lnum',
        'locl', 'numr', 'onum', 'pnum', 'smcp', 'ss01', 'ss02', 'ss03', 'ss04',
        'ss05', 'ss06', 'ss07', 'tnum']

    source_filename = argv[1]
    target_filename = argv[2]
    subset.subset_font(
        source_filename, target_filename,
        include=charlist,
        options={'layout_features': features_to_keep})
    
    web_ttfont = TTFont(target_filename)
    touchup_for_web(web_ttfont)


if __name__ == '__main__':
    main(sys.argv)