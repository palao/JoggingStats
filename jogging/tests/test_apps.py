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

from unittest.mock import patch, MagicMock

from django.test import TestCase

from jogging.apps import JoggingConfig
from jogging.signals import run_save_handler


@patch("jogging.apps.post_save")
@patch("jogging.apps.AppConfig")
class JoggingConfigTestCase(TestCase):
    """This is a very implementation dependent test case because
    it must fulfill the Django way to register signals."""
    
    def test_ready_method_registers_handler_for_post_save(
            self, pAppConfig, ppost_save):
        JoggingConfig.path = "."
        conf = JoggingConfig("jogging", "jogging.apps")
        conf.get_model = MagicMock()
        conf.ready()
        ppost_save.connect.assert_called_once_with(
            run_save_handler, sender=conf.get_model.return_value
        )
        conf.get_model.assert_called_once_with("Run")
        



