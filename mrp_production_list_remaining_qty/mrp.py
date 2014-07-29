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

from openerp.osv import fields, orm


class mrp(orm.Model):
    _inherit = 'mrp.production'

    def _get_remaining_qty(self, cr, uid, ids, field_name, arg, context):
        """ Gets the remaining quantity of the product associated to this MO
        to produce """
        res = {}
        for prod in self.browse(cr, uid, ids):
            to_produce = prod.product_qty

            # action_produce sums all non-scrapped moves to get the sum of
            # produced items, then applies
            for produced_product in prod.move_created_ids2:
                if produced_product.scrapped:
                    continue

                if produced_product.product_id.id != prod.product_id.id:
                    continue

                to_produce = to_produce - produced_product.product_qty

            res[prod.id] = to_produce

        return res

    def _get_production_id(self, cr, uid, sm_ids, fields, context=None):
        return [
            move.production_id.id
            for move in self.pool.get("stock.move").browse(
                cr, uid, sm_ids, context=context)
            if move.production_id
        ]

    _columns = {
        'remaining_qty': fields.function(
            _get_remaining_qty, method=True,
            store=False),
    }
