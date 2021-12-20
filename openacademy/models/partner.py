from odoo import fields, models, api

class respartner(models.Model):
    _inherit = 'res.partner'

    #adding fields
    instructor = fields.Boolean(string='Instructor', default=False)
    session_ids = fields.Many2many('openacademy.session', string='Sessions')
