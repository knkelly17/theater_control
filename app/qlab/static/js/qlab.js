$(function(){
	$('.qlab_action').on("click", function(){
	    var action = $(this).attr('id')
	    if (action == 'fire_qlab_cue' || action == 'stop_qlab_cue') {
	       var cue_number = $('#cue').val()
	       if (!(cue_number >=1 && cue_number<=500)) {
	           alert('Please enter a cue number')
	           return false
	       }
	       var req_data = {action:action,cue_number:cue_number}
	    } else {
	       var req_data = {action:action}
	    }
	    $.post('/qlab/qlabAJAX', req_data).done(function(response) {
	            if (response['result'] == 1) {
                	$('#etc_status').text(response['text']);
				} else {
					window.location.href = response['text'];
				}
            }).fail(function() {
                $('#qlab_status').text('Action Failed. Contact Support');
            });
	    return false

	})

});