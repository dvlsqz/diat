// region functions table


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function defaultConfig() {
    // noinspection JSUnresolvedVariable
    alertify.set('notifier','position', 'top-right');
}

$.fn.serializeFormJSON = function () {
    var o = {};
    var a = this.serializeArray();
    $.each(a, function () {
        if (o[this.name]) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};





function deleteDataTableItem(url, datatable) {
    swal({
        title: '¿Desea eliminar el registro?',
        text: "¡Esto no se puede revertir!",
        type: 'warning',
        showCancelButton: true,
        confirmButtonText: '¡Si, Eliminar!',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#d33',
        confirmButtonClass: 'btn btn-danger'
    }).then(function (result) {
        if (result.value) {
            $.ajax({
                url: url,
                method: 'POST',
                headers: {'X-CSRFToken': getCookie('csrftoken')},
                success: function (data) {
                    if (data.result === 'OK') {
                        success_function();
                        swal("¡Eliminado!", "Se ha eliminado el registro.", "success");
                        datatable.DataTable().ajax.reload(null, false);
                    } else {
                        swal("Error", "¡Ha ocurrido un error inesperado al intentar borrar el registro!", "error");
                    }
                },
                error: function (error) {
                    swal("Error", "", "error");
                    var message = '¡Ocurrio un error inesperado al intentar eliminar el registro!';
                    if (error.responseJSON) {
                        message = error.responseJSON.result;
                    }
                    swal("Error", message, "error");
                }
            });
        }
    });
}


// endregion


function loadComponents(parent) {
    $('input:visible:enabled:first', parent).focus();

    try {
        $('select.select2').select2({
            theme: 'bootstrap4',
            dropdownParent: parent,
            width: '100%'
        });
    } catch (e) {
        if (!(e instanceof TypeError)) {
            throw e;
        }
    }

    $('input.number').inputmask("numeric", {
        groupSeparator: ",",
        digits: 0,
        autoGroup: true,
        rightAlign: false,
        min: 0,
        removeMaskOnSubmit: true,
    });
}

function loadDefaultComponents() {
    loadComponents(null);
}

function loadModalDefaultComponents(parent) {
    loadComponents(parent);
}


/***
 * funcion para override
 * @param data
 */
function success_function(data) {

}



$('#add-button').click(function () {
    const url = $(this).data('url');
    $('#form-modal-content').load(url, function () {
        $('#form-modal').modal('show');
        formAjaxSubmit('#form-modal-content form', '#form-modal');
    });
});

$('#form-modal').on('shown.bs.modal', function () {
    loadModalDefaultComponents($(this));
});



let urlPDF = '';
function getPdf() {
    $.ajax({
        url: urlPDF,
        method: 'GET',
        headers: { 'X-CSRFToken': getCookie('csrftoken')},
        success: function() {
            $(location).attr('href',urlPDF);
        },
        error: function () {
            swal("Error", "Ocurrio un error inesperado al crear pdf", "error");
        }
    });
}