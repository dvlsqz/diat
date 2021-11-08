from .usuarios import UserCreateView, UsersListView, UsersListJson, UserUpdateView, UserDeleteJsonView, UserDetailsView
from .servicios import ServiciosListView, ServiciosListJson, ServicioCreateView, ServicioUpdateView,\
    ServicioDeleteJsonView
from .jornadas import JornadasListView, JornadasListJson, JornadaCreateView, JornadaUpdateView, JornadaDeleteJsonView
from .dietas import DietasListView, DietasListJson, DietaCreateView, DietaUpdateView, DietaDeleteJsonView, DietaGetView
from .solicitudes_dieta import SolicitudesDietaListView, SolicitudesDietasListJson, SolicitudDietaCreateView,\
    SolicitudDietaDetailsView, SolicitudDietaDeleteJsonView, SolicitudesDietasServidasListView,\
    SolicitudDietaServidaJsonView, SolicitudDietaTotalDietasJsonView,\
    SolicitudDietaExcelView, SolicitudesDietasEncargadoListView
from .detalles_solicitudes_dietas import *
from .informes import *
from .solicitudes_dietas_tiempo_establecido import *
