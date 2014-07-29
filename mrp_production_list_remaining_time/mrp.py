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

    def _get_remaining_time(self, cr, uid, ids, field_name, arg, context):
        """ Gets the remaining production time of the product associated to
        this MO to produce """
        res = {}
        for prod in self.browse(cr, uid, ids):
            # We can probably assume that remaining time scales with remaining
            # quantity, with rem_time = (rem_qty / prod_qty) * tot_time
            res[prod.id] = (prod.remaining_qty / prod.product_qty) * prod.hour_total

        return res

    _columns = {
        'remaining_hour': fields.function(
            _get_remaining_time, method=True,
            store={
                "mrp.production": (
                    lambda self, cr, uid, ids, c={}: ids,
                    ['product_qty', 'remaining_qty', 'hour_total'],
                    10),
            }),
    }
