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

from django.db.models import Q


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


def make_Qexpr_from_search_string(text):
    return QexprBuilder().parse(text)


def _generate_tokens(text):
    for m in re.finditer(pattern, text):
        kind = m.lastgroup
        if kind == "STRING":
            value = m.group(kind)
        else:
            value = m.group().lower()
        yield Token(kind, value)


class QexprBuilder:
    def parse(self, text):
        self.tokens = _generate_tokens(text)
        self.tok = None
        self.nexttok = None
        self.nextnexttok = None
        self._advance()
        return self.expr()

    def _advance(self):
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)

    def _accept(self, *toktypes):
        if self.nexttok and self.nexttok.type in toktypes:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype):
        if not self._accept(toktype):
            raise SyntaxError(f"Expected '{toktype}'")

    def expr(self):
        exprval = self.query()
        while self._accept("LOGICAL"):
            op = self.tok.value
            right = self.query()
            if op == "and":
                exprval = (exprval & right)
            elif op == "or":
                exprval = (exprval | right)
        return exprval

    def query(self):
        if self._accept("KEY"):
            key = self.tok.value
            suffix, ne = self._parse_op()
            value = self._parse_value()
            d = {f"{key}{suffix}": value}
            q = Q(**d)
            if ne:
                q = ~q
            return q
        elif self._accept("L_PAR"):
            exprval = self.expr()
            self._expect("R_PAR")
            return exprval
        else:
            raise SyntaxError("Expected L_PAR or KEY")

    def _parse_op(self):
        if self._accept("COMPARISON"):
            op = self.tok.value
            suffix = ""
            ne = False
            if op in ("lt", "gt"):
                suffix += f"__{op}"
            elif op == "ne":
                ne = True
            elif op == "eq":
                pass
            else:
                raise SyntaxError(f"Unknown operator: '{op}'")
        else:
            raise SyntaxError("Expected COMPARISON")
        return suffix, ne

    def _parse_value(self):
        if self._accept("NUM", "STRING", "DATE", "TIME"):
            val = self.tok.value
            if self.tok.type == "NUM":
                val = float(val)
            return val
        else:
            raise SyntaxError("Expected NUM, STRING, DATE or TIME")

