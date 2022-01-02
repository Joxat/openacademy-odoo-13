from odoo import fields, models, api

class Resconfig(models.TransientModel):
    _inherit = 'res.config.settings'

    seats_default = fields.Integer('Allowed Seats')
    duration_default = fields.Float('Allowed duration')

    @api.model
    def set_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        ICP.set_param('openacademy.seats_default', self.seats_default)
        ICP.set_param('openacademy.duration_default', self.duration_default)
        super(Resconfig, self).set_values()

    @api.model
    def get_values(self):
        ICP = self.env['ir.config_parameter'].sudo()
        res = super(Resconfig, self).get_values()
        res['seats_default'] = int(ICP.get_param('openacademy.seats_default'))
        res['duration_default'] = float(ICP.get_param('openacademy.duration_default'))
        return res


