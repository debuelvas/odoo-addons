from odoo import api,fields,models

class HolidaysAllocation(models.Model):
    """ Allocation Requests Access specifications: similar to leave requests """
    _inherit = "hr.leave.allocation"
    saldo = fields.Boolean(string="Es saldo",default=False)