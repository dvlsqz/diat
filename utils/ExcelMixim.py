import io

import xlsxwriter
from django.http import HttpResponse


class ExcelMixim:
    def __init__(self):
        # Create an in-memory output file for the new workbook.
        self.output = io.BytesIO()
        # Even though the final file will be in memory the module uses temp
        # files during assembly for efficiency. To avoid this on servers that
        # don't allow temp files, for example the Google APP Engine, set the
        # 'in_memory' Workbook() constructor option as shown in the docs.
        self.workbook = xlsxwriter.Workbook(self.output, {'remove_timezone': True})
        self.worksheet = self.workbook.add_worksheet()

        # Configurations print.
        self.worksheet.set_portrait()
        self.worksheet.set_print_scale(100)
        # A4
        self.worksheet.set_paper(9)
        self.worksheet.set_margins(0.5, 0.5, 0.5, 0.5)

        # Add a format for the header cells.
        self.merge_format = self.workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })

        self.properties = {
            'border': 1,
            'font_size': 9,
            'text_wrap': True,
            'align': 'left',
            'valign': 'vcenter',
            'locked': True
        }

        self.cell_format = self.workbook.add_format(self.properties)

        self.properties.update({'align': 'center'})
        self.cell_format_center = self.workbook.add_format(self.properties)
        self.properties.update({'text_wrap': False, 'align': 'left'})
        self.cell_format_wrap_false = self.workbook.add_format(self.properties)
        self.properties.update({'font_color': 'red', 'align': 'center'})
        self.cell_format_red_font = self.workbook.add_format(self.properties)
        self.properties.update({'font_color': 'blue', 'align': 'center'})
        self.cell_format_blue_font = self.workbook.add_format(self.properties)
        self.properties.update({'font_color': 'green', 'align': 'center'})
        self.cell_format_green_font = self.workbook.add_format(self.properties)

        self.properties.update({'bg_color': 'gray', 'font_color': 'black'})
        self.cell_format_center_bg_gray = self.workbook.add_format(self.properties)
        self.properties.update({'font_color': 'blue', 'align': 'center'})
        self.cell_format_blue_font_bg_gray = self.workbook.add_format(self.properties)
        self.properties.update({'font_color': 'red', 'align': 'center'})
        self.cell_format_red_font_bg_gray = self.workbook.add_format(self.properties)
        self.properties.update({'font_color': 'green', 'align': 'center'})
        self.cell_format_green_font_bg_gray = self.workbook.add_format(self.properties)

        self.cell_format_date = self.workbook.add_format({
            'border': 1,
            'font_size': 10,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'locked': True,
            'num_format': 'dd/mm/yyyy'
        })

        self.cell_format_hour = self.workbook.add_format({
            'border': 1,
            'font_size': 10,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'locked': True,
            'num_format': ' hh:mm AM/PM'
        })

        # Turn worksheet protection on.
        self.worksheet.protect()

    def finish(self, filename):
        # Close the workbook before sending the data.
        self.workbook.close()

        # Rewind the buffer.
        self.output.seek(0)

        # Set up the Http response.
        response = HttpResponse(
            self.output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
