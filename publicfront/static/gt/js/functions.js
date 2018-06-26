    (function( $ )
{

	if ( document.windowResizeFixFired )
	{
		return;
	}
	document.windowResizeFixFired = true;

	var $window = $(window),
		_wWidth = $window.width(),
		_wHeight = $window.height();

	$window.on(
		'resize',
		function( e )
		{
			var _nWidth = $window.width(),
				_nHeight= $window.height();

			if ( _wWidth == _nWidth && _wHeight == _nHeight )
			{
				e.preventDefault();
				e.stopImmediatePropagation();
				return;
			}
			_wWidth = _nWidth;
			_wHeight = _nHeight;
		}
	);

})( jQuery );
    
    $(document).ready(function() {
    	menuResizer();
    	//Shows the current menu-item's sub-menu
    	$('#menu.horizontalSubmenu').find('#MainMenuActive').next('ul').css("visibility", "visible");
    });
    
    //Shows the correct sub-menu on hover and temporarily hides the currenly selected sub-menu
    $("#menu.horizontalSubmenu li").hover(
    //On hover
    function() {
    	$('#menu.horizontalSubmenu').find('#MainMenuActive').next('ul').css("visibility", "hidden");
    	$(this).find('ul').css("visibility", "visible");
		//On mouse out
    }, function() {
    	$(this).find('ul').css("visibility", "hidden");
    	$('#menu.horizontalSubmenu').find('#MainMenuActive').next('ul').css("visibility", "visible");
    });
    
    $('#menu p').click(function() {
		menuHandler();
    });

    function menuHandler() {
    	if ($('#menu').find('ul').hasClass('up')) {
    		$('#menu').find('ul').slideDown('fast').addClass('down').removeClass('up');
    	} else {
    		$('#menu').find('ul').slideUp('fast').addClass('up').removeClass('down');
    	}
    }
    
    $(window).bind(
					'resize',
					function()
					{
						menuResizer();
					}
				);
				
	$(document).click(function(e) {
	    if ( $(e.target).closest('#menu').length === 0  && $('#menu').find('ul').hasClass('down')) {
	       menuHandler();
	    }
	});
    
    function menuResizer() {
    	if ($(window).width() <= 768) {
    		$('#menu').find('ul').hide().addClass('up');
    	} else {
    		$('#menu').find('ul').show().removeClass('up').removeClass('down');
    	}
    }

/*  	
<!--[if lt IE 8]>
<script>
//If client is lower or equal to IE7 than change menu to select (form element)
(function( $ ) {

if ( document.windowResizeFixFired ) {
	return;
}

document.windowResizeFixFired = true;

var $window = $(window),
	_wWidth = $window.width(),
	_wHeight = $window.height();

$window.bind(
	'resize',
	function( e )
	{
		var _nWidth = $window.width(),
			_nHeight= $window.height();

		if ( _wWidth == _nWidth && _wHeight == _nHeight )
		{
			e.preventDefault();
			e.stopImmediatePropagation();
			return;
		}
		_wWidth = _nWidth;
		_wHeight = _nHeight;
	}
);

})( jQuery );

// Create the dropdown base
$("<p><select / id='altMenu'></p>").appendTo("#menu");

// Create default option - same as .menuButton text
$("<option />", {
   "selected": "selected",
   "value"   : "",
   "text"    : $(".menuButton").text()
}).appendTo("#menu select");

// Populate dropdown with menu items
$("#menu a").each(function() {
 var el = $(this);
 $("<option />", {
     "value"   : el.attr("href"),
     "text"    : el.text()
 }).appendTo("#menu select");
});

$("#menu select").change(function() {
  window.location = $(this).find("option:selected").val();
});	

$(window).bind(
	'resize',
	function() {
		altMenu();
	}		
	);
				
function altMenu() {
				if ($(window).width() <= 768) {
				$(".menuButton").hide();
				$("#altMenu").show();
			} else {
				$("#altMenu").hide();
			}
}			
altMenu();
	
</script> 	    	
<![endif]-->
*/