# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'MRP Produce only if Started',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Manufacturing',
    'summary': 'MRP - produce only if MO has been marked as started first',
    'description': """
MRP - Produce only if Started
=============================

In some case, you need to prepare a machine before starting the production
(cleaning, change a mould...). In that case, you don't want the operator to
start the production if a production order has not been marked as started
first.

Without this module, in MO "Produce" button appears as soon as the MO is
"Ready to produce"; you can start to produce without clicking on the
"Mark as Started" button.

This module forces clicking on the "Mark as Started" button before being able
to click on "Produce".

Contributors
------------
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
""",
    'depends': [
        'mrp',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'mrp_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
