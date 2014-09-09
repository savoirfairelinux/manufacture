# -*- encoding: utf-8 -*-
###############################################################################
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
###############################################################################

import logging
_logger = logging.getLogger(__name__)

from openerp.osv import orm, fields


class mrp_production(orm.Model):
    _inherit = 'mrp.production'
    _columns = {
        'routing_id': fields.many2one(
            'mrp.routing', string='Routing',
            on_delete='set null', readonly=True,
            states={'draft': [('readonly', False)],
                    'confirmed': [('readonly', False)],
                    'ready': [('readonly', False)],
                    'in_production': [('readonly', False)],
                    },
            help="The list of operations (list of work centers) to produce the finished product. The routing is mainly used to compute work center costs during operations and to plan future loads on work centers based on production plannification."),
    }

    def fields_view_get(self, cr, uid, *args, **kwargs):
        res = super(mrp_production, self).fields_view_get(cr, uid, *args, **kwargs)
        if not self.pool.get('res.groups').user_has_groups(cr, uid, 'mrp.group_mrp_manager'):
            try:
                routing_field = res['fields']['routing_id']
            except KeyError:
                _logger.warn("`routing_id` not found in view fields, cannot enforce read-only")
            else:
                # Non-managers see the default read-only state
                routing_field["states"] = {'draft': [('readonly', False)]}
                res["fields"]["routing_id"] = routing_field

        return res
