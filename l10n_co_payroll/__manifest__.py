# -*- coding: utf-8 -*-
{

    'name': "Nómina Colombiana",

    'summary': """
    Nómina Colombiana.""",

    'description': """ 
    Módulo que permite la generación de nómina de acuerdo a la normatividad Colombiana.
    """,

    'author': "servisoft latam",
    'website': "https://www.servisoftlatam.com",,
    
    'category': 'Invoicing & Payments',
    'version': '14.3.0.2.2',
    'license': 'OPL-1',
    'images': ['static/description/icon.jpg'],
    'depends': ['base','hr','hr_holidays','account','hr_payroll','hr_payroll_account','hr_contract'],
    'data': [
            # 'data/res_bank.xml',
            'views/res_partner_bank.xml',
            'data/res_groups.xml',
            'data/funcion_trozo.xml',
            'data/cron_asignar_vacaciones.xml',
            #'data/cron_enviar_correos.xml',
            'data/hr_work_entry_types.xml',
            'data/tipo_hora_extra.xml',
            'data/hr_payroll_new_entry.xml',
            'data/res_partner_management.xml',
            'security/ir.rule.csv',
            'security/ir.model.access.csv',
            'views/hr_employee.xml',
            'views/hr_config.xml',
            'views/res_company.xml',
            'views/hr_payroll_account.xml',
            'views/bancos_report.xml',
            'views/bancolombia_report.xml',
            'wizard/select_bancolombia_report_view.xml',
            'views/hr_contract.xml',
            'views/traza_variable.xml',
            'views/hr_salary_rule.xml',
            'data/hr_payslip_mail.xml',
            'views/ir_act_window.xml',
            'views/hr_payslip_input_type.xml',
            'views/hr_payroll_structure.xml',
            'views/res_partner_management_views.xml',
            'views/res_partner.xml',
            'views/pila_report.xml',
            'views/pila_summary_report.xml',
            # De nomina electronica.
            'data/electronic/cron_envio_a_dian.xml',
            'data/electronic/ir_sequence.xml',
            'data/electronic/ir_config_parameter.xml',
            'views/electronic/res_company.xml',
            'views/electronic/nomina_electronica.xml',
            # 'views/electronic/residuo_report.xml',
            'security/electronic/ir.model.access.csv',
            'security/electronic_document/ir.model.access.csv',
            'views/electronic_document/electronic_document.xml',
            # Retefuente
            'views/retefuente_table_view.xml',
            'data/cron_calcular_procentaje_retencion.xml',
            'data/retefuente_table.xml',
    ],
    'application': True,
}
