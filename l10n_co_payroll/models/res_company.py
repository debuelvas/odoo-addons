# -*- encoding: utf-8 -*-


#PragmaTIC (om) 2015-07-03 actualiza para version 8
from odoo import models, fields, api


# Agrega campos Caja, ARL, ICBF, SENA, Salario mínimo, Salario mínimo integral, UVT  en datos del empleado.
#PragmaTIC (om) 2015-07-03 Agrega nivel de riesgo ARL, AFC, FPV, intereses de vivienda, medicina prepagada y dependientes

class ResCompany(models.Model):

    _inherit = 'res.company'
    ccf_id = fields.Many2one('res.partner', string = 'Caja de comp. familiar')
    arl_id = fields.Many2one('res.partner', string = 'ARL')
    icbf_id = fields.Many2one('res.partner', string = 'ICBF')
    sena_id = fields.Many2one('res.partner', string = 'SENA')
    dian_id = fields.Many2one('res.partner', string = 'DIAN')
    """smlv = fields.Integer(string = 'Salario mínimo mensual')
    smilv = fields.Integer(string = 'Salario mínimo integral mensual')
    aux_trans = fields.Integer(string = 'Auxilio de transporte')
    valor_uvt = fields.Integer(string = 'Valor UVT')"""
    ley_1607 = fields.Boolean(string = 'Acogido ley 1607/2012')
    aplicada = fields.Boolean(string='Aplicacion de Plantilla')
    pcts_incapacidades= fields.Many2one("funcion.trozo")