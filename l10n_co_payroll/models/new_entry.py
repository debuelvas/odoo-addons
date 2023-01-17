# -*- coding: utf-8 -*-

from odoo import fields, models


class NewEntry(models.Model):
    _name = "new.entry"
    _description = "Novedades en el contrato para otras entradas"

    contract_id = fields.Many2one('hr.contract')
    type_id = fields.Many2one('hr.payslip.input.type',string='Tipo de entrada',domain="[('appear_contract', '=', True)]")
    description = fields.Char(string='Descripción',help='Para sindicato se debe indicar el porcentaje, para los demás la descripción de la deducción o devengado ')
    value = fields.Float(string='Valor de la deducción o devengado')
    biweekly = fields.Boolean(string='Quincenal', help='Si la deducción o devemgado es quincenal el check debe quedar habilitado, si es mensual debe quedar deshabilitado')
    period = fields.Float(string='Número de periodos',help='Número de periodos a descontar el deducido o sumar el devengado')
    liquidated_periods= fields.Float(string='Periodos liquidados', readonly=True)
    vacations = fields.Boolean(string='Aplica en vacaciones', help='Si la deducción o el devengado se incluye aún si el empleado está en vacaciones debe quedar habilitado',default=True)
    absence_days = fields.Boolean(string='Aplica en días de ausencia',help='Este campo debe quedar habilitado si el monto en la nómina no cambia aunque el empleado tenga días de ausencia, en caso de quedar deshabilitado, el valor del deducido o devengado será calculado quitando los días de ausencia.',default=True)
    category = fields.Char(string='Categoría de la entrada',compute='_compute_category')
    liquidated = fields.Boolean(string='Liquidar en retiro',help='Habilitar si se requiere que cuando se finalice el contrato se debe liquidar el monto restante')
    definitive_periods = fields.Float(string='Periodos liquidados en la liquidación definitiva', readonly=True, default=0)
    partner_id = fields.Many2one('res.partner',string='Tercero')
    account_id = fields.Many2one('account.account',string='Cuenta')

    def _compute_category(self):
        for record in self:
            category = self.env['hr.salary.rule'].search([('name','=',record.type_id.name)], limit=1).category_id.name
            record.category = category

    def write(self,vals):
        if 'liquidated_periods' in vals and vals['liquidated_periods']<0:
            vals['liquidated_periods']=0
        return super(NewEntry, self).write(vals)