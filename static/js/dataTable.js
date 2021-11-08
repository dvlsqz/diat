let $table = $('#data-table');
let urlEditar, urlEliminar, urlDetalles = '';

function simpleBtns(data, linkEdit, btnDelete=true) {
    urlEditar = `${urlEditar.replace("0", data)}`;
    urlEliminar = `${urlEliminar.replace("0", data)}`;
    const btnEditar = (linkEdit) ? `<a class="edit-button btn btn-info btn-fab btn-icon btn-round btn-sm" title="Actualizar" href="${urlEditar}"><i class="tim-icons icon-pencil"></i></a>`
        : `<button class="edit-button btn btn-info btn-fab btn-icon btn-round btn-sm" title="Actualizar" data-url="${urlEditar}"><i class="tim-icons icon-pencil"></i></button>`;
    const btnEliminar = `<button class="delete-button btn btn-danger btn-fab btn-icon btn-round btn-sm" title="Eliminar" data-url="${urlEliminar}"><i class="tim-icons icon-trash-simple"></i></button>`;
    urlEditar = `${urlEditar.replace(data, "0")}`;
    urlEliminar = `${urlEliminar.replace(data, "0")}`;
    return `<div class="text-center">${btnEditar}${(btnDelete) ? btnEliminar: ""}</div>`;
}

function getDefaultDataTables(url, language_url, columns) {
    return {
        ajax: {
            url: url,
            type: 'post',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
        },
        language: {
            url: language_url
        },
        lengthMenu: [[10, 25, 50], [10, 25, 50]],
        searching: true,
        sDom: "<<'col-12 mt-2 pull-left'f>tr><'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
        processing: true,
        serverSide: true,
        responsive: true,
        order: [[ 0, "desc" ]],
        columns: columns
    };
}

function editBtn(data, linkEdit) {
    urlEditar = `${urlEditar.replace("0", data)}`;
    const btnEditar = (linkEdit) ? `<a class="edit-button btn btn-info btn-fab btn-icon btn-round btn-sm" title="Actualizar" href="${urlEditar}"><i class="tim-icons icon-pencil"></i></a>`
        : `<button class="edit-button btn btn-info btn-fab btn-icon btn-round btn-sm" title="Actualizar" data-url="${urlEditar}"><i class="tim-icons icon-pencil"></i></button>`;
    urlEditar = `${urlEditar.replace(data, "0")}`;
    return `${btnEditar}`;
}

function activoInactivoBtn(data) {
    const btnEliminar = `<button class="btn btn-outline-success btn-fab btn-icon btn-round btn-sm" title="Cambiar de estado" onclick="cambiarEstado(${data})"><i class="tim-icons icon-refresh-02"></i></button>`;
    return `${btnEliminar}`;
}

function deleteBtn(data) {
    urlEliminar = `${urlEliminar.replace("0", data)}`;
    const btnEliminar = `<button class="delete-button btn btn-danger btn-fab btn-icon btn-round btn-sm" title="Eliminar" data-url="${urlEliminar}"><i class="tim-icons icon-trash-simple"></i></button>`;
    urlEliminar = `${urlEliminar.replace(data, "0")}`;
    return `${btnEliminar}`;
}

function detailsBtn(data, linkEdit) {
    urlDetalles = `${urlDetalles.replace("0", data)}`;
    const btnDetalles = (linkEdit) ?  `<a class="btn btn-info btn-fab btn-icon btn-round btn-sm" title="Actualizar" href="${urlDetalles}"><i class="tim-icons icon-alert-circle-exc"></i></a>`
        : `<button class="details-button btn btn-success btn-fab btn-icon btn-round btn-sm" title="Detalles" data-url="${urlDetalles}"><i class="tim-icons icon-alert-circle-exc"></i></button>`;
    urlDetalles = `${urlDetalles.replace(data, "0")}`;
    return `${btnDetalles}`;
}

// region Eventos Botones DataTable
$table.on('click', '.delete-button', function () {
    const url = $(this).data('url');
    deleteDataTableItem(url, $table);
});

$table.on('click', '.edit-button', function () {
    const url = $(this).data('url');
    $('#form-modal-content').load(url, function () {
        $('#form-modal').modal('show');
        formAjaxSubmit('#form-modal-content form', '#form-modal', true);
    });
});

$table.on('click', '.details-button', function () {
    const url = $(this).data('url');
    $('#form-modal-content').load(url, function () {
        $('#form-modal').modal('show');
    });
});

// endregion
