function save_payment() {
    var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
    var currency = $('#currency').val();
    var merchant_id = $('#merchant_id').val();
    var payment_types = $('#payment_types').val();
    var key1 = $('#key1').val();
    var key2 = $('#key2').val();

    if (currency == '') {
        $.growl.error({message: 'Currency is missing!'});
    } else if (merchant_id == '') {
        $.growl.error({message: 'Merchant ID is missing!'});
    } else if (payment_types == '') {
        $.growl.error({message: 'Payment types is missing!'});
    } else if (key1 == '') {
        $.growl.error({message: 'Key1 is missing!'});
    } else if (key2 == '') {
        $.growl.error({message: 'Key2 is missing!'});
    } else {
        $.ajax({
            url: base_url + '/admin/economy/payment-settings/',
            type: "POST",
            data: {
                currency: currency,
                merchant_id: merchant_id,
                payment_types: payment_types,
                key1: key1,
                key2: key2,
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


}

$('body').on('click', '#btn-save-payment', function (e) {
    save_payment();
});

$('body').on('click', '.btn-show-key', function (e) {
    $(this).closest('.input-group').find('input').attr('type', 'text');
});