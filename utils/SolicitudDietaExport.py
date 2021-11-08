import threading


from catalogos.models import SolicitudDieta, DetalleSolicitudDieta
import pytz

from utils.ExcelMixim import ExcelMixim

time_zone = pytz.timezone('America/Guatemala')


def get_dietas_report():
    # Simulate a more complex table read.
    return [{'position': '5', 'name': 'Líquidos Claros', 'id': '1'},
            {'position': '6', 'name': 'Líquidos Completos', 'id': '2'},
            {'position': '7', 'name': 'Papilla', 'id': '3'},
            {'position': '8', 'name': 'Blanda', 'id': '4'},
            {'position': '9', 'name': 'Hipertroteica', 'id': '5'},
            {'position': '10', 'name': 'Hipoproteica', 'id': '6'},
            {'position': '11', 'name': 'Hipograsa', 'id': '7'},
            {'position': '12', 'name': 'Hiposódica', 'id': '8'},
            {'position': '13', 'name': 'Baja en purinas', 'id': '9'},
            {'position': '14', 'name': 'Diabético 1,200 Calorías', 'id': '10'},
            {'position': '15', 'name': 'Diabético 1,500 Calorías', 'id': '11'},
            {'position': '16', 'name': 'Diabético 1,800 Calorías', 'id': '12'},
            {'position': '17', 'name': 'Diabético 2,000 Calorías', 'id': '13'},
            {'position': '18', 'name': 'Diabético 2,200 Calorías', 'id': '14'},
            {'position': '19', 'name': 'PEDIATRÏA', 'id': '0'},
            {'position': '20', 'name': 'Menor de 6 meses', 'id': '15'},
            {'position': '21', 'name': 'De 6 a 9 meses (papilla)', 'id': '16'},
            {'position': '22', 'name': 'De 09 a 12 meses (picada)', 'id': '17'},
            {'position': '23', 'name': 'De 12 meses a 5 años (libre)', 'id': '18'},
            {'position': '24', 'name': 'Libre', 'id': '20', 'other_id': '19'},
            {'position': '25', 'name': 'Otras (Especificar)', 'id': '22', 'other_id': '23'},
            {'position': '26', 'name': 'Instructivo', 'id': '21'},
            {'position': '27'},
            {'position': '28'},
            {'position': '29', 'name': 'NPO', 'id': '24'},
            ]


class SolicitudDietaExcel(threading.Thread, ExcelMixim):

    def __init__(self):
        ExcelMixim.__init__(self)

    def export(self, solicitud_dieta: SolicitudDieta):

        self.worksheet.set_column('A:F', 8.5)
        self.worksheet.set_row(0, 50)
        heading1 = 'HOJA PARA SOLICITUD DE DIETAS DIARIAS HGQ'
        self.worksheet.merge_range('A1:G1', heading1, self.merge_format)

        # Format the columns to make the text more visible.
        self.worksheet.set_column('A:A', 5)
        self.worksheet.set_column('B:B', 12)
        self.worksheet.set_column('C:E', 8.5)
        self.worksheet.set_column('F:F', 17)
        self.worksheet.set_column('G:G', 8.5)
        self.worksheet.set_default_row(22)

        # make time zone aware
        utc_date_time = solicitud_dieta.created.astimezone()

        self.worksheet.write('A2', 'Fecha:', self.cell_format)
        self.worksheet.write('B2', utc_date_time, self.cell_format_date)
        self.worksheet.write('C2', 'Hora:', self.cell_format)
        self.worksheet.write('D2', utc_date_time, self.cell_format_hour)
        self.worksheet.write('E2', 'Servicio:', self.cell_format)
        self.worksheet.merge_range('F2:G2', solicitud_dieta.servicio.nombre, self.cell_format)

        self.worksheet.merge_range('A3:B3', 'Nombre de Encargado:', self.cell_format)
        full_name = '%s %s' % (solicitud_dieta.usuario.first_name, solicitud_dieta.usuario.last_name)
        self.worksheet.merge_range('C3:D3', full_name, self.cell_format_center)
        self.worksheet.merge_range('E3:G3', 'Firma y sello:', self.cell_format)

        self.worksheet.merge_range('A4:B4', None, self.cell_format)
        self.worksheet.merge_range('C4:F4', 'Número de cama.', self.cell_format)
        self.worksheet.write('G4', 'Total', self.cell_format)

        # Write dietas report
        detalles = []

        dietas_distintas = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=solicitud_dieta.pk) \
            .values('dieta_id').distinct()

        total_dietas_solicitadas = 0
        for dieta in dietas_distintas:
            data = DetalleSolicitudDieta.objects.filter(solicitud_dieta_id=solicitud_dieta.pk,
                                                        dieta_id=dieta.get('dieta_id'))
            values = []
            for value in data.values('no_cama', 'especificar'):
                if value.get('no_cama', None) is None:
                    values.append(value.get('especificar', ''))
                else:
                    values.append(value.get('no_cama', ''))

            detalle = {
                'id': str(data.first().dieta.pk),
                'dieta_nombre': data.first().dieta.nombre,
                'camas': str(values).replace("'", '').replace('[', '').replace(']', ''),
                'descripciones': str(values).replace('[', '').replace(']', ''),
                'total': data.filter(dieta__npo=False).count(),
            }
            detalles.append(detalle)
            total_dietas_solicitadas += data.exclude(dieta__npo=True).count()

        current_row = 30
        dietas_db = get_dietas_report()
        rows_writer = []
        rows_writer2 = []
        for d in dietas_db:
            for detalle in detalles:
                row_colum_dieta = 'A%s:B%s' % (d.get('position'), d.get('position'))
                row_colum_camas = 'C%s:F%s' % (d.get('position'), d.get('position'))
                if d.get('other_id', None) is not None and detalle.get('id', 0) == d.get('other_id', 0):
                    if rows_writer2.__contains__(d.get('id', 0)) is True:
                        continue
                    else:
                        rows_writer.append(d.get('id', 0))
                        pass
                elif rows_writer.__contains__(d.get('position', 0)) is True:
                    continue
                else:
                    rows_writer.append(d.get('position'))

                if d.get('id', '0') == detalle.get('id', '0'):
                    self.worksheet.merge_range(row_colum_dieta, d.get('name', None), self.cell_format)
                    self.worksheet.merge_range(row_colum_camas, detalle.get('camas', None), self.cell_format)
                    self.worksheet.write('G%s' % d.get('position'), detalle.get('total', None), self.cell_format_center)
                    if d.get('other_id', None) is None:
                        break
                elif d.get('other_id', '0') == detalle.get('id', '0'):
                    row_colum_dieta = 'A%s:B%s' % (current_row, current_row)
                    row_colum_camas = 'C%s:F%s' % (current_row, current_row)
                    self.worksheet.merge_range(row_colum_dieta, detalle.get('dieta_nombre', None), self.cell_format)
                    self.worksheet.merge_range(row_colum_camas, detalle.get('camas', None), self.cell_format)
                    self.worksheet.write('G%s' % current_row, detalle.get('total', None), self.cell_format_center)
                    current_row = current_row + 1
                    break
                else:
                    rows_writer.remove(d.get('position'))
                    self.worksheet.merge_range(row_colum_dieta, d.get('name', None), self.cell_format)
                    self.worksheet.merge_range(row_colum_camas, None, self.cell_format)
                    self.worksheet.write('G%s' % d.get('position'), None, self.cell_format_center)

        self.worksheet.set_row(current_row, 25)
        self.worksheet.merge_range('A%s:F%s' % (current_row, current_row), "TOTAL DE DIETAS SOLICITADAS",
                                   self.cell_format)
        self.worksheet.write('G%s' % current_row, total_dietas_solicitadas, self.cell_format_center)
        current_row = current_row + 1

        self.worksheet.set_row(current_row, 25)
        self.worksheet.merge_range('A%s:F%s' % (current_row, current_row), "TOTAL DIETAS SERVIDAS", self.cell_format)
        self.worksheet.write('G%s' % current_row, None, self.cell_format_center)
        current_row = current_row + 1

        self.worksheet.set_row(current_row, 25)
        self.worksheet.merge_range('A%s:B%s' % (current_row, current_row), "Nombre del Encargado:", self.cell_format)
        self.worksheet.merge_range('C%s:D%s' % (current_row, current_row), "____________________",
                                   self.cell_format_center)
        self.worksheet.write('E%s' % current_row, "Firma y sello:", self.cell_format_wrap_false)
        self.worksheet.merge_range('F%s:G%s' % (current_row, current_row), '____________________',
                                   self.cell_format_center)

        filename = 'SolicitudDieta%s.xlsx' % solicitud_dieta.pk
        return SolicitudDietaExcel.finish(self, filename)
