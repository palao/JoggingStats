########################################################################
#
#  Copyright (c) 2020 David Palao
#
#  This file is part of JoggingStats.
#
#  JoggingStats is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  JoggingStats is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with JoggingStats. If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

import re
from collections import namedtuple


KEY = r"(?P<KEY>[a-zA-Z_]+)"
COMPARISON = r"(?P<COMPARISON>EQ|eq|NE|ne|GT|gt|LT|lt)"
LOGICAL = r"(?P<LOGICAL>and|AND|or|OR)"
L_PAR = r"(?P<L_PAR>[(])"
R_PAR = r"(?P<R_PAR>[)])"
DATE = r"(?P<DATE>\d{4}[-]\d{1,2}[-]\d{1,2})"
NUM = r"(?P<NUM>\d+(\.\d*)?)"
TIME = r"(?P<TIME>\d+:\d{1,2}(:\d{1,2}(\.\d+)?)?)"
STRING = r"""(?P<quote>['"])(?P<STRING>[-a-zA-Z_ ]*?)(?P=quote)"""

pattern = re.compile("|".join(
    [COMPARISON, LOGICAL, STRING, KEY, DATE, TIME, NUM, L_PAR, R_PAR]
))


Token = namedtuple("Token", ["type", "value"])


def _generate_tokens(text):
    for m in re.finditer(pattern, text):
        kind = m.lastgroup
        if kind == "STRING":
            value = m.group(kind)
        else:
            value = m.group().lower()
        yield Token(kind, value)


make_Qexpr_from_search_string = None

