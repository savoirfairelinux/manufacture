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

from openerp.osv import orm


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _get_move_chain_to_close(self, cr, uid, move):
        """ Returns a list of move ids starting after a move and ending
        before the close move or when the product or unit changes"""
        chain = []
        po = self.pool['procurement.order']
        next_move = move.move_dest_id
        while next_move:
            if any([
                   next_move.product_id != move.product_id,
                   next_move.product_uom != move.product_uom,
                   ]):
                # We can't handle product or unit changes
                break
            move_po = po.browse(cr, uid,
                                po.search(cr, uid,
                                          [('move_id', '=', next_move.id)]))
            if move_po and move_po[0].close_move:
                break
            else:
                chain.append(next_move.id)
                next_move = next_move.move_dest_id
        return chain
