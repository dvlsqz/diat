import datetime
from io import BytesIO

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from reportlab.lib.pagesizes import LETTER, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from catalogos.forms import DietaForm, SolicitudesDietasForm
from catalogos.forms.informe import MatrizForm
from catalogos.models import Servicio, SolicitudDieta, Dieta, Jornada
from utils.MatrizSolicitudesDietasExport import MatrizSolicitudesDietasExport
from utils.PdfMixim import MyPrint, SolicitudesFechaPdf, PdfMixin, SolicitudEstadoPdfMixin


class SolicitudesDiariasJsonView(View):

    @staticmethod
    def post(request, *args, **kwargs):
        # Informes para solicitudes diarias

        data = SolicitudesDiariasJsonView.getDataReport()

        return JsonResponse({'result': 'OK', 'data': data})

    @staticmethod
    def getDataReport(params=None):

        if params is None or (params.__contains__('desde') is False and params.__contains__('hasta') is False):
            now_begin = datetime.datetime.now().replace(hour=0, minute=00)
            now_end = datetime.datetime.now().replace(hour=23, minute=59)
        else:
            now_begin = datetime.datetime.strptime(params.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
            now_end = datetime.datetime.strptime(params.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)

        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])


        # Filtrar solicitudes en rango de fechas
        if params is None or (params.__contains__('usuario') is False or params.__contains__('jornada') is False):
            pass
        else:
            user_id = params.get('usuario', 0)
            if (user_id is not '' and user_id is not '0') and str(user_id).__len__() > 0:
                dietas_diarias = dietas_diarias.filter(usuario_id=user_id)
            jornada_id = params.get('jornada', 0)
            if (jornada_id is not '' and jornada_id is not '0') and str(jornada_id).__len__() > 0:
                dietas_diarias = dietas_diarias.filter(jornada_id=jornada_id)

        solicitudes_dietas_dia = dietas_diarias.count()
        solicitudes_dietas_servicios = dietas_diarias.filter(servicio__isnull=False).count()
        solicitudes_diarias = [
            {
                'name': 'Servicios',
                'value': solicitudes_dietas_servicios
            },
        ]
        solicitudes_diarias_totales = [
            {
                'name': 'Solicitudes',
                'value': dietas_diarias.filter(servida=False).count()
            },
            {
                'name': 'Servidas',
                'value': dietas_diarias.filter(servida=True).count()
            }
        ]
        # Totales de solicitides de dietas por servicio
        servicios = Servicio.objects.all()
        servicios_totales = []
        for servicio in servicios:
            servicios_totales.append({
                'name': servicio.nombre,
                'value': dietas_diarias.filter(servicio_id=servicio.id).count()
            })
        # Totales de solicitudes de dietas por dieta
        dietas = Dieta.objects.all()
        dietas_totales = []
        for dieta in dietas:
            dietas_totales.append({
                'name': dieta.nombre,
                'value': dietas_diarias.filter(detalle_solicitud__dieta_id=dieta.id).count()
            })
        # Totales de Solicitudes de dietas por jornada
        jornadas = Jornada.objects.all()
        jornadas_totales = []
        for jornada in jornadas:
            jornadas_totales.append({
                'name': jornada.nombre,
                'value': dietas_diarias.filter(jornada_id=jornada.id).count()
            })
        data = {
            'solicitudes_dietas_dia': solicitudes_dietas_dia,
            'solicitudes_diarias': solicitudes_diarias,
            'solicitudes_diarias_totales': solicitudes_diarias_totales,
            'solicitudes_dietas_servicios': solicitudes_dietas_servicios,
            'servicios_totales': servicios_totales,
            'dietas_totales': dietas_totales,
            'jornadas_totales': jornadas_totales,
        }
        return data


class SolicitudesDietasInformesJsonView(TemplateView, View):
    template_name = 'informes/tipos_informes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create a form instance and populate it with data from the request (binding):
        form = SolicitudesDietasForm()
        context['form'] = form
        return context

    @staticmethod
    def post(request, *args, **kwargs):
        filtros = request.POST
        # Filtrar solicitudes en rango de fechas

        now_begin = datetime.datetime.strptime(filtros.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
        now_end = datetime.datetime.strptime(filtros.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)

        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        user_id = filtros.get('usuario', 0)
        if user_id is not '':
            dietas_diarias = dietas_diarias.filter(usuario_id=user_id)
        jornada_id = filtros.get('jornada', 0)
        if jornada_id is not '':
            dietas_diarias = dietas_diarias.filter(jornada_id=jornada_id)

        solicitudes_dietas_dia = dietas_diarias.count()
        solicitudes_dietas_servicios = dietas_diarias.filter(servicio__isnull=False).count()
        solicitudes_diarias = [
            {
                'name': 'Servicios',
                'value': solicitudes_dietas_servicios
            },
        ]

        solicitudes_diarias_totales = [
            {
                'name': 'Solicitudes',
                'value': dietas_diarias.filter(servida=False).count()
            },
            {
                'name': 'Servidas',
                'value': dietas_diarias.filter(servida=True).count()
            }
        ]

        # Totales de solicitides de dietas por servicio
        servicios = Servicio.objects.all()
        servicios_totales = []
        for servicio in servicios:
            servicios_totales.append({
                'name': servicio.nombre,
                'value': dietas_diarias.filter(servicio_id=servicio.id).count()
            })

        # Totales de solicitudes de dietas por dieta
        dietas = Dieta.objects.all()
        dietas_totales = []
        for dieta in dietas:
            dietas_totales.append({
                'name': dieta.nombre,
                'value': dietas_diarias.filter(detalle_solicitud__dieta_id=dieta.id).count()
            })

        # Totales de Solicitudes de dietas por jornada
        jornadas = Jornada.objects.all()
        jornadas_totales = []
        for jornada in jornadas:
            jornadas_totales.append({
                'name': jornada.nombre,
                'value': dietas_diarias.filter(jornada_id=jornada.id).count()
            })

        data = {
            'solicitudes_dietas_dia': solicitudes_dietas_dia,
            'solicitudes_diarias': solicitudes_diarias,
            'solicitudes_diarias_totales': solicitudes_diarias_totales,
            'solicitudes_dietas_servicios': solicitudes_dietas_servicios,
            'servicios_totales': servicios_totales,
            'dietas_totales': dietas_totales,
            'jornadas_totales': jornadas_totales,
        }

        return JsonResponse({'result': 'OK', 'data': data})


class SDInformesRangeJsonView(View):

    def get(request, *args, **kwargs):
        filtros = request.request.GET
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format('SolicitudDietaDesde')
        # inicializar array de bits en buffer
        buffer = BytesIO()

        reporte = SolicitudesFechaPdf('Solicitudes de Dietaa')
        reporte.init(buffer, 'A4')
        # response.create_header()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def create_header_objects(self, model_object, pdf, y):
        y = self.create_new_line("Fecha", pdf, 'Hello World', y)
        return y


class EstadoDietasPdfView(SolicitudEstadoPdfMixin, TemplateView, SolicitudesDiariasJsonView):
    data = None
    title = 'Estado de Dietas'
    margen = 30
    detail_len_units = 7
    detail_col_size = (letter[0] - margen * 2) / detail_len_units
    detail_widths = [detail_col_size * 2] + [detail_col_size * 2] + [detail_col_size] * 3

    def get_data(self):
        params = self.request.GET
        self.data = self.getDataReport(params)
        return self.data

    def create_body(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Dietas Solicitadas:")
        codigo = [Paragraph("Código", ParagraphStyle('cabecera'))]
        fecha = [Paragraph("Fecha", ParagraphStyle('cabecera'))]
        encargado = [Paragraph("Encargado", ParagraphStyle('cabecera'))]
        jornada = [Paragraph("Jornada", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[codigo, fecha, encargado, jornada]]

        detalles = []

        now_begin = datetime.datetime.now().replace(hour=0, minute=00)
        now_end = datetime.datetime.now().replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])

        for servida in dietas_diarias.filter(servida=False):
            detalle = {
                'codigo': servida.pk,
                'fecha': str(servida.created.strftime("%d/%m/%Y %H:%M:%S")),
                'encargado': str(servida.usuario),
                'jornada': servida.jornada,
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_body2(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Dietas Servidas:")
        codigo = [Paragraph("Código", ParagraphStyle('cabecera'))]
        fecha = [Paragraph("Fecha", ParagraphStyle('cabecera'))]
        encargado = [Paragraph("Encargado", ParagraphStyle('cabecera'))]
        jornada = [Paragraph("Jornada", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[codigo, fecha, encargado, jornada]]

        detalles = []

        now_begin = datetime.datetime.now().replace(hour=0, minute=00)
        now_end = datetime.datetime.now().replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        solicitudes_dietas_dia = dietas_diarias.count()
        solicitudes_dietas_servicios = dietas_diarias.filter(servicio__isnull=False).count()

        for servida in dietas_diarias.filter(servida=True):
            detalle = {
                'codigo': servida.pk,
                'fecha': str(servida.created.strftime("%d/%m/%Y %H:%M:%S")),
                'encargado': str(servida.usuario_sirvio),
                'jornada': servida.jornada,
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_table_summary(self):
        now_begin = datetime.datetime.now().replace(hour=0, minute=00)
        now_end = datetime.datetime.now().replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        solicitudes_dietas_dia = dietas_diarias.filter(servida=False).count()
        table = [
            ["Total de Dietas Solicitadas", solicitudes_dietas_dia],
        ]
        return table

    def create_table_summary2(self):
        now_begin = datetime.datetime.now().replace(hour=0, minute=00)
        now_end = datetime.datetime.now().replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        solicitudes_dietas_servicios = dietas_diarias.filter(servida=True).count()
        table = [
            ["Total de Dietas Servidas", solicitudes_dietas_servicios],
        ]
        return table

    def create_detail_content(self, detail):
        row = [self.get_table_cell(detail.get('codigo')),
               self.get_table_cell(detail.get('fecha')),
               self.get_table_cell(detail.get('encargado')),
               self.get_table_cell(detail.get('jornada')),
               ]
        return row


class SolicitudesJornadaPdfView(SolicitudEstadoPdfMixin, TemplateView, SolicitudesDiariasJsonView):
    data = None
    title = 'Solicitudes Por Jornada'
    margen = 30
    detail_len_units = 7
    detail_col_size = (letter[0] - margen * 2) / detail_len_units
    detail_widths = [detail_col_size * 2] + [detail_col_size * 2] + [detail_col_size] * 3

    def get_data(self):
        params = self.request.GET
        self.data = self.getDataReport(params)
        return self.data

    def create_body(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        jornada = [Paragraph("Jornada", ParagraphStyle('cabecera'))]
        total = [Paragraph("Total", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[jornada, total]]

        detalles = []

        for item in self.data.get('jornadas_totales'):
            detalle = {
                'jornada': item.get('name', 'NI'),
                'total': item.get('value', 0),
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_detail_content(self, detail):
        row = [self.get_table_cell(detail.get('jornada')),
               self.get_table_cell(detail.get('total')),
               ]
        return row

    def create_content(self, pdf, y):
        """function to override because create_body normally be different"""
        y = self.create_body(pdf, y)
        return y


class SolicitudesDietaPdfView(SolicitudEstadoPdfMixin, TemplateView, SolicitudesDiariasJsonView):
    data = None
    title = 'Solicitudes Por Dieta'
    margen = 30
    detail_len_units = 7
    detail_col_size = (letter[0] - margen * 2) / detail_len_units
    detail_widths = [detail_col_size * 2] + [detail_col_size * 2] + [detail_col_size] * 3

    def get_data(self):
        params = self.request.GET
        self.data = self.getDataReport(params)
        return self.data

    def create_body(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        dieta = [Paragraph("Dieta", ParagraphStyle('cabecera'))]
        total = [Paragraph("Total", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[dieta, total]]

        detalles = []

        for item in self.data.get('dietas_totales'):
            detalle = {
                'dieta': item.get('name', 'NI'),
                'total': item.get('value', 0),
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_detail_content(self, detail):
        row = [self.get_table_cell(detail.get('dieta')),
               self.get_table_cell(detail.get('total')),
               ]
        return row

    def create_content(self, pdf, y):
        """function to override because create_body normally be different"""
        y = self.create_body(pdf, y)
        return y


class SolicitudesServiciosPdfView(SolicitudEstadoPdfMixin, TemplateView, SolicitudesDiariasJsonView):
    data = None
    title = 'Solicitudes Por Servicio'
    margen = 30
    detail_len_units = 7
    detail_col_size = (letter[0] - margen * 2) / detail_len_units
    detail_widths = [detail_col_size * 2] + [detail_col_size * 2] + [detail_col_size] * 3

    def get_data(self):
        params = self.request.GET
        self.data = self.getDataReport(params)
        return self.data

    def create_body(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        servicio = [Paragraph("Servicio", ParagraphStyle('cabecera'))]
        total = [Paragraph("Total", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[servicio, total]]

        detalles = []

        for item in self.data.get('servicios_totales'):
            detalle = {
                'servicio': item.get('name', 'NI'),
                'total': item.get('value', 0),
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_detail_content(self, detail):
        row = [self.get_table_cell(detail.get('servicio')),
               self.get_table_cell(detail.get('total')),
               ]
        return row

    def create_content(self, pdf, y):
        """function to override because create_body normally be different"""
        y = self.create_body(pdf, y)
        return y


class EstadoDietasRangePdfView(EstadoDietasPdfView):

    def create_body(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Dietas Solicitadas:")
        codigo = [Paragraph("Código", ParagraphStyle('cabecera'))]
        fecha = [Paragraph("Fecha", ParagraphStyle('cabecera'))]
        encargado = [Paragraph("Encargado", ParagraphStyle('cabecera'))]
        jornada = [Paragraph("Jornada", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[codigo, fecha, encargado, jornada]]

        detalles = []

        now_begin = datetime.datetime.strptime(self.request.GET.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
        now_end = datetime.datetime.strptime(self.request.GET.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        user_id = self.request.GET.get('usuario', 0)
        if (user_id is not '' and user_id is not '0') and str(user_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(usuario_id=user_id)
        jornada_id = self.request.GET.get('jornada', 0)
        if (jornada_id is not '' and jornada_id is not '0') and str(jornada_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(jornada_id=jornada_id)


        for servida in dietas_diarias.filter(servida=False):
            detalle = {
                'codigo': servida.pk,
                'fecha': str(servida.created.strftime("%d/%m/%Y %H:%M:%S")),
                'encargado': str(servida.usuario),
                'jornada': servida.jornada,
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_body2(self, pdf, y):
        margen = self.margen
        pdf.setFont("Helvetica-Bold", 14)
        y = y - 35
        pdf.drawString(margen, y, "Dietas Servidas:")
        codigo = [Paragraph("Código", ParagraphStyle('cabecera'))]
        fecha = [Paragraph("Fecha", ParagraphStyle('cabecera'))]
        encargado = [Paragraph("Encargado", ParagraphStyle('cabecera'))]
        jornada = [Paragraph("Jornada", ParagraphStyle('cabecera'))]
        # create table for detail
        matrix = [[codigo, fecha, encargado, jornada]]

        detalles = []

        now_begin = datetime.datetime.strptime(self.request.GET.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
        now_end = datetime.datetime.strptime(self.request.GET.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        user_id = self.request.GET.get('usuario', 0)
        if (user_id is not '' and user_id is not '0') and str(user_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(usuario_id=user_id)
        jornada_id = self.request.GET.get('jornada', 0)
        if (jornada_id is not '' and jornada_id is not '0') and str(jornada_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(jornada_id=jornada_id)

        for servida in dietas_diarias.filter(servida=True):
            detalle = {
                'codigo': servida.pk,
                'fecha': str(servida.created.strftime("%d/%m/%Y %H:%M:%S")),
                'encargado': str(servida.usuario_sirvio),
                'jornada': servida.jornada,
            }
            detalles.append(detalle)

        y = self.create_detail(matrix, y, pdf, detalles)
        return y

    def create_table_summary(self):
        now_begin = datetime.datetime.strptime(self.request.GET.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
        now_end = datetime.datetime.strptime(self.request.GET.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        user_id = self.request.GET.get('usuario', 0)
        if (user_id is not '' and user_id is not '0') and str(user_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(usuario_id=user_id)
        jornada_id = self.request.GET.get('jornada', 0)
        if (jornada_id is not '' and jornada_id is not '0') and str(jornada_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(jornada_id=jornada_id)

        solicitudes_dietas_dia = dietas_diarias.filter(servida=False).count()
        table = [
            ["Total de Dietas Solicitadas", solicitudes_dietas_dia],
        ]
        return table

    def create_table_summary2(self):
        now_begin = datetime.datetime.strptime(self.request.GET.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
        now_end = datetime.datetime.strptime(self.request.GET.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)
        dietas_diarias = SolicitudDieta.objects.filter(created__range=[now_begin, now_end])
        user_id = self.request.GET.get('usuario', 0)
        if (user_id is not '' and user_id is not '0') and str(user_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(usuario_id=user_id)
        jornada_id = self.request.GET.get('jornada', 0)
        if (jornada_id is not '' and jornada_id is not '0') and str(jornada_id).__len__() > 0:
            dietas_diarias = dietas_diarias.filter(jornada_id=jornada_id)
        solicitudes_dietas_servicios = dietas_diarias.filter(servida=True).count()
        table = [
            ["Total de Dietas Servidas", solicitudes_dietas_servicios],
        ]
        return table


class SolicitudesJornadaRangePdfView(SolicitudesJornadaPdfView):
    pass


class MatrizView(TemplateView, View):
    template_name = 'informes/exportar_matriz.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create a form instance and populate it with data from the request (binding):
        form = MatrizForm()
        context['form'] = form
        return context


class MatrizExportView(View):
    def get(self, request, *args, **kwargs):
        filtros = request.GET
        report = MatrizSolicitudesDietasExport()
        return report.export(filtros)
