# Copyright 2013 Cloudera Inc.
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


"""
This test module simply wraps _dbapi20_tests.py, which ensure that our
PEP 249 implementation is compliant.
"""


from __future__ import absolute_import, print_function

import pytest

import impala.dbapi
from impala.tests.util import ImpylaTestEnv
from impala.util import (
    _random_id, force_drop_impala_database, force_drop_hive_database)
# must import the module, rather than the class, per comment in module
from impala.tests import _dbapi20_tests


ENV = ImpylaTestEnv()
tmp_db = _random_id('tmp_impyla_dbapi_')
hive = ENV.auth_mech == 'PLAIN'


@pytest.mark.connect
class ImpalaDBAPI20Test(_dbapi20_tests.DatabaseAPI20Test):
    driver = impala.dbapi
    connect_kw_args = {'host': ENV.host,
                       'port': ENV.port,
                       'auth_mechanism': ENV.auth_mech,
                       'database': tmp_db}

    ddl1 = 'create table {0}booze (name string)'.format(
        _dbapi20_tests.DatabaseAPI20Test.table_prefix)
    ddl2 = 'create table {0}barflys (name string)'.format(
        _dbapi20_tests.DatabaseAPI20Test.table_prefix)

    @classmethod
    def setUpClass(cls):
        con = cls.driver.connect(host=ENV.host, port=ENV.port,
                                 auth_mechanism=ENV.auth_mech)
        cur = con.cursor()
        cur.execute('CREATE DATABASE {0}'.format(tmp_db))
        cur.close()
        con.close()

    @classmethod
    def tearDownClass(cls):
        con = cls.driver.connect(host=ENV.host, port=ENV.port,
                                 auth_mechanism=ENV.auth_mech)
        cur = con.cursor()
        if hive:
            force_drop_hive_database(cur, tmp_db)
        else:
            force_drop_impala_database(cur, tmp_db)
        cur.close()
        con.close()

    def test_nextset(self):
        pass

    def test_setoutputsize(self):
        pass

    # The following tests fail against Hive. We override them so we can skip on
    # Hive, and otherwise execute the superclass version.

    HIVE_STRING_ESCAPE_ERROR = 'HIVE-11723'

    @pytest.mark.skipif(hive, reason=HIVE_STRING_ESCAPE_ERROR)
    def test_execute(self):
        super(ImpalaDBAPI20Test, self).test_execute()

    @pytest.mark.skipif(hive, reason=HIVE_STRING_ESCAPE_ERROR)
    def test_executemany(self):
        super(ImpalaDBAPI20Test, self).test_executemany()

    @pytest.mark.skipif(hive, reason=HIVE_STRING_ESCAPE_ERROR)
    def test_setinputsizes(self):
        super(ImpalaDBAPI20Test, self).test_setinputsizes()

    @pytest.mark.skipif(hive, reason=HIVE_STRING_ESCAPE_ERROR)
    def test_setoutputsize_basic(self):
        super(ImpalaDBAPI20Test, self).test_setoutputsize_basic()
