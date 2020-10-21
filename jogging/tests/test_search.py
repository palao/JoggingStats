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

import unittest
from unittest.mock import patch

from jogging.search import (
    make_Qexpr_from_search_string, _generate_tokens, Token, QexprBuilder,
)


TEST_CASES = {
    "(date eq '2020-10-23')": (
        [
            Token(type='L_PAR', value='('),
            Token(type='KEY', value='date'),
            Token(type='COMPARISON', value='eq'),
            Token(type='DATE', value='2020-10-23'),
            Token(type='R_PAR', value=')')
        ],
        "(AND: ('date', '2020-10-23'))"
    ),
    "(distance gt 23)": (
        [
            Token(type='L_PAR', value='('),
            Token(type='KEY', value='distance'),
            Token(type='COMPARISON', value='gt'),
            Token(type='NUM', value='23'),
            Token(type='R_PAR', value=')')
        ],
        "(AND: ('distance__gt', 23.0))"
    ),
    "(time gt '11')": (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='time'), Token(type='COMPARISON', value='gt'), Token(type='NUM', value='11'), Token(type='R_PAR', value=')')],
        "(AND: ('time__gt', 11.0))"
    ),
    "(time gt '11:23')": (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='time'), Token(type='COMPARISON', value='gt'), Token(type='TIME', value='11:23'), Token(type='R_PAR', value=')')],
        "(AND: ('time__gt', '11:23'))",
    ),
    "(time lt '11:23:23.3')": (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='time'), Token(type='COMPARISON', value='lt'), Token(type='TIME', value='11:23:23.3'), Token(type='R_PAR', value=')')],
        "(AND: ('time__lt', '11:23:23.3'))"
    ),
    '(location ne "Talavera de la Reina")': (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='location'), Token(type='COMPARISON', value='ne'), Token(type='STRING', value='Talavera de la Reina'), Token(type='R_PAR', value=')')],
        "(NOT (AND: ('location', 'Talavera de la Reina')))"
    ),
    "(distance gt 20) OR (distance lt 10)": (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='distance'), Token(type='COMPARISON', value='gt'), Token(type='NUM', value='20'), Token(type='R_PAR', value=')'), Token(type='LOGICAL', value='or'), Token(type='L_PAR', value='('), Token(type='KEY', value='distance'), Token(type='COMPARISON', value='lt'), Token(type='NUM', value='10'), Token(type='R_PAR', value=')')],
        "(OR: ('distance__gt', 20.0), ('distance__lt', 10.0))"
    ),
    "(date eq '2020-10-23') AND ((distance gt 20) OR (distance lt 10))": (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='date'), Token(type='COMPARISON', value='eq'), Token(type='DATE', value='2020-10-23'), Token(type='R_PAR', value=')'), Token(type='LOGICAL', value='and'), Token(type='L_PAR', value='('), Token(type='L_PAR', value='('), Token(type='KEY', value='distance'), Token(type='COMPARISON', value='gt'), Token(type='NUM', value='20'), Token(type='R_PAR', value=')'), Token(type='LOGICAL', value='or'), Token(type='L_PAR', value='('), Token(type='KEY', value='distance'), Token(type='COMPARISON', value='lt'), Token(type='NUM', value='10'), Token(type='R_PAR', value=')'), Token(type='R_PAR', value=')')],
        "(AND: ('date', '2020-10-23'), (OR: ('distance__gt', 20.0), ('distance__lt', 10.0)))"
    ),
    "(date ne '2020-10-23') AND ((distance gt 20) OR (distance lt 10))": (
        [Token(type='L_PAR', value='('), Token(type='KEY', value='date'), Token(type='COMPARISON', value='ne'), Token(type='DATE', value='2020-10-23'), Token(type='R_PAR', value=')'), Token(type='LOGICAL', value='and'), Token(type='L_PAR', value='('), Token(type='L_PAR', value='('), Token(type='KEY', value='distance'), Token(type='COMPARISON', value='gt'), Token(type='NUM', value='20'), Token(type='R_PAR', value=')'), Token(type='LOGICAL', value='or'), Token(type='L_PAR', value='('), Token(type='KEY', value='distance'), Token(type='COMPARISON', value='lt'), Token(type='NUM', value='10'), Token(type='R_PAR', value=')'), Token(type='R_PAR', value=')')],
        "(AND: (NOT (AND: ('date', '2020-10-23'))), (OR: ('distance__gt', 20.0), ('distance__lt', 10.0)))"
    ),
}


@patch("jogging.search.QexprBuilder")
class MakeQexprFromSearchString(unittest.TestCase):
    def test_delegates_to_QexprBuilder(self, pQexprBuilder):
        res = make_Qexpr_from_search_string("something")
        self.assertEqual(res, pQexprBuilder.return_value.parse.return_value)
        pQexprBuilder.return_value.parse.assert_called_once_with("something")


class TokenGeneratorTestCase(unittest.TestCase):
    def test_regular_values(self):
        for text, (tokens, strQ) in TEST_CASES.items():
            self.assertEqual(
                list(_generate_tokens(text)),
                tokens
            )


class QexprBuilderTestCase(unittest.TestCase):
    def test_regular_values(self):
        b = QexprBuilder()
        for text, (tokens, strQ) in TEST_CASES.items():
            self.assertEqual(
                str(b.parse(text)),
                strQ
            )
