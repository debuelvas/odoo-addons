from odoo import models,fields,api

class TrazaVariable(models.Model):
    _name="traza.variable"
    _description = "traza variable"

    fecha_desde = fields.Date(string="Facha inicio periodo",required=True)
    fecha_hasta = fields.Date(string="Facha fin periodo", required=True)

    smlv = fields.Integer(string = 'Salario mínimo mensual')
    smilv = fields.Integer(string = 'Salario mínimo integral mensual')
    aux_trans = fields.Integer(string = 'Auxilio de transporte')
    valor_uvt = fields.Integer(string = 'Valor UVT')
