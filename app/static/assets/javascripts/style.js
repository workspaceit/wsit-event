document.addEventListener('keydown', function (e) {
    if (e.keyCode == 83 && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        save_style();
        return false;
    }

});

function save_style() {
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var style = editor.getValue()
    $.ajax({
        url: base_url + '/admin/styles/',
        type: "POST",
        data: {
            style: style,
            base_url: base_url,
            csrfmiddlewaretoken: csrf_token
        },
        success: function (response) {
            if (response.success) {
                $.growl.notice({message: response.message});
                //setTimeout(function () {
                //    window.location = ''
                //}, 500);
            }
            else {
                $.growl.error({message: response.message});
            }
        }
    });
}

$('body').on('click', '#btn-save-style', function (e) {
    save_style();
});