function formAjaxSubmit(form, modal, edit = false) {
    $(form).submit(function (e) {
        e.preventDefault();
        // noinspection JSUnresolvedVariable
        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr) {
                if ($(xhr).find('.is-invalid').length < 1) {
                    // noinspection JSUnresolvedFunction
                    $table.DataTable().ajax.reload(null, false);
                    success_function(xhr);
                    $('#form-modal').modal('hide');
                    // noinspection JSUnresolvedVariable
                    alertify.notify(`${!edit ? 'Registro guardado.' : 'Registro actualizado.'}`,
                        `${!edit ? 'success' : 'notify'}`, 10);
                }

                $(modal).find('#form-modal-content').html(xhr);
                formAjaxSubmit(form, modal);
                loadModalDefaultComponents($(form));
            },
            error: (error) => alertify.notify(`Error al realizar la petición`, `error`, 10, () => console.log(error))
        });
    });
}

