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

from datetime import datetime

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class mrp_production_run_line_extra(orm.Model):
    _name = 'mrp.production.run.line.extra'
    _description = 'Keep extra information about a production line'
    _columns = {
        "state": fields.selection(
            (("before", "Before"), ("after", "After")),
        ),
        "run_id": fields.many2one('mrp.production.run', 'Production run'),
        "move_id": fields.many2one('stock.move', 'Stock Move'),
        "prodlot_id": fields.many2one('stock.production.lot'),
        "move_state": fields.selection(
            [('draft', 'New'),
             ('cancel', 'Cancelled'),
             ('waiting', 'Waiting Another Move'),
             ('confirmed', 'Waiting Availability'),
             ('assigned', 'Available'),
             ('done', 'Done'),
             ],
            'Status'),
    }

    def write_for_stock_move(self, cr, uid, move_id, state):
        move = self.pool["stock.move"].browse(cr, uid, move_id)
        return {
            "state": state,
            "move_id": move.id,
            "prodlot_id": move.prodlot_id and move.prodlot_id.id,
            "move_state": move.state,
        }

    def get_undo_write(self, cr, uid, run_id, move_id, state="before",
                       context=None):
        res = {}
        undo_lines = self.search(cr, uid, [
            ('run_id', '=', run_id),
            ('move_id', '=', move_id),
            ('state', '=', state),
        ], context=context)

        if undo_lines:
            undo = self.browse(cr, uid, undo_lines[0], context=context)
            res["prodlot_id"] = undo.prodlot_id and undo.prodlot_id.id
            res["state"] = undo.move_state

        return res


class mrp_production_run(orm.Model):
    _name = 'mrp.production.run'
    _description = 'Production Run'
    _order = 'date_produced'
    _columns = {
        "production_id": fields.many2one('mrp.production', 'Production'),
        "production_qty": fields.integer("Production Quantity"),
        "src_consumed_lines": fields.many2many(
            'stock.move',
            'mrp_production_run_src_consumed_lines',
            'production_id',
            'move_id',
            'Source To Consume Moves'),
        "consumed_lines": fields.many2many(
            'stock.move',
            'mrp_production_run_consumed_lines',
            'production_id',
            'move_id',
            'Consumed Moves'),
        "src_produced_lines": fields.many2many(
            'stock.move',
            'mrp_production_run_src_produced_lines',
            'production_id',
            'move_id',
            'Source To Produce Moves'),
        "produced_lines": fields.many2many(
            'stock.move',
            'mrp_production_run_produced_lines',
            'production_id',
            'move_id',
            'Produced Moves'),
        "date_produced": fields.datetime('Production Date', readonly=True),
        "line_extras": fields.one2many("mrp.production.run.line.extra",
                                       "run_id", "Extra Stock Move Info"),
    }

    _defaults = {
        'date_produced': lambda *a: datetime.utcnow().strftime(
            DEFAULT_SERVER_DATETIME_FORMAT),
    }


class mrp_production(orm.Model):
    _inherit = "mrp.production"

    def _has_production_runs(self, cr, uid, ids, f, arg, context):
        res = {}
        for this in self.browse(cr, uid, ids):
            res[this.id] = len(this.production_run_ids) > 0

        return res

    _columns = {
        'has_production_runs': fields.function(_has_production_runs,
                                               type="boolean", method=True),
        'production_run_ids': fields.one2many('mrp.production.run',
                                              'production_id',
                                              "Production runs"),
    }

    def action_produce(self, cr, uid, production_id, production_qty,
                       production_mode, context=None):
        m_extra = self.pool["mrp.production.run.line.extra"]
        write = {
            "production_qty": production_qty,
            "production_id": production_id,
        }
        prod = self.read(cr, uid, production_id, fields=[
            "move_lines",
            "move_created_ids",
            "move_lines2",
            "move_created_ids2",
        ], context=context)
        write["src_consumed_lines"] = [(6, 0, prod["move_lines"])]
        write["src_produced_lines"] = [(6, 0, prod["move_created_ids"])]

        # Keep all the info we don't want to guess later
        line_extras = [
            m_extra.write_for_stock_move(cr, uid, move_id, "before")
            for move_id in prod["move_lines"] + prod["move_created_ids"]
        ]

        produce_result = super(mrp_production, self).action_produce(
            cr, uid, production_id, production_qty, production_mode,
            context=context,
        )

        new_prod = self.read(cr, uid, production_id, fields=[
            "move_lines2",
            "move_created_ids2",
        ], context=context)

        write["consumed_lines"] = [(6, 0, [
            move_id for move_id in new_prod["move_lines2"]
            if move_id not in prod["move_lines2"]
        ])]
        write["produced_lines"] = [(6, 0, [
            move_id for move_id in new_prod["move_created_ids2"]
            if move_id not in prod["move_created_ids2"]
        ])]

        line_extras.extend(
            m_extra.write_for_stock_move(cr, uid, move_id, "after")
            for move_id in prod["move_lines2"] + prod["move_created_ids2"]
        )

        write["line_extras"] = [
            (0, 0, value)
            for value in line_extras
        ]

        self.pool["mrp.production.run"].create(cr, uid, write)
        return produce_result
