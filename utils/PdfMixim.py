from io import BytesIO
from django.http import JsonResponse, HttpResponse
from reportlab.lib import colors, styles
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, TableStyle, Table

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from django.contrib.auth.models import User


class MyPrint:
    width: float
    height: float
    buffer: object
    pagesize: float

    def init(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
            self.width, self.height = self.pagesize

    def print_users(self):
        buffer = self.buffer

        doc = SimpleDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)

        # Our container for 'Flowable' objects
        elements = []

        # A large collection of style sheets pre-made for us
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='centered', alignment=TA_CENTER))

        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.
        users = User.objects.all()
        elements.append(Paragraph('My User Names', styles['Heading1']))
        for i, user in enumerate(users):
            elements.append(Paragraph(user.username, styles['Normal']))

        doc.build(elements)

        # Get the value of the BytesIO buffer and write it to the response.
        pdf = buffer.getvalue()
        buffer.close()
        return pdf


class PdfMixin:
    object = None
    title = None
    model = None
    detail_widths = None
    detail_col_size = None
    start_page = 730
    end_page = 60
    margen = 30
    resume_size = 200
    detail_len_units = None
    cell_style = ParagraphStyle('parrafos',
                                alignment=TA_LEFT,
                                fontSize=12,
                                fontName="Helvetica")
    table_style = TableStyle(
        [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
        ]
    )

    def create_new_line(self, label, pdf, value, y, **kwargs):
        """ create lines for header"""
        margen = self.margen
        new_line_size = 25
        pdf.setFont("Helvetica-Bold", 12)
        y -= new_line_size
        pdf.drawString(margen, y, label)
        pdf.setFont("Helvetica", 12)
        style = ParagraphStyle('parrafos', alignment=TA_JUSTIFY, fontSize=12, fontName="Helvetica")
        text = Paragraph(str(value or ""), style)
        # create margin to text for not overflow
        _, length = text.wrap(letter[0] - margen * 2 - 150 - kwargs.get('right_space', 0), y)
        if length > new_line_size:
            y -= length
        text.drawOn(pdf, margen + 200, y)
        return y

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        self.object = self.model.objects.get(id=kwargs.get('pk'))
        response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format('SolicitudDieta' + str(self.object.pk))
        # inicializar array de bits en buffer
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 14)

        # Se dibuja una cadena en el pdf
        y = self.create_header(self.object, pdf)
        y = self.create_content(pdf, y)
        y = self.create_footer(self.object, pdf)

        self.add_at_summary_left(pdf, y)
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def create_content(self, pdf, y):
        """function to override because create_body normally be different"""
        y = self.create_body(pdf, y)
        self.create_resume(pdf, y)
        return y

    def create_header(self, model_object, pdf):
        pdf.drawCentredString(letter[0] / 2, 760, f"{self.title}")
        y = self.start_page
        y = self.create_header_objects(model_object, pdf, y)
        return y

    def create_header_objects(self, model_object, pdf, y):
        """to override the text of header"""
        return y

    def create_footer(self, model_object, pdf):
        pdf.drawCentredString(letter[0] / 2, 760, f"{self.title}")
        y = self.end_page
        y = self.create_footer_objects(model_object, pdf, y)
        return y

    def create_header_objects(self, model_object, pdf, y):
        """to override the text of header"""
        return y

    def create_footer_objects(self, model_object, pdf, y):
        """to override the text of header"""
        return y

    def add_at_summary_left(self, pdf, y):
        """ function to override y is after detail positioned at left of
        summary be carefull of not overwrite summary """

    def print_detail(self, col_size, matrix, pdf, widths, y):
        """ matrix are the cells to paint"""
        detalle = Table(matrix, colWidths=widths)
        detalle.setStyle(self.table_style)
        _, table_length = detalle.wrapOn(pdf, col_size * 8 + 15, y)
        y -= table_length + 15
        detalle.drawOn(pdf, self.margen, y)
        return y

    def get_table_cell(self, value, currency=False):
        """ return value as paragraph and if currency is checked set $ """
        if currency:
            return [Paragraph('$ ' + str(value), self.cell_style)]
        return [Paragraph(str(value), self.cell_style)]

    def create_detail(self, matrix, y, pdf, detalles):
        detail_widths = self.detail_widths
        detail_col_size = self.detail_col_size
        header = matrix.copy()
        self.before_create_detail()

        for detalle_orden in detalles:
            row = self.create_detail_content(detalle_orden)
            matrix.append(row.copy())
            temp_table = Table(matrix, colWidths=detail_widths)
            temp_table.setStyle(self.table_style)
            _, table_length = temp_table.wrapOn(pdf, detail_col_size * self.detail_len_units + 15, letter[1] + 15)
            # si es necesario crear nueva pagina pintar y reiniciar tabla
            if table_length >= y - self.margen:
                last = matrix.pop()
                self.print_detail(detail_col_size, matrix, pdf, detail_widths, y)
                pdf.showPage()
                matrix = header
                matrix.append(row.copy())
                matrix.append(last)
                y = self.start_page
        y = self.print_detail(detail_col_size, matrix, pdf, detail_widths, y)
        return y

    def before_create_detail(self):
        """to overryde before detail cycle"""

    def create_body(self, pdf, y):
        """function to override, this is an example of how"""
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Detalle de Productos:")
        # create table for detail
        matrix = [[]]
        y = self.create_detail(matrix, y, pdf, [])
        return y

    def create_resume(self, pdf, y):
        """ create summary """
        margen = self.margen
        table = self.create_table_summary()
        detalle = Table(table)
        detalle.setStyle(self.table_style)
        _, table_length = detalle.wrapOn(pdf, self.resume_size, y)
        y -= table_length + 15
        if y <= margen:
            pdf.showPage()
            y = self.start_page - table_length
        detalle.drawOn(pdf, letter[0] - margen - self.resume_size, y)

    def create_table_summary(self):
        """override, you have to create the table summary here"""
        return []

    def create_detail_content(self, detalle_orden):
        """function to override, you have to set the content of rows detail"""
        return []


class SolicitudesFechaPdf:
    width: float
    height: float
    buffer: object
    pagesize: float
    start_page = 730
    title = ''
    doc = object

    def __init__(self, title):
        self.title = title

    def init(self, buffer, pagesize):
        self.buffer = buffer
        if pagesize == 'A4':
            self.pagesize = A4
        elif pagesize == 'Letter':
            self.pagesize = letter
            self.width, self.height = self.pagesize

        doc = SimpleDocTemplate(buffer,
                                rightMargin=72,
                                leftMargin=72,
                                topMargin=72,
                                bottomMargin=72,
                                pagesize=self.pagesize)


    def create_header(self, model_object, pdf):
        pdf.drawCentredString(letter[0] / 2, 760, f"{self.title} No. {model_object.pk}")
        y = self.start_page
        y = self.create_header_objects(model_object, pdf, y)
        return y

    def create_header_objects(self, model_object, pdf, y):
        """to override the text of header"""
        return y



class SolicitudEstadoPdfMixin:
    object = None
    title = None
    model = None
    detail_widths = None
    detail_col_size = None
    start_page = 730
    end_page = 60
    margen = 30
    resume_size = 200
    detail_len_units = None
    cell_style = ParagraphStyle('parrafos',
                                alignment=TA_LEFT,
                                fontSize=12,
                                fontName="Helvetica")
    table_style = TableStyle(
        [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT')
        ]
    )

    def create_new_line(self, label, pdf, value, y, **kwargs):
        """ create lines for header"""
        margen = self.margen
        new_line_size = 25
        pdf.setFont("Helvetica-Bold", 12)
        y -= new_line_size
        pdf.drawString(margen, y, label)
        pdf.setFont("Helvetica", 12)
        style = ParagraphStyle('parrafos', alignment=TA_JUSTIFY, fontSize=12, fontName="Helvetica")
        text = Paragraph(str(value or ""), style)
        # create margin to text for not overflow
        _, length = text.wrap(letter[0] - margen * 2 - 150 - kwargs.get('right_space', 0), y)
        if length > new_line_size:
            y -= length
        text.drawOn(pdf, margen + 200, y)
        return y

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        self.object = self.get_data()
        response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format('SolicitudDieta')
        # inicializar array de bits en buffer
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica-Bold", 14)

        # Se dibuja una cadena en el pdf
        y = self.create_header(self.object, pdf)
        y = self.create_content(pdf, y)

        self.add_at_summary_left(pdf, y)
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    @staticmethod
    def get_data():
        data = None
        return data

    def create_content(self, pdf, y):
        """function to override because create_body normally be different"""
        y = self.create_body(pdf, y)
        self.create_resume(pdf, y)
        y = self.create_body2(pdf, y)
        self.create_resume2(pdf, y)
        return y

    def create_header(self, model_object, pdf):
        pdf.drawCentredString(letter[0] / 2, 760, f"{self.title}")
        y = self.start_page
        y = self.create_header_objects(model_object, pdf, y)
        return y

    def create_header_objects(self, model_object, pdf, y):
        """to override the text of header"""
        return y


    def create_header_objects(self, model_object, pdf, y):
        """to override the text of header"""
        return y


    def add_at_summary_left(self, pdf, y):
        """ function to override y is after detail positioned at left of
        summary be carefull of not overwrite summary """

    def print_detail(self, col_size, matrix, pdf, widths, y):
        """ matrix are the cells to paint"""
        detalle = Table(matrix, colWidths=widths)
        detalle.setStyle(self.table_style)
        _, table_length = detalle.wrapOn(pdf, col_size * 8 + 15, y)
        y -= table_length + 15
        detalle.drawOn(pdf, self.margen, y)
        return y

    def get_table_cell(self, value, currency=False):
        """ return value as paragraph and if currency is checked set $ """
        if currency:
            return [Paragraph('$ ' + str(value), self.cell_style)]
        return [Paragraph(str(value), self.cell_style)]

    def create_detail(self, matrix, y, pdf, detalles):
        detail_widths = self.detail_widths
        detail_col_size = self.detail_col_size
        header = matrix.copy()
        self.before_create_detail()

        for detalle_orden in detalles:
            row = self.create_detail_content(detalle_orden)
            matrix.append(row.copy())
            temp_table = Table(matrix, colWidths=detail_widths)
            temp_table.setStyle(self.table_style)
            _, table_length = temp_table.wrapOn(pdf, detail_col_size * self.detail_len_units + 15, letter[1] + 15)
            # si es necesario crear nueva pagina pintar y reiniciar tabla
            if table_length >= y - self.margen:
                last = matrix.pop()
                self.print_detail(detail_col_size, matrix, pdf, detail_widths, y)
                pdf.showPage()
                matrix = header
                matrix.append(row.copy())
                matrix.append(last)
                y = self.start_page
        y = self.print_detail(detail_col_size, matrix, pdf, detail_widths, y)
        return y

    def before_create_detail(self):
        """to overryde before detail cycle"""

    def create_body(self, pdf, y):
        """function to override, this is an example of how"""
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Detalle de Productos:")
        # create table for detail
        matrix = [[]]
        y = self.create_detail(matrix, y, pdf, [])
        return y

    def create_body2(self, pdf, y):
        """function to override, this is an example of how"""
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Detalle de Productos:")
        # create table for detail
        matrix = [[]]
        y = self.create_detail(matrix, y, pdf, [])
        return y

    def create_resume(self, pdf, y):
        """ create summary """
        margen = self.margen
        table = self.create_table_summary()
        detalle = Table(table)
        detalle.setStyle(self.table_style)
        _, table_length = detalle.wrapOn(pdf, self.resume_size, y)
        y -= table_length + 15
        if y <= margen:
            pdf.showPage()
            y = self.start_page - table_length
        detalle.drawOn(pdf, letter[0] - margen - self.resume_size, y)

    def create_resume2(self, pdf, y):
        """ create summary """
        margen = self.margen
        table = self.create_table_summary2()
        detalle = Table(table)
        detalle.setStyle(self.table_style)
        _, table_length = detalle.wrapOn(pdf, self.resume_size, y)
        y -= table_length + 15
        if y <= margen:
            pdf.showPage()
            y = self.start_page - table_length
        detalle.drawOn(pdf, letter[0] - margen - self.resume_size, y)

    def create_table_summary(self):
        """override, you have to create the table summary here"""
        return []

    def create_table_summary2(self):
        """override, you have to create the table summary here"""
        return []

    def create_detail_content(self, detalle_orden):
        """function to override, you have to set the content of rows detail"""
        return []