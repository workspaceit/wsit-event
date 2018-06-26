// FORM LOGIC //
var base_url = window.location.origin + '/' + event_url;
var csrf_token = $('input[name=csrfmiddlewaretoken]').val();

$(document).ready(function(){
    sessionId=$("#speakerSessions").val();
    sessionType=$("#sessionType").val();
    appendAttendeeToTable(sessionId,sessionType);
});

$('body').on('change', "#speakerSessions", function () {
    sessionId=$("#speakerSessions").val();
    sessionType=$("#sessionType").val();
    appendAttendeeToTable(sessionId,sessionType);
});
$('body').on('change', "#sessionType", function () {
    sessionId=$("#speakerSessions").val();
    sessionType=$("#sessionType").val();
    appendAttendeeToTable(sessionId,sessionType);
});

function appendAttendeeToTable(sessionId,sessionType){

    $.ajax({
        url: base_url + '/getDesiredAttList/',
        type: "POST",
        data: {'sessionId': sessionId,'sessionType':sessionType, csrfmiddlewaretoken: csrf_token},
        success: function (response) {
            $("#attListTbl tbody").empty();
             $("#total_attending").text(response.attending);
             $("#total_cue").text(response.cue);
            $.each(response.datas, function( index, value ) {

//                value=$.parseJSON(value);
                newRowContent= "<tr><td>"+value[0]+" "+value[1]+"</td><td>"+value[2]+"</td><td>"+value[3]+"</td><td>"+value[4]+"</td></tr>";
                $("#attListTbl tbody").append(newRowContent);
            });

        }

    });



}


//If "I can't find a suitable flight" view "Comments regarding flight reservations / Special requests"
//$('body').on('change', "#no_suitable_flight", function () {
//    $("#flights_table").find("input[type='radio'], input[type='checkbox']").not("#no_suitable_flight").removeAttr("checked");
//    $("#travel3").slideDown("fast")
//    $("tr.homebound").hide();
//});

