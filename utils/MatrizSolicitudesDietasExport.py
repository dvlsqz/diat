import datetime
import threading

from xlsxwriter.utility import xl_range, xl_rowcol_to_cell

from catalogos.models import SolicitudDieta, DetalleSolicitudDieta, Dieta, Servicio
import pytz

from utils.ExcelMixim import ExcelMixim

time_zone = pytz.timezone('America/Guatemala')


class MatrizSolicitudesDietasExport(threading.Thread, ExcelMixim):

    def __init__(self):
        ExcelMixim.__init__(self)

    def export(self, params):
        filename = 'Matriz%s.xlsx' % datetime.datetime.now().strftime('%d/%m/%Y')
        self.worksheet.name = 'MATRIZ'
        worksheet_npo_servicios = self.workbook.add_worksheet()
        worksheet_npo_servicios.name = 'NPO EN SERVICIOS'
        worksheet_dietas_viaje = self.workbook.add_worksheet()
        worksheet_dietas_viaje.name = 'DIETAS VIAJE'
        worksheet_tipo = self.workbook.add_worksheet()
        worksheet_tipo.name = 'TIPO'
        worksheet_servicio = self.workbook.add_worksheet()
        worksheet_servicio.name = 'SERVICIO'

        # region ids de registros estaticos de jornadas, dietas y servicios
        desayuno = 1
        almuerzo = 2
        cena = 3

        libre = 19
        libre_madres = 20
        npo = 24
        viaje = 23

        # filtrar las solicitudes de dietas en los rangos de fechas ingresadas.
        if params is None or (params.__contains__('desde') is False and params.__contains__('hasta') is False):
            now_begin = datetime.datetime.now().replace(hour=0, minute=00)
            now_end = datetime.datetime.now().replace(hour=23, minute=59)
        else:
            now_begin = datetime.datetime.strptime(params.get('desde'), '%d/%m/%Y').replace(hour=0, minute=00)
            now_end = datetime.datetime.strptime(params.get('hasta'), '%d/%m/%Y').replace(hour=23, minute=59)

        # Obtener registros de la bd
        dietas = Dieta.objects.all().order_by('pk')
        servicios = Servicio.objects.all().order_by('pk')
        registros = SolicitudDieta.objects.filter(created__range=[now_begin, now_end]).order_by('created__day')

        # region TITULO
        self.worksheet.set_row(0, 50)
        heading1 = 'INFORME SII-IGSS DIETAS POR  TIPO. SERVIDAS DURANTE EL PERIODO DEL \n %s al %s' %\
                   (now_begin.strftime('%d/%m/%Y'), now_end.strftime('%d/%m/%Y'))
        self.worksheet.merge_range(0, 0, 0, 3 * dietas.count() + 1, heading1, self.merge_format)
        # endregion

        # region Columnas de dietas y totales

        # Format the columns to make the text more visible.
        self.worksheet.set_column('A:A', 8)
        self.worksheet.set_column('B:B', 20)
        self.worksheet.set_default_row(22)

        self.worksheet.merge_range('A2:A3', 'DIA No.', self.cell_format_center)
        self.worksheet.merge_range('B2:B3', 'SERVICIO', self.cell_format_center)

        first_row = 1
        first_col = 2
        dieta_id_last = dietas.last().pk
        for dieta in dietas:
            last_col = first_col + 2
            self.worksheet.merge_range(first_row, first_col, first_row, last_col, dieta.nombre, self.cell_format_center)
            self.worksheet.set_column(first_row + 1, first_col, 3)
            self.worksheet.set_column(first_row + 1, first_col + 1, 3)
            self.worksheet.set_column(first_row + 1, first_col + 2, 3)
            self.worksheet.write(first_row + 1, first_col, 'D', self.cell_format_blue_font)
            self.worksheet.write(first_row + 1, first_col + 1, 'A', self.cell_format_red_font)
            self.worksheet.write(first_row + 1, first_col + 2, 'C', self.cell_format_green_font)
            first_col = first_col + 3

            if dieta.pk == dieta_id_last:
                # columna de Totales
                self.worksheet.merge_range(first_row, first_col + 1, first_row, last_col + 4, 'TOTAL',
                                           self.cell_format_center)
                self.worksheet.write(first_row + 1, first_col + 1, 'D', self.cell_format_blue_font)
                self.worksheet.write(first_row + 1, first_col + 2, 'A', self.cell_format_red_font)
                self.worksheet.write(first_row + 1, first_col + 3, 'C', self.cell_format_green_font)

                # columna de Totales de dietas especiales
                self.worksheet.merge_range(first_row, first_col + 5, first_row + 1, last_col + 6, 'Servicios',
                                           self.cell_format_center)
                self.worksheet.merge_range(first_row, first_col + 6, first_row, last_col + 9,
                                           'TOTAL DE DIETAS ESPECIALES', self.cell_format_center)
                self.worksheet.write(first_row + 1, first_col + 6, 'D', self.cell_format_blue_font)
                self.worksheet.write(first_row + 1, first_col + 7, 'A', self.cell_format_red_font)
                self.worksheet.write(first_row + 1, first_col + 8, 'C', self.cell_format_green_font)

        # endregion

        # region Agrupar por solicitudes por dia

        first_row = first_row + 2

        dias_array = []
        for item in registros:
            day_date = item.created.astimezone().day
            aux = True
            for dia in dias_array:
                if dia.get('dia', 0) is day_date:
                    dia['items'].append(item)
                    aux = False
                    break
            if aux:
                items = [item]
                dias_array.append({'dia': day_date, 'items': items})

        # endregion

        # region Escribir totales, subtotales de solicitudes por jornada en la columna de dieta y fila de servicio

        if dias_array.__len__() == 0:
            return MatrizSolicitudesDietasExport.finish(self, filename)

        last_dia = dias_array[dias_array.__len__() - 1].get('dia')
        total_tiempos = 0
        total_especiales = 0
        for dia in dias_array:
            aux = first_row
            for servicio in servicios:
                self.worksheet.write(first_row, 1, servicio.nombre, self.cell_format)
                first_col = 2
                total_d = 0
                total_a = 0
                total_c = 0

                for dieta in dietas:
                    solicitudes = dia.get('items')

                    subtotal_d = self.get_total_solicitudes_jornada(solicitudes, jornada_id=desayuno,
                                                                    servicio_id=servicio.id, dieta_id=dieta.id)

                    subtotal_a = self.get_total_solicitudes_jornada(solicitudes, jornada_id=almuerzo,
                                                                    servicio_id=servicio.id, dieta_id=dieta.id)

                    subtotal_c = self.get_total_solicitudes_jornada(solicitudes, jornada_id=cena,
                                                                    servicio_id=servicio.id, dieta_id=dieta.id)

                    if dieta.npo is False or dieta.viaje is False:
                        total_d = total_d + subtotal_d
                        total_a = total_a + subtotal_a
                        total_c = total_c + subtotal_c
                        total_tiempos = total_tiempos + subtotal_d + subtotal_a + subtotal_c

                    # Imprimir subtotales por jornada
                    self.worksheet.write_number(first_row, first_col, subtotal_d, self.cell_format_blue_font)
                    self.worksheet.write_number(first_row, first_col + 1, subtotal_a, self.cell_format_red_font)
                    self.worksheet.write_number(first_row, first_col + 2, subtotal_c, self.cell_format_green_font)
                    first_col = first_col + 3

                    if dieta.pk == dieta_id_last:
                        # Escribir Subtotales por fila
                        self.worksheet.write_number(first_row, first_col + 1, total_d, self.cell_format_blue_font)
                        self.worksheet.write_number(first_row, first_col + 2, total_a, self.cell_format_red_font)
                        self.worksheet.write_number(first_row, first_col + 3, total_c, self.cell_format_green_font)

                        # Escribir subtotales de dietas especiales
                        libres_d = self.get_total_solicitudes_jornada(
                            solicitudes, jornada_id=desayuno, servicio_id=servicio.id, dieta_id=libre) + \
                            self.get_total_solicitudes_jornada(solicitudes, jornada_id=desayuno,
                                                               servicio_id=servicio.id, dieta_id=libre_madres)
                        libres_a = self.get_total_solicitudes_jornada(
                            solicitudes, jornada_id=almuerzo, servicio_id=servicio.id, dieta_id=libre) + \
                            self.get_total_solicitudes_jornada(solicitudes, jornada_id=almuerzo,
                                                               servicio_id=servicio.id, dieta_id=libre_madres)

                        libres_c = self.get_total_solicitudes_jornada(
                            solicitudes, jornada_id=cena, servicio_id=servicio.id, dieta_id=libre) + \
                            self.get_total_solicitudes_jornada(solicitudes, jornada_id=cena,
                                                               servicio_id=servicio.id, dieta_id=libre_madres)

                        total_especiales = total_especiales + (total_d - libres_d) + (total_a - libres_a) + \
                                                              (total_c - libres_c)

                        cell = xl_rowcol_to_cell(first_row, first_col + 5)
                        self.worksheet.set_column('%s:%s' % (cell, cell), 20)
                        self.worksheet.write(first_row, first_col + 5, servicio.nombre, self.cell_format)
                        self.worksheet.write_number(first_row, first_col + 6, total_d - libres_d,
                                                    self.cell_format_blue_font)
                        self.worksheet.write_number(first_row, first_col + 7, total_a - libres_a,
                                                    self.cell_format_red_font)
                        self.worksheet.write_number(first_row, first_col + 8, total_c - libres_c,
                                                    self.cell_format_green_font)

                first_row = first_row + 1

            # Calcular Subtotales por columna
            first_col = 2
            total_dietas = dietas.count()
            self.worksheet.write(first_row, first_col - 1, "Subtotal", self.cell_format_center_bg_gray)
            for i in range(total_dietas + 2):
                cell_range = xl_range(aux, first_col, first_row-1, first_col)
                cell_range1 = xl_range(aux, first_col + 1, first_row-1, first_col + 1)
                cell_range2 = xl_range(aux, first_col + 2, first_row-1, first_col + 2)
                self.worksheet.write(first_row, first_col, '{=SUM(%s)}' % cell_range,
                                     self.cell_format_blue_font_bg_gray)
                self.worksheet.write(first_row, first_col + 1, '{=SUM(%s)}' % cell_range1,
                                     self.cell_format_red_font_bg_gray)
                self.worksheet.write(first_row, first_col + 2, '{=SUM(%s)}' % cell_range2,
                                     self.cell_format_green_font_bg_gray)

                first_col = first_col + 3

                if i == total_dietas - 1:
                    first_col = first_col + 1

                if i == total_dietas:
                    self.worksheet.write(first_row, first_col + 1, "Subtotal", self.cell_format_center_bg_gray)
                    first_col = first_col + 2

            self.worksheet.merge_range(aux, 0, first_row, 0, dia.get('dia'), self.cell_format_center)
            first_row = first_row + 1

            # Calcular Totales por columna
            total_servicios = servicios.count()
            if dia.get('dia', 0) == last_dia:
                first_col = 2
                self.worksheet.write(first_row, first_col - 1, "GRAN TOTAL", self.cell_format_center)
                for i in range(total_dietas + 2):
                    celdas_d = []
                    celdas_a = []
                    celdas_c = []
                    row_init = 3 + total_servicios
                    for j in range(dias_array.__len__()):
                        cell_d = xl_rowcol_to_cell(row_init, first_col)
                        cell_a = xl_rowcol_to_cell(row_init, first_col + 1)
                        cell_c = xl_rowcol_to_cell(row_init, first_col + 2)
                        celdas_d.append(cell_d)
                        celdas_a.append(cell_a)
                        celdas_c.append(cell_c)
                        row_init = row_init + total_servicios + 1

                    self.worksheet.write(first_row, first_col, '{=SUM(%s)}' % ','.join(celdas_d),
                                         self.cell_format_blue_font)
                    self.worksheet.write(first_row, first_col + 1, '{=SUM(%s)}' % ','.join(celdas_a),
                                         self.cell_format_red_font)
                    self.worksheet.write(first_row, first_col + 2, '{=SUM(%s)}' % ','.join(celdas_c),
                                         self.cell_format_green_font)
                    first_col = first_col + 3

                    if i == total_dietas - 1:
                        first_col = first_col + 1
                        # Agregar el total de tiempos
                        self.worksheet.merge_range(first_row + 1, first_col, first_row + 1, first_col + 2,
                                                   "Total de tiempos: %s" % total_tiempos, self.cell_format_center)

                    if i == total_dietas:
                        self.worksheet.write(first_row, first_col + 1, "GRAN TOTAL", self.cell_format)
                        # Agregar el total de dietas especiales
                        self.worksheet.merge_range(first_row + 1, first_col + 2, first_row + 1, first_col + 4,
                                                   "Total de dietas especiales: %s" % total_especiales,
                                                   self.cell_format_center)
                        first_col = first_col + 2
        # endregion

        # region TITULO NPO
        worksheet_npo_servicios.set_row(0, 50)
        heading1 = 'INFORME SII-IGSS DE DIETAS. PACIENTES CON NPO, PERIODO DEL \n %s al %s' %\
                   (now_begin.strftime('%d/%m/%Y'), now_end.strftime('%d/%m/%Y'))
        worksheet_npo_servicios.merge_range(0, 0, 0, 3 * servicios.count() + 1, heading1, self.merge_format)
        # endregion

        # region Columnas de servicios y totales NPO
        # Format the columns to make the text more visible.
        worksheet_npo_servicios.set_column('B:B', 8)
        worksheet_npo_servicios.set_default_row(22)

        worksheet_npo_servicios.merge_range('B2:B3', 'DIA No.', self.cell_format_center)

        first_row = 1
        first_col = 2
        servicio_id_last = servicios.last().pk
        for servicio in servicios:
            last_col = first_col + 2
            worksheet_npo_servicios.merge_range(first_row, first_col, first_row, last_col, servicio.nombre,
                                                self.cell_format_center)
            worksheet_npo_servicios.set_column(first_row + 1, first_col, 3)
            worksheet_npo_servicios.set_column(first_row + 1, first_col + 1, 3)
            worksheet_npo_servicios.set_column(first_row + 1, first_col + 2, 3)
            worksheet_npo_servicios.write(first_row + 1, first_col, 'D', self.cell_format_blue_font)
            worksheet_npo_servicios.write(first_row + 1, first_col + 1, 'A', self.cell_format_red_font)
            worksheet_npo_servicios.write(first_row + 1, first_col + 2, 'C', self.cell_format_green_font)
            first_col = first_col + 3

            if servicio.pk == servicio_id_last:
                # columna de Subtotal
                worksheet_npo_servicios.merge_range(first_row, first_col + 1, first_row, last_col + 4, 'TOTAL',
                                                    self.cell_format_center)
                worksheet_npo_servicios.write(first_row + 1, first_col + 1, 'D', self.cell_format_blue_font)
                worksheet_npo_servicios.write(first_row + 1, first_col + 2, 'A', self.cell_format_red_font)
                worksheet_npo_servicios.write(first_row + 1, first_col + 3, 'C', self.cell_format_green_font)

        # endregion

        # region Escribir totales, subtotales de solicitudes por jornada en dieta NPO

        total_tiempos = 0
        total_desayuno = 0
        total_almuerzo = 0
        total_cena = 0
        first_row = 3
        for dia in dias_array:
            first_col = 2
            total_d = 0
            total_a = 0
            total_c = 0
            for servicio in servicios:
                worksheet_npo_servicios.write(first_row, 1, dia.get('dia'), self.cell_format)

                solicitudes = dia.get('items')

                subtotal_d = self.get_total_solicitudes_jornada(solicitudes, jornada_id=desayuno,
                                                                servicio_id=servicio.id, dieta_id=npo)

                subtotal_a = self.get_total_solicitudes_jornada(solicitudes, jornada_id=almuerzo,
                                                                servicio_id=servicio.id, dieta_id=npo)

                subtotal_c = self.get_total_solicitudes_jornada(solicitudes, jornada_id=cena,
                                                                servicio_id=servicio.id, dieta_id=npo)

                total_d = total_d + subtotal_d
                total_a = total_a + subtotal_a
                total_c = total_c + subtotal_c
                total_desayuno = total_desayuno + subtotal_d
                total_almuerzo = total_almuerzo + subtotal_a
                total_cena = total_cena + subtotal_c
                total_tiempos = total_tiempos + subtotal_d + subtotal_a + subtotal_c

                # Imprimir subtotales por jornada
                worksheet_npo_servicios.write_number(first_row, first_col, subtotal_d, self.cell_format_blue_font)
                worksheet_npo_servicios.write_number(first_row, first_col + 1, subtotal_a, self.cell_format_red_font)
                worksheet_npo_servicios.write_number(first_row, first_col + 2, subtotal_c, self.cell_format_green_font)
                first_col = first_col + 3

                if servicio.pk == servicio_id_last:
                    # Escribir Subtotales por fila
                    worksheet_npo_servicios.write_number(first_row, first_col + 1, total_d, self.cell_format_blue_font)
                    worksheet_npo_servicios.write_number(first_row, first_col + 2, total_a, self.cell_format_red_font)
                    worksheet_npo_servicios.write_number(first_row, first_col + 3, total_c, self.cell_format_green_font)

            first_row = first_row + 1

        # Calcular Subtotales por columna
        aux = 3
        first_col = 2
        total_servicios = servicios.count()
        worksheet_npo_servicios.write(first_row, first_col - 1, "Total", self.cell_format_center_bg_gray)
        for i in range(total_servicios + 1):
            cell_range = xl_range(aux, first_col, first_row-1, first_col)
            cell_range1 = xl_range(aux, first_col + 1, first_row-1, first_col + 1)
            cell_range2 = xl_range(aux, first_col + 2, first_row-1, first_col + 2)
            worksheet_npo_servicios.write(first_row, first_col, '{=SUM(%s)}' % cell_range,
                                          self.cell_format_blue_font_bg_gray)
            worksheet_npo_servicios.write(first_row, first_col + 1, '{=SUM(%s)}' % cell_range1,
                                          self.cell_format_red_font_bg_gray)
            worksheet_npo_servicios.write(first_row, first_col + 2, '{=SUM(%s)}' % cell_range2,
                                          self.cell_format_green_font_bg_gray)

            first_col = first_col + 3

            if i == total_servicios - 1:
                first_col = first_col + 1

        # Imprimir TOTALES POR JORNADA DE NPO
        first_row = first_row + 2
        first_col = 0
        worksheet_npo_servicios.write(first_row, first_col, 'Total Desayuno', self.cell_format)
        worksheet_npo_servicios.write(first_row, first_col + 1, total_desayuno, self.cell_format_blue_font)
        worksheet_npo_servicios.write(first_row + 1, first_col, 'Total Almuerzo', self.cell_format)
        worksheet_npo_servicios.write(first_row + 1, first_col + 1, total_almuerzo, self.cell_format_red_font)
        worksheet_npo_servicios.write(first_row + 2, first_col, 'Total Cena', self.cell_format)
        worksheet_npo_servicios.write(first_row + 2, first_col + 1, total_cena, self.cell_format_green_font)
        worksheet_npo_servicios.write(first_row + 3, first_col, 'Gran Total', self.cell_format)
        worksheet_npo_servicios.write(first_row + 3, first_col + 1, total_tiempos, self.cell_format_center_bg_gray)
        # endregion

        # region TITULO DIETAS DE VIAJE
        worksheet_dietas_viaje.set_row(0, 50)
        heading1 = 'DIETAS DE VIAJE ENTREGADAS POR SERVICIO, PERIODO DEL \n %s al %s' %\
                   (now_begin.strftime('%d/%m/%Y'), now_end.strftime('%d/%m/%Y'))
        worksheet_dietas_viaje.merge_range(0, 0, 0, 3 * servicios.count() + 1, heading1, self.merge_format)
        # endregion

        # region Columnas de servicios y totales DIETAS DE VIAJE
        # Format the columns to make the text more visible.
        worksheet_dietas_viaje.set_column('B:B', 8)
        worksheet_dietas_viaje.set_default_row(22)

        worksheet_dietas_viaje.merge_range('B2:B3', 'DIA No.', self.cell_format_center)

        first_row = 1
        first_col = 2
        servicio_id_last = servicios.last().pk
        for servicio in servicios:
            last_col = first_col + 2
            worksheet_dietas_viaje.merge_range(first_row, first_col, first_row, last_col, servicio.nombre,
                                               self.cell_format_center)
            worksheet_dietas_viaje.set_column(first_row + 1, first_col, 3)
            worksheet_dietas_viaje.set_column(first_row + 1, first_col + 1, 3)
            worksheet_dietas_viaje.set_column(first_row + 1, first_col + 2, 3)
            worksheet_dietas_viaje.write(first_row + 1, first_col, 'D', self.cell_format_blue_font)
            worksheet_dietas_viaje.write(first_row + 1, first_col + 1, 'A', self.cell_format_red_font)
            worksheet_dietas_viaje.write(first_row + 1, first_col + 2, 'C', self.cell_format_green_font)
            first_col = first_col + 3

            if servicio.pk == servicio_id_last:
                # columna de Totales
                worksheet_dietas_viaje.merge_range(first_row, first_col + 1, first_row, last_col + 4, 'TOTAL',
                                                   self.cell_format_center)
                worksheet_dietas_viaje.write(first_row + 1, first_col + 1, 'D', self.cell_format_blue_font)
                worksheet_dietas_viaje.write(first_row + 1, first_col + 2, 'A', self.cell_format_red_font)
                worksheet_dietas_viaje.write(first_row + 1, first_col + 3, 'C', self.cell_format_green_font)

        # endregion

        # region Escribir totales, subtotales de solicitudes por jornada en DIETAS DE VIAJE

        total_tiempos = 0
        total_desayuno = 0
        total_almuerzo = 0
        total_cena = 0
        first_row = 3
        for dia in dias_array:
            first_col = 2
            total_d = 0
            total_a = 0
            total_c = 0
            for servicio in servicios:
                worksheet_dietas_viaje.write(first_row, 1, dia.get('dia'), self.cell_format)

                solicitudes = dia.get('items')

                subtotal_d = self.get_total_solicitudes_jornada(solicitudes, jornada_id=desayuno,
                                                                servicio_id=servicio.id, dieta_id=viaje)

                subtotal_a = self.get_total_solicitudes_jornada(solicitudes, jornada_id=almuerzo,
                                                                servicio_id=servicio.id, dieta_id=viaje)

                subtotal_c = self.get_total_solicitudes_jornada(solicitudes, jornada_id=cena,
                                                                servicio_id=servicio.id, dieta_id=viaje)

                total_d = total_d + subtotal_d
                total_a = total_a + subtotal_a
                total_c = total_c + subtotal_c
                total_desayuno = total_desayuno + subtotal_d
                total_almuerzo = total_almuerzo + subtotal_a
                total_cena = total_cena + subtotal_c
                total_tiempos = total_tiempos + subtotal_d + subtotal_a + subtotal_c

                # Imprimir subtotales por jornada
                worksheet_dietas_viaje.write_number(first_row, first_col, subtotal_d, self.cell_format_blue_font)
                worksheet_dietas_viaje.write_number(first_row, first_col + 1, subtotal_a, self.cell_format_red_font)
                worksheet_dietas_viaje.write_number(first_row, first_col + 2, subtotal_c, self.cell_format_green_font)
                first_col = first_col + 3

                if servicio.pk == servicio_id_last:
                    # Escribir Subtotales por fila
                    worksheet_dietas_viaje.write_number(first_row, first_col + 1, total_d, self.cell_format_blue_font)
                    worksheet_dietas_viaje.write_number(first_row, first_col + 2, total_a, self.cell_format_red_font)
                    worksheet_dietas_viaje.write_number(first_row, first_col + 3, total_c, self.cell_format_green_font)

            first_row = first_row + 1

        # Calcular Subtotales por columna
        aux = 3
        first_col = 2
        total_servicios = servicios.count()
        worksheet_dietas_viaje.write(first_row, first_col - 1, "Total", self.cell_format_center_bg_gray)
        for i in range(total_servicios + 1):
            cell_range = xl_range(aux, first_col, first_row-1, first_col)
            cell_range1 = xl_range(aux, first_col + 1, first_row-1, first_col + 1)
            cell_range2 = xl_range(aux, first_col + 2, first_row-1, first_col + 2)
            worksheet_dietas_viaje.write(first_row, first_col, '{=SUM(%s)}' % cell_range,
                                         self.cell_format_blue_font_bg_gray)
            worksheet_dietas_viaje.write(first_row, first_col + 1, '{=SUM(%s)}' % cell_range1,
                                         self.cell_format_red_font_bg_gray)
            worksheet_dietas_viaje.write(first_row, first_col + 2, '{=SUM(%s)}' % cell_range2,
                                         self.cell_format_green_font_bg_gray)

            first_col = first_col + 3

            if i == total_servicios - 1:
                first_col = first_col + 1

        # Imprimir TOTALES POR JORNADA DE NPO
        first_row = first_row + 2
        first_col = 0
        worksheet_dietas_viaje.write(first_row, first_col, 'Total Desayuno', self.cell_format)
        worksheet_dietas_viaje.write(first_row, first_col + 1, total_desayuno, self.cell_format_blue_font)
        worksheet_dietas_viaje.write(first_row + 1, first_col, 'Total Almuerzo', self.cell_format)
        worksheet_dietas_viaje.write(first_row + 1, first_col + 1, total_almuerzo, self.cell_format_red_font)
        worksheet_dietas_viaje.write(first_row + 2, first_col, 'Total Cena', self.cell_format)
        worksheet_dietas_viaje.write(first_row + 2, first_col + 1, total_cena, self.cell_format_green_font)
        worksheet_dietas_viaje.write(first_row + 3, first_col, 'Gran Total', self.cell_format)
        worksheet_dietas_viaje.write(first_row + 3, first_col + 1, total_tiempos, self.cell_format_center_bg_gray)
        # endregion

        # region TITULO TIPO
        worksheet_tipo.set_row(0, 50)
        heading1 = 'INFORME SII-IGSS  DIETAS POR  TIPO, PERIODO DEL \n %s al %s' %\
                   (now_begin.strftime('%d/%m/%Y'), now_end.strftime('%d/%m/%Y'))
        worksheet_tipo.merge_range(0, 0, 0, 3 * dietas.count() + 1, heading1, self.merge_format)
        # endregion

        # region Columnas de servicios y totales TIPO
        # Format the columns to make the text more visible.
        worksheet_tipo.set_column('B:B', 8)
        worksheet_tipo.set_default_row(22)

        worksheet_tipo.merge_range('B2:B3', 'DIA No.', self.cell_format_center)

        first_row = 1
        first_col = 2
        dieta_id_last = dietas.last().pk
        for dieta in dietas:
            last_col = first_col + 2
            worksheet_tipo.merge_range(first_row, first_col, first_row, last_col, dieta.nombre, self.cell_format_center)
            worksheet_tipo.set_column(first_row + 1, first_col, 3)
            worksheet_tipo.set_column(first_row + 1, first_col + 1, 3)
            worksheet_tipo.set_column(first_row + 1, first_col + 2, 3)
            worksheet_tipo.write(first_row + 1, first_col, 'D', self.cell_format_blue_font)
            worksheet_tipo.write(first_row + 1, first_col + 1, 'A', self.cell_format_red_font)
            worksheet_tipo.write(first_row + 1, first_col + 2, 'C', self.cell_format_green_font)
            first_col = first_col + 3

            if dieta.pk == dieta_id_last:
                # columna de Totales
                worksheet_tipo.merge_range(first_row, first_col + 1, first_row, last_col + 4, 'TOTAL',
                                                   self.cell_format_center)
                worksheet_tipo.write(first_row + 1, first_col + 1, 'D', self.cell_format_blue_font)
                worksheet_tipo.write(first_row + 1, first_col + 2, 'A', self.cell_format_red_font)
                worksheet_tipo.write(first_row + 1, first_col + 3, 'C', self.cell_format_green_font)

        # endregion

        # region Escribir totales, subtotales de solicitudes por jornada en TIPO

        total_tiempos = 0
        total_desayuno = 0
        total_almuerzo = 0
        total_cena = 0
        first_row = 3
        for dia in dias_array:
            first_col = 2
            total_d = 0
            total_a = 0
            total_c = 0
            for dieta in dietas:
                worksheet_tipo.write(first_row, 1, dia.get('dia'), self.cell_format)

                solicitudes = dia.get('items')

                subtotal_d = self.get_total_solicitudes_jornada(solicitudes, jornada_id=desayuno,
                                                                servicio_id=0, dieta_id=dieta.id)

                subtotal_a = self.get_total_solicitudes_jornada(solicitudes, jornada_id=almuerzo,
                                                                servicio_id=0, dieta_id=dieta.id)

                subtotal_c = self.get_total_solicitudes_jornada(solicitudes, jornada_id=cena,
                                                                servicio_id=0, dieta_id=dieta.id)

                total_d = total_d + subtotal_d
                total_a = total_a + subtotal_a
                total_c = total_c + subtotal_c
                total_desayuno = total_desayuno + subtotal_d
                total_almuerzo = total_almuerzo + subtotal_a
                total_cena = total_cena + subtotal_c
                total_tiempos = total_tiempos + subtotal_d + subtotal_a + subtotal_c

                # Imprimir subtotales por jornada
                worksheet_tipo.write_number(first_row, first_col, subtotal_d, self.cell_format_blue_font)
                worksheet_tipo.write_number(first_row, first_col + 1, subtotal_a, self.cell_format_red_font)
                worksheet_tipo.write_number(first_row, first_col + 2, subtotal_c, self.cell_format_green_font)
                first_col = first_col + 3

                if dieta.pk == dieta_id_last:
                    # Escribir Subtotales por fila
                    worksheet_tipo.write_number(first_row, first_col + 1, total_d, self.cell_format_blue_font)
                    worksheet_tipo.write_number(first_row, first_col + 2, total_a, self.cell_format_red_font)
                    worksheet_tipo.write_number(first_row, first_col + 3, total_c, self.cell_format_green_font)

            first_row = first_row + 1

        # Calcular Subtotales por columna
        aux = 3
        first_col = 2
        worksheet_tipo.write(first_row, first_col - 1, "Total", self.cell_format_center_bg_gray)
        for i in range(total_dietas + 1):
            cell_range = xl_range(aux, first_col, first_row-1, first_col)
            cell_range1 = xl_range(aux, first_col + 1, first_row-1, first_col + 1)
            cell_range2 = xl_range(aux, first_col + 2, first_row-1, first_col + 2)
            worksheet_tipo.write(first_row, first_col, '{=SUM(%s)}' % cell_range,
                                 self.cell_format_blue_font_bg_gray)
            worksheet_tipo.write(first_row, first_col + 1, '{=SUM(%s)}' % cell_range1,
                                 self.cell_format_red_font_bg_gray)
            worksheet_tipo.write(first_row, first_col + 2, '{=SUM(%s)}' % cell_range2,
                                 self.cell_format_green_font_bg_gray)

            first_col = first_col + 3

            if i == total_dietas - 1:
                first_col = first_col + 1

        # Imprimir TOTALES POR JORNADA DE TIPO
        first_row = first_row + 2
        first_col = 0
        worksheet_tipo.write(first_row, first_col, 'Total Desayuno', self.cell_format)
        worksheet_tipo.write(first_row, first_col + 1, total_desayuno, self.cell_format_blue_font)
        worksheet_tipo.write(first_row + 1, first_col, 'Total Almuerzo', self.cell_format)
        worksheet_tipo.write(first_row + 1, first_col + 1, total_almuerzo, self.cell_format_red_font)
        worksheet_tipo.write(first_row + 2, first_col, 'Total Cena', self.cell_format)
        worksheet_tipo.write(first_row + 2, first_col + 1, total_cena, self.cell_format_green_font)
        worksheet_tipo.write(first_row + 3, first_col, 'Gran Total', self.cell_format)
        worksheet_tipo.write(first_row + 3, first_col + 1, total_tiempos, self.cell_format_center_bg_gray)
        # endregion

        # region TITULO Servicios
        worksheet_servicio.set_row(0, 50)
        heading1 = 'INFORME SII-IGSS DE DIETAS POR SERVICIO, ENTREGADAS DURANTE EL PERIODO DEL \n %s al %s' %\
                   (now_begin.strftime('%d/%m/%Y'), now_end.strftime('%d/%m/%Y'))
        worksheet_servicio.merge_range(0, 0, 0, 3 * servicios.count() + 1, heading1, self.merge_format)
        # endregion

        # region Columnas de servicios y totales SERVICIOS
        # Format the columns to make the text more visible.
        worksheet_servicio.set_column('B:B', 8)
        worksheet_servicio.set_default_row(22)

        worksheet_servicio.merge_range('B2:B3', 'DIA No.', self.cell_format_center)

        first_row = 1
        first_col = 2
        servicio_id_last = servicios.last().pk
        for servicio in servicios:
            last_col = first_col + 2
            worksheet_servicio.merge_range(first_row, first_col, first_row, last_col, servicio.nombre,
                                           self.cell_format_center)
            worksheet_servicio.set_column(first_row + 1, first_col, 3)
            worksheet_servicio.set_column(first_row + 1, first_col + 1, 3)
            worksheet_servicio.set_column(first_row + 1, first_col + 2, 3)
            worksheet_servicio.write(first_row + 1, first_col, 'D', self.cell_format_blue_font)
            worksheet_servicio.write(first_row + 1, first_col + 1, 'A', self.cell_format_red_font)
            worksheet_servicio.write(first_row + 1, first_col + 2, 'C', self.cell_format_green_font)
            first_col = first_col + 3

            if servicio.pk == servicio_id_last:
                # columna de Totales
                worksheet_servicio.merge_range(first_row, first_col + 1, first_row, last_col + 4, 'TOTAL',
                                               self.cell_format_center)
                worksheet_servicio.write(first_row + 1, first_col + 1, 'D', self.cell_format_blue_font)
                worksheet_servicio.write(first_row + 1, first_col + 2, 'A', self.cell_format_red_font)
                worksheet_servicio.write(first_row + 1, first_col + 3, 'C', self.cell_format_green_font)

        # endregion

        # region Escribir totales, subtotales de solicitudes por jornada en DIETAS DE VIAJE

        total_tiempos = 0
        total_desayuno = 0
        total_almuerzo = 0
        total_cena = 0
        first_row = 3
        for dia in dias_array:
            first_col = 2
            total_d = 0
            total_a = 0
            total_c = 0
            for servicio in servicios:
                worksheet_servicio.write(first_row, 1, dia.get('dia'), self.cell_format)

                solicitudes = dia.get('items')

                subtotal_d = self.get_total_solicitudes_jornada(solicitudes, jornada_id=desayuno,
                                                                servicio_id=servicio.id, dieta_id=0)

                subtotal_a = self.get_total_solicitudes_jornada(solicitudes, jornada_id=almuerzo,
                                                                servicio_id=servicio.id, dieta_id=0)

                subtotal_c = self.get_total_solicitudes_jornada(solicitudes, jornada_id=cena,
                                                                servicio_id=servicio.id, dieta_id=0)

                total_d = total_d + subtotal_d
                total_a = total_a + subtotal_a
                total_c = total_c + subtotal_c
                total_desayuno = total_desayuno + subtotal_d
                total_almuerzo = total_almuerzo + subtotal_a
                total_cena = total_cena + subtotal_c
                total_tiempos = total_tiempos + subtotal_d + subtotal_a + subtotal_c

                # Imprimir subtotales por jornada
                worksheet_servicio.write_number(first_row, first_col, subtotal_d, self.cell_format_blue_font)
                worksheet_servicio.write_number(first_row, first_col + 1, subtotal_a, self.cell_format_red_font)
                worksheet_servicio.write_number(first_row, first_col + 2, subtotal_c, self.cell_format_green_font)
                first_col = first_col + 3

                if servicio.pk == servicio_id_last:
                    # Escribir Subtotales por fila
                    worksheet_servicio.write_number(first_row, first_col + 1, total_d, self.cell_format_blue_font)
                    worksheet_servicio.write_number(first_row, first_col + 2, total_a, self.cell_format_red_font)
                    worksheet_servicio.write_number(first_row, first_col + 3, total_c, self.cell_format_green_font)

            first_row = first_row + 1

        # Calcular Subtotales por columna
        aux = 3
        first_col = 2
        total_servicios = servicios.count()
        worksheet_servicio.write(first_row, first_col - 1, "Total", self.cell_format_center_bg_gray)
        for i in range(total_servicios + 1):
            cell_range = xl_range(aux, first_col, first_row-1, first_col)
            cell_range1 = xl_range(aux, first_col + 1, first_row-1, first_col + 1)
            cell_range2 = xl_range(aux, first_col + 2, first_row-1, first_col + 2)
            worksheet_servicio.write(first_row, first_col, '{=SUM(%s)}' % cell_range,
                                     self.cell_format_blue_font_bg_gray)
            worksheet_servicio.write(first_row, first_col + 1, '{=SUM(%s)}' % cell_range1,
                                     self.cell_format_red_font_bg_gray)
            worksheet_servicio.write(first_row, first_col + 2, '{=SUM(%s)}' % cell_range2,
                                     self.cell_format_green_font_bg_gray)

            first_col = first_col + 3

            if i == total_servicios - 1:
                first_col = first_col + 1

        # Imprimir TOTALES POR JORNADA DE NPO
        first_row = first_row + 2
        first_col = 0
        worksheet_servicio.write(first_row, first_col, 'Total Desayuno', self.cell_format)
        worksheet_servicio.write(first_row, first_col + 1, total_desayuno, self.cell_format_blue_font)
        worksheet_servicio.write(first_row + 1, first_col, 'Total Almuerzo', self.cell_format)
        worksheet_servicio.write(first_row + 1, first_col + 1, total_almuerzo, self.cell_format_red_font)
        worksheet_servicio.write(first_row + 2, first_col, 'Total Cena', self.cell_format)
        worksheet_servicio.write(first_row + 2, first_col + 1, total_cena, self.cell_format_green_font)
        worksheet_servicio.write(first_row + 3, first_col, 'Gran Total', self.cell_format)
        worksheet_servicio.write(first_row + 3, first_col + 1, total_tiempos, self.cell_format_center_bg_gray)
        # endregion

        return MatrizSolicitudesDietasExport.finish(self, filename)

    @staticmethod
    def get_total_solicitudes_jornada(solicitudes, jornada_id: int, servicio_id, dieta_id):
        if servicio_id is not 0:
            solicitudes_filtradas = list(filter(lambda solicitud: (solicitud.jornada_id == jornada_id
                                                                   and solicitud.servicio_id == servicio_id),
                                                solicitudes))
        else:
            solicitudes_filtradas = list(filter(lambda solicitud: (solicitud.jornada_id == jornada_id),
                                                solicitudes))

        subtotal = 0
        if dieta_id is not 0:
            if servicio_id is not 0:
                for d in solicitudes_filtradas:
                    subtotal = subtotal + DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=d.pk,
                                                                               dieta_id=dieta_id).count()
            else:
                for d in solicitudes_filtradas:
                    subtotal = subtotal + DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=d.pk,
                                                                               dieta_id=dieta_id,
                                                                               dieta__npo=False,
                                                                               dieta__viaje=False).count()
        else:
            for d in solicitudes_filtradas:
                subtotal = subtotal + DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=d.pk,
                                                                           dieta__npo=False,
                                                                           dieta__viaje=False).count()

        return subtotal
