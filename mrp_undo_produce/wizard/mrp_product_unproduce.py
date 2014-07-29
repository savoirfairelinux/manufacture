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

from datetime import datetime

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
from openerp.osv import orm, fields

DT_EPSILON_SECONDS = 10


def dates_similar(datestr1, datestr2):
    return DT_EPSILON_SECONDS >= abs((
        datetime.strptime(datestr1, DEFAULT_SERVER_DATETIME_FORMAT) -
        datetime.strptime(datestr2, DEFAULT_SERVER_DATETIME_FORMAT)
    ).total_seconds()),


class mrp_product_unproduce(orm.TransientModel):
    _name = "mrp.product.unproduce"
    _description = "Undo Produce"

    def _get_values_from_production(self, cr, uid, ids, fields, arg, context):
        res = {}
        for this in self.browse(cr, uid, ids, context=context):
            prod_run = this.production_run_id
            res[this.id] = {
                "consumed_lines": [sm.id for sm in prod_run.consumed_lines],
                "produced_lines": [sm.id for sm in prod_run.produced_lines],
            }
        return res

    _columns = {
        "production_run_id": fields.many2one('mrp.production.run', 'Production Run'),
        "consumed_lines": fields.function(
            _get_values_from_production,
            method=True,
            multi="production_run",
            type="many2many",
            obj="stock.move",
        ),
        "produced_lines": fields.function(
            _get_values_from_production,
            method=True,
            multi="production_run",
            type="many2many",
            obj="stock.move",
        ),
    }

    def default_get(self, cr, uid, fields=None, context=None):
        if not context or not context.get("active_id"):
            raise orm.except_orm(
                _("No active id"),
                _("Undo Produce must be called with an active production "
                  "in the context."))

        production = self.pool["mrp.production"].browse(cr, uid,
                                                        context["active_id"])
        if production.production_run_ids:
            prod_run = production.production_run_ids[-1]
            return {
                "production_run_id": prod_run.id,
                # When displaying the form for the first time, we'll need to
                # send those anyways even if they are calculated.
                "consumed_lines": [sm.id for sm in prod_run.consumed_lines],
                "produced_lines": [sm.id for sm in prod_run.produced_lines],
            }
        else:
            raise orm.except_orm(
                _("No production run"),
                _("Undo Produce must be called on a production that has been "
                  "started and has produced products. Productions done before"
                  " installing this module cannot be undone."))

    def _undo_next_splits(self, cr, uid, source_move, undo_move):
        """ Undo the splits following an original production split """

        source_move.refresh()

        m_sm = self.pool["stock.move"]
        source_chain = m_sm._get_move_chain_to_close(cr, uid, source_move)
        move_chain = m_sm._get_move_chain_to_close(cr, uid, undo_move)

        for source_id, move_id in zip(source_chain, move_chain):
            if source_id == move_id:
                break

            move = m_sm.browse(cr, uid, move_id)
            source = m_sm.browse(cr, uid, source_id)

            new_quantity = move.product_qty + source.product_qty
            source.write({"product_qty": new_quantity})
            m_sm.unlink(cr, uid, [move.id], {"call_unlink": True})

    def do_unproduce(self, cr, uid, ids, context=None):
        m_stock_move = self.pool["stock.move"]
        m_line_extra = self.pool["mrp.production.run.line.extra"]

        this = self.browse(cr, uid, ids[0], context=context)
        prod_run = this.production_run_id
        if any((
            len(prod_run.src_consumed_lines) != len(prod_run.consumed_lines),
            len(prod_run.src_produced_lines) != len(prod_run.produced_lines),
        )):
            raise orm.except_orm(
                _("Incorrect data"),
                _("Both of these lists pairs should be of the same length:\n"
                  "%r == %r\n%r == %r")
                % (
                    [m.id for m in prod_run.src_consumed_lines],
                    [m.id for m in prod_run.consumed_lines],
                    [m.id for m in prod_run.src_produced_lines],
                    [m.id for m in prod_run.produced_lines],
                )
            )

        def move_sort(move):
            return (
                move.product_id.id,
                move.product_uom.id,
                move.product_qty,
                move.id
            )

        scons = sorted(prod_run.src_consumed_lines, key=move_sort)
        cons = sorted(prod_run.consumed_lines, key=move_sort)
        sprod = sorted(prod_run.src_produced_lines, key=move_sort)
        prod = sorted(prod_run.produced_lines, key=move_sort)

        # Undo the moves
        for source_move, move in zip(scons + sprod, cons + prod):
            # Maybe we should assert some invariants about products, such as
            # quantity, unit and id
            before_write = m_line_extra.get_undo_write(cr, uid,
                                                       prod_run.id,
                                                       source_move.id,
                                                       "before",
                                                       context=context)

            if source_move.state == "done" and source_move.id == move.id:
                # This means the move was processed, we need to unprocess it
                move.write(before_write)
            elif source_move.state == "confirmed" and source_move.id != move.id:
                new_quantity = source_move.product_qty + move.product_qty
                before_write["product_qty"] = new_quantity
                source_move.write(before_write)
                self._undo_next_splits(cr, uid, source_move, move)
                m_stock_move.unlink(cr, uid, [move.id], {"call_unlink": True})
            else:
                raise orm.except_orm(
                    _("Internal Error"),
                    _("Unable to properly revert move\n"
                      "#{0.id} {0.product_qty} {0.product_id.name} {0.state}\n"
                      "\nfrom source move\n"
                      "#{1.id} {1.product_qty} {1.product_id.name} {1.state}"
                      ).format(move, source_move)
                )

        # If the production was now done, make it "in_production" again
        if prod_run.production_id.state == "done":
            prod_run.production_id.write({"state": "in_production"})

        # Finally, the production run should be removed
        prod_run.unlink()
