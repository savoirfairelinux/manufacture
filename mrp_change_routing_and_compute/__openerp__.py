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
    'name': ' mrp_change_routing_and_compute',
    'version': '7.0.1.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'MRP',
    'summary': 'MRP - In Manufacturing Order, allow to change routing and recompute Work Orders',
    'description': """
MRP - In Manufacturing Order, allow to change routing and recompute Work Orders
===============================================================================

By default, this button is only visible in 'New' state.

When manufacturing order is created by the system, from a procurement order, they arrive in the system with status
'Ready to produce' or 'Awaiting Raw Materials'; the work orders, duration and number of cycles are computed from
the routing set on the product's Bill of Material.

This module answer the use-case in which, the routing can not be defined automatically or has to be changed before
going into production : a machine broke, choose the machine according to the current load or the current mould
configuration... Hence, the BoM has an "Unassigned" virtual routing and the production manager has to assign the
correct routing before starting to produce.

With this module, managers can change routing on Manufacturing Orders with status 'Ready to produce' or
'Awaiting Raw Materials'.
Once the routing is changed, the manager can recompute the Work Orders.

Finally, the routing can also be change while manufacturing order is in 'In Production' state :
 -  in case of unplanned interruption;
 - or to to suspend MOs (by creating a virtual 'Suspended' routing)

Contributors
------------
* Vincent Vinet (vincent.vinet@savoirfairelinux.com)
* Marc Cassuto (marc.cassuto@savoirfairelinux.com)
""",
    'depends': [
        'mrp',
    ],
    'data': [
        'mrp_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
