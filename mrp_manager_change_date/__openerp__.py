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
    'name': 'MRP - Manager can change date on MO',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Manufacturing',
    'summary': 'MRP - Manager can change date on MO',
    'description': """
In Manufacturing Orders, managers can change date
=================================================

By default, in OpenERP the date of a Manufacturing Order can only been set while creating the MO (status is 'New').

When the MO is triggered from a Procurement Order, the MO arrive in the system with status 'Awaiting Raw Materials' or
'Ready to Produce'; in both case the scheduled date is not modifiable.

With this module, you can modify the scheduled date if the MO is in one of the following state :
'New', 'Awaiting Raw Materials' or 'Ready to Produce'

All of this allow also the manual scheduling of the orders since OpenERP does not manage production capacity

Contributors
------------
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
* Mathieu Benoit (mathieu.benoit@savoirfairelinux.com)
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
