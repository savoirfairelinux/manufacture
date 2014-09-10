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
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class mrp_production(orm.Model):
    _inherit = 'mrp.production'

    def _action_compute_lines_routing(self, cr, uid, ids, properties=None,
                                      context=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """

        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')

        for production in self.browse(cr, uid, ids, context=context):
            #unlink product_lines
            prod_line_obj.unlink(cr, SUPERUSER_ID,
                                 [line.id for line in production.product_lines],
                                 context=context)

            #unlink workcenter_lines
            workcenter_line_obj.unlink(
                cr, SUPERUSER_ID,
                [line.id for line in production.workcenter_lines],
                context=context)

            # search BoM structure and route
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id,
                                           production.product_uom.id,
                                           properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id],
                               {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise orm.except_orm(_('Error!'),
                                     _("Cannot find a bill of material "
                                       "for this product."))

            # get components and workcenter_lines from BoM structure
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id,
                                          production.product_qty,
                                          bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point,
                                       factor / bom_point.product_qty,
                                       properties, routing_id=properties[0])
            # product_lines
            results = res[0]
            # workcenter_lines
            results2 = res[1]

            # reset product_lines in production order
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)

            #reset workcenter_lines in production order
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return results2

    def onchange_routing_id(self, cr, uid, ids, routing_id,
                            context=None):
        if context is None:
            context = {}
        final_result = self._action_compute_lines_routing(
            cr, uid, ids, [routing_id], context=context)
        return {'value': {'workcenter_lines': final_result, }}
