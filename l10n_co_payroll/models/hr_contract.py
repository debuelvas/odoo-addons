# -*- encoding: utf-8 -*-

from ast import Raise
from odoo import models, fields, api
from odoo.exceptions import UserError
from . import traza_atributo
from datetime import datetime,time
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'hr.contract'

    tipo_salario = fields.Selection(
        selection=[
            ('aprendiz Sena', 'Aprendiz Sena'),
            ('integral', 'Integral'),
            ('practicante', 'Practicante'),
            ('tradicional', 'Tradicional'),
            ('pasante', 'Pasante'),
        ],
        string='Tipo de Salario',
        required=True
    )
    salario_variable = fields.Boolean(string="Salario variable")

    area_trabajo = fields.Selection(
        selection=[
            ('administracion','Administración'),
            ('produccion', 'Producción'),
            ('ventas', 'Ventas'),
        ],
        string='Área de Trabajo',
        required=True
    )
    saldo_prima = fields.Float(string='Saldo prima', digits=(12,2))
    saldo_cesantias = fields.Float(string='Saldo cesantias', digits=(12,2))
    saldo_intereses_cesantias = fields.Float(string='Saldo intereses cesantias', digits=(12, 2))
    saldo_vacaciones = fields.Float(string='Saldo vacaciones', digits=(12, 2))

    # Variables Retencion en la fuente
    retencion_fuente = fields.Selection(
        selection=[
            ('procedimiento1', 'Procedimiento 1'),
            ('procedimiento2', 'Procedimiento 2'),
        ],
        string='Retención en la fuente',
        default='procedimiento1',
    )

    retefuente_table_value_ids = fields.Many2many(
        'retefuente.table',
        compute="_compute_retefuente_table_value_ids",
        help='Variable técnica para obtener el valor de la tabla de retencion en la fuente adecuado'
    )

    withholding_percentage_id = fields.Many2one(
        'historical.withholdings',
        string='Withholding tax percentage',
        help='Percentage used for the calculation of the withholding tax for the period',
        # Dominio evita que se muestren permisos porcentajes creados anteriormente
        domain=[('create_date', '=', False)],
    )

    ###########################
    #saldo_cesantias_anio_anterior = fields.Float(string='Saldo cesantias año anterior', digits=(12,2))
    #dias_saldo_suspensiones = fields.Float(string='Dias suspensiones saldo')
    #dias_saldo_suspensiones_anio_anterior = fields.Float(string='Dias suspensiones saldo - año anterior')

    fecha_corte = fields.Date(string="Fecha corte")

    traza_atributo_salario_ids = fields.One2many("traza.atributo","id_objeto",string="Ultimos salarios")
    #Campos para nomina electronica.
    periodo_de_nomina = fields.Selection(
        selection=[("1","Semanal"),
                   ("2","Decenal"),
                   ("3", "Catorcenal"),
                   ("4", "Quincenal"),
                   ("5", "Mensual")
                   ],
        string="Periodo de nomina",
        required=True
    )

    intervalo_calendario_ids = fields.One2many("intervalo.calendario","contract_id")

    credito_ids = fields.One2many("credito","contract_id",string="Creditos")
    new_entries_ids = fields.One2many('new.entry', 'contract_id', string='novedades del contrato')

    def _generate_work_entries(self, date_start, date_stop):
        not_work_entries_automatic = self.env['ir.config_parameter'].sudo().get_param('payroll.not_work_entries_automatic')
        if not_work_entries_automatic and not_work_entries_automatic=="True":
            print("no se generan entradas de trabajo...")
            return self.env['hr.work.entry']
        else:
            print("Se generan las entradas de trabajo....")
            #super(Contract, self)._generate_work_entries(date_start,date_stop)
            self._generate_work_entries_base(date_start, date_stop)

    def _generate_work_entries_base(self, date_start, date_stop):
        vals_list = []

        date_start = fields.Datetime.to_datetime(date_start)
        date_stop = datetime.combine(fields.Datetime.to_datetime(date_stop), time.max)

        date_start = date_start + relativedelta(hours=5)
        date_stop = date_stop + relativedelta(hours=5)

        for contract in self:
            # In case the date_generated_from == date_generated_to, move it to the date_start to
            # avoid trying to generate several months/years of history for old contracts for which
            # we've never generated the work entries.
            if contract.date_generated_from == contract.date_generated_to:
                contract.write({
                    'date_generated_from': date_start,
                    'date_generated_to': date_start,
                })
            # For each contract, we found each interval we must generate
            contract_start = fields.Datetime.to_datetime(contract.date_start)
            contract_stop = datetime.combine(fields.Datetime.to_datetime(contract.date_end or datetime.max.date()),
                                             datetime.max.time())
            last_generated_from = min(contract.date_generated_from, contract_stop)
            date_start_work_entries = max(date_start, contract_start)

            if last_generated_from > date_start_work_entries:
                contract.date_generated_from = date_start_work_entries
                vals_list.extend(contract._get_work_entries_values(date_start_work_entries, last_generated_from))

            last_generated_to = max(contract.date_generated_to, contract_start)
            date_stop_work_entries = min(date_stop, contract_stop)
            if last_generated_to < date_stop_work_entries:
                contract.date_generated_to = date_stop_work_entries
                vals_list.extend(contract._get_work_entries_values(last_generated_to, date_stop_work_entries))
        if not vals_list:
            return self.env['hr.work.entry']
        return self.env['hr.work.entry'].create(vals_list)

    def _compute_retefuente_table_value_ids(self):
        '''Toma los valores de la tabla de retencion en la fuente
        para ser usados en las reglas salariales.
        '''
        for contract in self:
            contract.retefuente_table_value_ids = self.env['retefuente.table'].search([])

            # Si el contrato tiene procedimiento 2, y no tiene porcentaje fijo asignado, se busca si hay un porcentaje creado para el periodo actual
            # y se asigna (Por algún motivo no esta asignado)
            if contract and contract.retencion_fuente == 'procedimiento2' and not contract.withholding_percentage_id:
                records = self.env['historical.withholdings'].search([('contract_id', '=', contract.id)])
                for record in records:
                    today = datetime.today().date()
                    if today >= record.period_from and today <= record.period_to:
                        contract.withholding_percentage_id = record

    def write(self, vals):
        # Asignar contrato al porcentaje fijo
        if self.retencion_fuente == 'procedimiento2' and self.withholding_percentage_id and not self.withholding_percentage_id.contract_id:
            self.withholding_percentage_id.contract_id = self.id
        # Si se elimina el porcentaje fijo del contrato, también se elimina el registro en la tabla de porcentajes
        if 'withholding_percentage_id' in vals and vals['withholding_percentage_id'] is False and self._origin.withholding_percentage_id.id:
            self.env['historical.withholdings'].search([('id', '=', self._origin.withholding_percentage_id.id)]).unlink()
        return super(Contract, self).write(vals)

    @api.model
    def create(self, vals_list):
        res = super(Contract, self).create(vals_list)
        # Asignar contrato al porcentaje fijo
        if res.retencion_fuente == 'procedimiento2' and res.withholding_percentage_id:
            res.withholding_percentage_id.contract_id = res.id
        return res

    @api.onchange('retencion_fuente')
    def _onchange_retencion_fuente(self):
        # Seleccionado procedimiento 1
        if self.retencion_fuente == 'procedimiento1':
            self.withholding_percentage_id = None

        # Seleccionado procedimiento 2
        if self.retencion_fuente == 'procedimiento2':
            self.withholding_percentage_id = None
            # Buscar si ya existe calculado un porcentaje fijo para el periodo actual, si lo hay se asigna
            records = self.env['historical.withholdings'].search([('contract_id', '=', self._origin.id)])

            for record in records:
                today = datetime.today().date()
                if record.period_from and record.period_to:
                    if today >= record.period_from and today <= record.period_to:
                        self.withholding_percentage_id = record

    @api.model
    def cron_calcular_porcentaje_retencion(self, day=False, month=False, year=False):
        # Se asigna el dia 10 de Enero y 10 de Julio como la fecha para realizar el calculo de porcentaje fijo
        if day and month and year:
            today = datetime.today().date().replace(month=month, day=day, year=year)
        else:
            today = datetime.today().date()
        _logger.info("Fecha calculo retencion: {}".format(today))
        if (today.month in (7, 1) and today.day == 10):
            # Buscar contratos que tengran procedimiento de retencion 2 y no tengan porcentaje fijo o este porcentaje ya no aplique para la fecha actual
            contracts = self.env['hr.contract'].search([
                ('employee_id', '!=', False),
                ('state', '=', 'open'),
                ('retencion_fuente', '=', 'procedimiento2'),
                '|', ('date_end', '>', today), ('date_end', '=', False),
                '|', ('withholding_percentage_id', '=', False), ('withholding_percentage_id.period_to', '<', today)
            ])

            # De cada contrato obtener las nominas del empleado de un año de anterioridad
            for contract in contracts:
                payslips = self.env['hr.payslip']
                # Debe tener una antigüedad de al menos 6 meses para poder calcular el porcentaje fijo
                if today.month == 1 and contract.date_start <= (today.replace(year=today.year - 1, month=7, day=1)):
                    payslips = self.env['hr.payslip'].search([
                        ('employee_id', '=', contract.employee_id.id),
                        ('date_to', '>=', today.replace(year=today.year - 1, day=1, month=1)),
                        ('date_to', '<', today.replace(day=1)),
                        ('state', '=', 'done')
                    ], order='date_to')

                if today.month == 7 and contract.date_start <= (today.replace(month=1, day=1)):
                    payslips = self.env['hr.payslip'].search([
                        ('employee_id', '=', contract.employee_id.id),
                        ('date_to', '>=', today.replace(year=today.year - 1, day=1, month=7)),
                        ('date_to', '<', today.replace(day=1)),
                        ('state', '=', 'done')
                    ], order='date_to')

                # Si numero de nominas es cero el contrato no tiene mas de 6 meses o no se han generado nomina
                if len(payslips) > 0:
                    base_gravable = 0
                    base_gravable_prima = 0
                    num_meses = 0
                    actual_month = None
                    for payslip in payslips:
                        for line in payslip.line_ids:
                            if line.code == 'BAS_GRA_RTF':
                                # Cuando la nomina es de la prima, se almacena aparte y luego se suma si se tiene al menos el año completo de antigüedad
                                if payslip.liquidar_por != 'prima':
                                    base_gravable += line.total
                                else:
                                    base_gravable_prima += line.total

                        # Para personas que no tiene una antigüedad de un año se toman los meses que lleve para el calculo del porcentaje fijo
                        if not actual_month:
                            actual_month = payslip.date_to
                            num_meses += 1
                        else:
                            # Las nominas se reciben en orden de fecha (date_to), por lo que si el mes cambia significa que se aumenta el numero de meses
                            if actual_month.month != payslip.date_to.month:
                                num_meses += 1
                                actual_month = payslip.date_to

                    # Se suma la prima
                    base_gravable += base_gravable_prima
                    # Si es 12 meses se suma uno mas que corresponde a la prima, si es menor solo se tiene en cuenta los meses
                    if num_meses == 12:
                        num_meses += 1

                    _logger.info("Numero meses: {}, base gravable: {}".format(num_meses, base_gravable))
                    # Promedio (redondeado al mil mas cercano)
                    base_gravable = round(base_gravable / num_meses, -3)
                    # Conversión base gravable a UVT
                    base_grabable_uvt = round(base_gravable / payslip.valor_uvt, 2)

                    # Calculo UVT en base a la tabla
                    valor_uvt_tabla = 0
                    for record in contract.retefuente_table_value_ids:
                        if base_grabable_uvt >= record.range_from and base_grabable_uvt < record.range_to:
                            valor_uvt_tabla = round(((base_grabable_uvt - record.range_from) * (record.marginal_rate / 100)) + record.uvt_added, 2)  # * payslip.valor_uvt

                    porcentaje_fijo_final = round(((valor_uvt_tabla * payslip.valor_uvt) / base_gravable) * 100, 2)

                    vals = {
                        'percentage_value': porcentaje_fijo_final
                    }

                    res = self.env['historical.withholdings'].create(vals)
                    # Asignación de datos al porcentaje
                    res.onchange_percentage_value(today)
                    res.contract_id = contract.id

                    contract.withholding_percentage_id = res
