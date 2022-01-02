import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

class openacademy(models.Model):
    _name = 'openacademy.course'
    _description = 'Courses'

    name = fields.Char(placeholder='Name', required=True, copy=False, index=True)
    description = fields.Char(string="Description", help="Add your course description here")
    lol = fields.Char(string='ffs')
    responsible_id = fields.Many2one('res.user', ondelete='set null', string='Responsible', index=True)
    sessions = fields.Many2many('openacademy.session', string="Sessions")
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('completed', 'Completed'),
                              ('cancel', 'Cancel')], string="status", readonly=True, tracking=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name', 'lol') == 'lol':
            vals['name'] = self.env['ir.sequence'].next_by_code('openacademy.course.sequence')
        return super(openacademy, self).create(vals)

    def action_validate(self):
        for record in self:
            logger.info(f"Course{record.name} is in progress now by {self.env.user.name} ")
            record.write({'state': 'in_progress'})

    def action_complete(self):
        for record in self:
            record.write({'state': 'completed'})

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancel'})

    _sql_constraints = [
        ('name and description check',
         'check(name != lol)',
         'name and description should ont be the same'),

        ('Name uniqueness',
         'unique(name)',
         'Name must be unique')
    ]

    # def copy(self, default={}):
    #     copied_field = self.search(['name'])
    #     default['name'] = "copy(self.name)"
    #     return super(default, self).copy(default=default)

class sessions(models.Model):
    _name = 'openacademy.session'
    _description = 'Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # note that to add mail on the depends in the manifest file
    _rec_name = 'course'

    def duration_default(self):
        ICP = self.env['ir.config_parameter'].sudo()
        default_duration = ICP.get_param('openacademy.duration_default')
        return default_duration

    def seats_default(self):
        ICP = self.env['ir.config_parameter'].sudo()
        default_seats = ICP.get_param('openacademy.seats_default')
        return default_seats

    # fields in odoo
    name = fields.Char(placeholder='Name', required=True, copy=False)
    start_date = fields.Date(string="Start Date")
    duration = fields.Float(string='Duration', digits=(6, 2), help='Duration in days', default=duration_default)
    end_date = fields.Date(string='End Date', compute='_get_date', inverse='_get_date_inverse')
    seats = fields.Integer(string='Seats', default=seats_default)
    course = fields.Many2one('openacademy.course', ondelete='cascade', string='Course name', required=True)
    user = fields.Many2one('res.partner', ondelete='cascade', string='Responsible',
                           domain=[('country_id', '=', 'United States')])
    # countries = fields.Many2one('res.country', String="Country1")
    country_smh = fields.Many2one('res.country', related='user.country_id', string='Country')
    attendees = fields.Many2many('res.partner', string='Attendees')
    seat_percentage = fields.Float(digits=(2, 2), compute='_pos', string='Taken seats')
    lol = fields.Char(string='name for check')
    attendees_no = fields.Integer(string="Attendees Number", compute="_get_attendee_no", store="Ture")
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), ('completed', 'Completed'),
                              ('cancel', 'Cancel')], string="status", readonly=True, tracking=True, copy=False,
                             default='draft')
    email = fields.Boolean('sent emails', default=False)
    image_100 = fields.Image(string='Image')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            course = self._search([('name', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
            if not course:  # this says if not the value of this course in which the name=name then try another one
                course = self._search([('course', '=', name)])
                if not course:
                    course = self._search([('user', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        else:
            course = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(course)).with_user(name_get_uid)

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name}  {record.course}"
            result.append((record.id, name))
        return result

    def openacademy_session_ir_cron(self):
        session_ids = self.env['openacademy.session'].search([('email', '=', False)])
        for session in session_ids:
            if session.email is False:
                session.action_email()
                session.email = True

    def action_email(self):
        for attendee in self.attendees:
            ctx = {}
            email_list = [attendee.email]
            if email_list:
                ctx['email_to'] = ','.join([email for email in email_list if email])
                ctx['email_from'] = self.env.user.company_id.email
                ctx['send_email'] = True
                ctx['attendee'] = attendee.name
                template = self.env.ref('openacademy.email_template_openacademy_session')
                template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)

    @api.depends('attendees')
    def _get_attendee_no(self):
        for i in self:
            i.attendees_no = len(i.attendees)

    def get_attendee(self):
        return len(self.attendees)

    @api.depends('seats', 'attendees')
    def _pos(self):
        for i in self:
            if not i.seats:
                i.seat_percentage = 0
            if i.seats:
                i.seat_percentage = 100 * len(i.attendees) / i.seats

    @api.onchange('seats', 'attendees')
    def seats_validation(self):
        if self.seats < 0:
            return {
                'warning': {
                    'title': "The Seats value is not-valid",
                    'message': "Incorrect 'seats' value ",
                }
            }
        if self.seats < len(self.attendees):
            return {
                'warning': {
                    'message': "Please decrease the seats or rem ",
                    'title': "Too many attendees ",
                }
            }

    @api.constrains('user', 'attendees')
    def _check_ct(self):
        for i in self:
            if self.user in self.attendees:
                raise exceptions.ValidationError('you cannot have an instructor as an attendee! ')

    _sql_constraints = [
        ('name and description check',
         'check(name != lol)',
         'name and course should ont be the same'),

        ('Name uniqueness',
         'unique(name)',
         'Name must be unique'),

        ('duration should not be in miuns',
         'check(duration&lt;0)',
         'duration is in Minus'),

    ]

    def copy(self, default={}):
        return super(sessions, self).copy(default=default)
        default['name'] = "copy (" + self.name + ")"

    @api.depends('start_date', 'duration')
    def _get_date(self):
        for i in self:
            if not (i.start_date and i.duration):
                i.end_date = i.start_date
                continue
            duration = datetime.timedelta(days=i.duration, seconds=-1)
            i.end_date = i.start_date + duration

    @api.depends('start_date', 'end_date')
    def _get_date_inverse(self):
        for i in self:
            if not (i.start_date and i.end_date):
                continue
            i.duration = (i.end_date - i.start_date).days + 1

    def action_validate(self):
        for record in self:
            record.write({'state': 'in_progress'})

    def action_complete(self):
        for record in self:
            record.write({'state': 'completed'})

    def action_cancel(self):
        for record in self:
            record.write({'state': 'cancel'})

