let countDetalles = 0;
const $containerDetalles = $("#container-tablaDetalles");
let auxNombreDieta = false;
let auxNPO = false;
let auxViaje = false;

async function addDetalle() {
    const $dieta = $("#id_dieta");
    const $no_cama = $("#id_no_cama");
    const $especificar = $("#id_especificar");
    // Auxiliares de validación
    const auxCama = $no_cama.val() === '';
    const auxEspecificar = $especificar.val() === '';

    if ($dieta.select2('data')[0] && !auxCama || ((auxNombreDieta.toString().toLowerCase() === "otras" || auxNPO || auxViaje) && !auxEspecificar)) {
        const dieta = `<td data-value="${$dieta.val()}">${$dieta.select2('data')[0].text}</td>`;
        const no_cama = `<td data-value="${$no_cama.val()}">${$no_cama.val()}</td>`;
        const especificar = `<td data-value="${$especificar.val()}">${$especificar.val()}</td>`;
        const btnBorrar = `<td><button type="button" class="btn btn-danger btn-sm" onclick="removeDetalle('row_d_count_${countDetalles}', ${auxNPO})"><i class="tim-icons icon-trash-simple"></i></button></td>`;
        const row = `<tr id="row_d_count_${countDetalles}">${dieta}${no_cama}${especificar}${btnBorrar}</tr>`;
        $containerDetalles.append(row);
        // Limpiar form
        $dieta.val(null);
        $selectDieta.val(null).trigger('change');
        $no_cama.val(null);
        $especificar.val(null);
        $("#div_id_especificar").css("display", "none");
        $("#div_id_no_cama").css("display", "none");
        // Actualizar contador
        countDetalles += (auxNPO) ? 0 : 1;
        alertify.success(`Detalle agregado`, '10');
        $("#total_dietas").text(countDetalles);
    } else {
        alertify.error(`Datos no válidos`, '10');
    }
}

function removeDetalle(row, npo) {
    $containerDetalles.find($(`#${row}`)).remove();
    countDetalles -= (npo) ? 0 : 1; // Actualizar contador
    alertify.error(`Detalle removido`, '10');
    $("#total_dietas").text(countDetalles);
}

function templateConfirmacion() {
    let detalles = '';
    $('#container-tablaDetalles > tr').each(function () {
        if (($(this).find('td')[2]).innerText.length === 0) {
            detalles += `<p class="text-left">D: ${($(this).find('td')[0]).innerText + " C: " + ($(this).find('td')[1]).innerText}<p>`
        } else {
            detalles += `<p class="text-left">D: ${($(this).find('td')[0]).innerText + " O; " + ($(this).find('td')[2]).innerText}<p>`
        }
    });


    return `
            <p class="text-left">Jornada: ${$("#id_jornada").select2('data')[0].text}<p>
            <p class="text-left">Servicio: ${$("#id_servicio").select2('data')[0].text}<p>
            <hr>
            <p class="text-left text-muted">D: Dieta, C: No. de Cama, O: Observación</p>
            <p class="text-right">Total Solicitadas: ${countDetalles}<p>
            ${detalles}
            `;
}
