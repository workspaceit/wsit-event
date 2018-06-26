var question_language = '';
var option_language = '';
var session_language = '';
var location_language = '';
var travel_language = '';
var menu_language = '';
var manu_parent_items_language = '';
var default_language_id = '';

// $(function(){
//     $(".settings-groups-table tbody tr").each(function () {
//         var group_name_lang = $(this).find('td:nth-child(4) a').attr('data-lang');
//         var group_name = valueWithSpecialCharacter($(this).find('td:nth-child(4) a').html());
//         if(group_name_lang != '' || group_name_lang != undefined){
//             var data = getGroupContentByLanguage(group_name, group_name_lang, $('#settings_defualt_language_id').val())
//             $(this).find('td:nth-child(4) a').html(data);
//         }
//     });
//
// });

init.push(function () {
    // Question edit modal language select2 create and change event
    $(".question-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        if (question_language != '') {
            $('.editTitle').val(getcontentByLanguage(question_language.title, question_language.title_lang, language_id));
            $('#edit-description').val(getcontentByLanguage(question_language.description, question_language.description_lang, language_id));
        }
        if (option_language != '' && option_language.length != 0) {
            for (var i = 0; i < option_language.length; i++) {
                $("#options_table tbody").find('tr[data-id=' + option_language[i].id + ']').find('a.edit-button-label').editable('setValue', getcontentByLanguage(option_language[i].option, option_language[i].option_lang, language_id));
            }
        }
    });
    // Session edit modal language select2 create and change event
    $(".session-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        console.log(language_id);
        if (session_language != '') {
            $('#name').val(getcontentByLanguage(session_language.name, session_language.name_lang, language_id));
            if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
            }
            $('textarea#froala_content_editor').froalaEditor('html.set', getcontentByLanguage(session_language.description, session_language.description_lang, language_id));
        }
    });
    // Location edit modal language select2 create and change event
    $(".location-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        if (location_language != '') {
            $('#location_name').val(getcontentByLanguage(location_language.name, location_language.name_lang, language_id));
            if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
            }
            $('textarea#froala_content_editor').froalaEditor('html.set', getcontentByLanguage(location_language.description, location_language.description_lang, language_id));
            $('#location_address').val(getcontentByLanguage(location_language.address, location_language.address_lang, language_id));
            $('#contact_name').val(getcontentByLanguage(location_language.contact_name, location_language.contact_name_lang, language_id));
        }
    });
    $(".travel-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        if (travel_language != '') {
            $('#travel-name').val(getcontentByLanguage(travel_language.name, travel_language.name_lang, language_id));
            if ($('textarea#froala_content_editor').froalaEditor('codeView.isActive')) {
                $('textarea#froala_content_editor').froalaEditor('codeView.toggle');
            }
            $('textarea#froala_content_editor').froalaEditor('html.set', getcontentByLanguage(travel_language.description, travel_language.description_lang, language_id));
        }
    });
    $(".menu-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        if (manu_parent_items_language != '') {
            var options = "";
            options += "<option value=''></option>";
            for (i = 0; i < manu_parent_items_language.length; i++) {
                options += "<option value=" + manu_parent_items_language[i].id + ">" + getcontentByLanguage(manu_parent_items_language[i].title, manu_parent_items_language[i].title_lang, language_id) + "</option>";
            }
            $('#menu-parent').html(options);
        }
        if (menu_language != '') {
            $('#menu-title').val(getcontentByLanguage(menu_language.title, menu_language.title_lang, language_id));
            $('#menu-parent').val(menu_language.parent.id);
        }
    });
    $(".group-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        default_language_id = $('#settings_defualt_language_id').val();
        $(".settings-groups-table tbody tr").each(function () {
            var group_name_lang = $(this).find('td:nth-child(4) a').attr('data-lang');
            var group_name = valueWithSpecialCharacter($(this).find('td:nth-child(4) a').html());
            if (group_name_lang != '' || group_name_lang != undefined) {
                var data = getGroupContentByLanguage(group_name, group_name_lang, language_id)
                // $(this).find('td:nth-child(4) a').html(data);
                $(this).find('td:nth-child(4) a').editable('setValue', data);
            }
        });
    });

    $(".hotel-language-presets-selector").select2({
        placeholder: "Select a preset"
    }).on("change", function (e) {
        var language_id = e.val;
        default_language_id = $('#hotel_defualt_language_id').val();
        var hotel_name_lang = $('#hotel-details').find('.hotel-name').attr('data-lang');
        var hotel_name = valueWithSpecialCharacter($('#hotel-details').find('.hotel-name').val());
        if (hotel_name_lang != '' || hotel_name_lang != undefined) {
            var data = getcontentByLanguage(hotel_name, hotel_name_lang, language_id)
            $('#hotel-details').find('.hotel-name').val(data);
        }
        $('#hotel-details').find('.hotel-room tr').each(function () {
            var room_description_lang = $(this).find('.room-description').attr('data-lang');
            var room_description = valueWithSpecialQuote($(this).find('.room-description').html());
            if (room_description_lang != '' || room_description_lang != undefined) {
                var data = getcontentByLanguage(room_description, room_description_lang, language_id)
                $(this).find('.room-description').html(data);
            }
        });
    });


});

function getcontentByLanguage(data, data_lang, language_id) {
    try {
        if (data_lang != '' && data_lang != null && data_lang != undefined) {
            var data_list = JSON.parse(data_lang.replace(/\n/g, "\\n").replace(/\r/g, "\\r").replace(/\t/g, "\\t").replace(/\f/g, "\\f"));
            if (data_list != null && data_list != '' && data_list != undefined) {
                if (data_list[language_id] != undefined) {
                    data = (data_list[language_id]);
                } else if (default_language_id != "" && data_list[default_language_id] != undefined) {
                    data = (data_list[default_language_id]);
                }
                else {
                    data = "";
                }
            }
        }
    } catch (exception) {
        console.log(exception);
    }
    if (data != '' && data != null && data != undefined) {
        data = data.replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&");
    }
    console.log(data);
    return data;

}

function getGroupContentByLanguage(data, data_lang, language_id) {
    try {
        if (data_lang != '' && data_lang != null && data_lang != undefined) {
            var data_list = JSON.parse(data_lang.replace(/\n/g, "\\n").replace(/\r/g, "\\r").replace(/\t/g, "\\t").replace(/\f/g, "\\f"));
            if (data_list != null && data_list != '' && data_list != undefined) {
                if (data_list[language_id] != undefined) {
                    data = (data_list[language_id]);
                } else if (default_language_id != "" && data_list[default_language_id] != undefined) {
                    data = (data_list[default_language_id]);
                }
            }
        }
    } catch (exception) {
        console.log(exception);
    }
    if (data != '' && data != null && data != undefined) {
        data = data.replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&amp;/g, "&");
    }
    return data;

}