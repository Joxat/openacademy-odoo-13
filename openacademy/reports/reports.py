from odoo import models, fields, api
from odoo.exceptions import UserError
import io
import base64

class ReportWarning(models.AbstractModel):
    _name = 'report.openacademy.report_session_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        # if not self.env.user.has_group('openaca'):
        #     raise UserError('you do not have access ')
        sessions = self.env['openacademy.session'].browse(docids)
        for session in sessions:
            if len(session.attendees) == 0:
                raise UserError('no attendees')
        return {
            'doc_ids': docids,
            'doc_model': 'openacademy.session',
            'docs': self.env['openacademy.session'].browse(docids)
        }


class ReportXlsx(models.AbstractModel):
    _name = 'report.openacademy.report_saleorder_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def header_of_xlsx_report(self, row, sheet, user, bold):
        user_name = user.name
        address = f"{user.street} {user.street2}"
        country = user.country_id.name
        # bold = workbook.add_format({'bold': True})
        if order.image_100:
            image_data = io.BytesIO(base64.b64decode(order.image_100))
            sheet.insert_image(row+1, 1, 'logo.png', {'image_data': image_data, 'x_scale': 0.03, 'y_scale': 0.03})
            sheet.write(row+2, 1, user_name, bold)
            sheet.write(row+3, 1, address, bold)
            sheet.write(row+4, 1, country, bold)



    def generate_xlsx_report(self, workbook, data, orders):
        for order in orders:
            row = 3
            col = 3
            sheet = workbook.add_worksheet('report')
            bold = workbook.add_format({'bold': True})
            format1 = workbook.add_format({'bold': True, 'align': 'center'})
            format2 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': '#fffbed'})
            format3 = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'center'})
            sheet.set_column('A:J', 15)
            user = order.user
            self.header_of_xlsx_report(row, sheet, user, bold)
            # sheet.merge_range(row, col, row, col+8, 'Session', format2)
            # if order.image_100:
            #     image_data = io.BytesIO(base64.b64decode(order.image_100))
            #     sheet.insert_image(row+2, col+10, 'logo.png', {'image_data': image_data, 'x_scale': 0.03, 'y_scale': 0.03})
            #     row += 3
            #     sheet.write(row, col, 'Name', bold)
            #     sheet.write(row+1, col, order.name)
            #     row += 1
            #     sheet.write(row, col, 'Duration', bold)
            #     sheet.write(row+1, col, order.duration, format3)
            #     row += 1
            #     sheet.write(row, col, 'Attendees No', bold)
            #     sheet.write(row+1, col, order.attendees_no, format1)
            #     row += 1
            #     sheet.write(row, col, 'Attendees No', bold)
            #     sheet.write(row+1, col, order.attendees_no, format1)
