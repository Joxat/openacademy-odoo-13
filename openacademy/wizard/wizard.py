from odoo import fields, models, api, _


class wizard(models.TransientModel):
    _name = "openacademy.wizard"
    _description = "Transient Model"


    def _defualt_id(self):
        return self.env['openacademy.session'].browse(self._context.get('active_id')) #this just fills in the field in which it is specified to
    #fields

    session = fields.Many2many('openacademy.session', string='Responsible', required=True, default=_defualt_id)
    attendee = fields.Many2many('res.partner', string='Attendee', help="it helps defining attendees if they're missing !!")

    def subscribe(self):
        for i in self.session:
            i.attendees |= self.attendee  # this one means add this {...self.field} in react lol
        return {}


class Openacademy_pdf_report(models.TransientModel):
    _name = "openacademy.wizard.pdf"
    _description = "Transient Model for PDF report"

    #fields
    start_date = fields.Date(string='From')
    end_date = fields.Date(string='to')
    duration = fields.Float(string='duration', readonly="True")
    course = fields.Many2one('openacademy.course', string='Course')
    user = fields.Many2one('res.partner', string='Responsible')
    attendees = fields.Many2many('res.partner', string='Attendees')
    # attendees_no = fields.Integer(string="Attendees Number")

    # @api.depends('attendees')
    # def _get_attendee_no(self):
    #     for i in self:
    #         i.attendees_no = len(i.attendees)


    @api.onchange('start_date', 'end_date')
    def get_duration(self):
        for i in self:
            if not (i.start_date and i.end_date):
                continue
            i.duration = (i.end_date - i.start_date).days + 1

    def get_attendees(self):
        return len(self.attendees)

    def print_report(self):
        print('attendees are : ', self.attendees)
        domain = []
        start_date = self.start_date
        if start_date:
            domain += [('start_date', '>=', start_date)]
        end_date = self.end_date
        if end_date:
            domain += [('end_date', '<=', end_date)]
        course = self.course.ids
        if course:
            domain += [('course', '=', course)]
        user = self.user.id
        if user:
            domain += [('user', '=', user)]
        attendees = self.attendees
        if attendees:
            domain += [('attendees', '=', attendees)]
        # attendees_no = self.attendees_no
        # if attendees_no:
        #     domain += [('attendees_no', '=', attendees_no)]

        session = self.env['openacademy.session'].search_read(domain)
        data = {
            'form': self.read()[0],
            'session': session,

        }
        print(self.read()[0])
        return self.env.ref('openacademy.wizard_openacademy_report').report_action(self, data=data)
