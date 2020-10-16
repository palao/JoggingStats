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

from rest_framework.permissions import BasePermission

from jogging.permissions import IsOwner, IsOwnerOrAdmin


class IsOwnerTestCase(unittest.TestCase):
    def test_is_permission(self):
        self.assertTrue(issubclass(IsOwner, BasePermission))
        
    def test_has_access_if_owner(self):
        class FakeRequest:
            user = "peter"

        class FakeObj:
            owner = "peter"
            
        perm = IsOwner()
        self.assertTrue(
            perm.has_object_permission(FakeRequest(), None, FakeObj())
        )

    def test_has_no_access_if_not_owner(self):
        class FakeRequest:
            user = "peter"

        class FakeObj:
            owner = "paul"
            
        perm = IsOwner()
        self.assertFalse(
            perm.has_object_permission(FakeRequest(), None, FakeObj())
        )
        
class SuperUser:
    is_superuser = True

    
class NormalUser:
    is_superuser = False

    
class IsOwnerOrAdminTestCase(unittest.TestCase):
    def test_is_permission(self):
        self.assertTrue(issubclass(IsOwnerOrAdmin, BasePermission))
        
    def test_has_access_if_owner(self):
        user = NormalUser()
        class FakeRequest:
            ...

        class FakeObj:
            ...

        FakeRequest.user = user
        FakeObj.owner = user
        perm = IsOwnerOrAdmin()
        self.assertTrue(
            perm.has_object_permission(FakeRequest(), None, FakeObj())
        )

    def test_has_no_access_if_not_owner_and_not_superuser(self):
        class FakeRequest:
            user = NormalUser()

        class FakeObj:
            owner = NormalUser()
            
        perm = IsOwnerOrAdmin()
        self.assertFalse(
            perm.has_object_permission(FakeRequest(), None, FakeObj())
        )

    def test_has_access_if_admin(self):            
        class FakeRequest:
            user = SuperUser()

        class FakeObj:
            owner = NormalUser()
            
        perm = IsOwnerOrAdmin()
        self.assertTrue(
            perm.has_object_permission(FakeRequest(), None, FakeObj())
        )
