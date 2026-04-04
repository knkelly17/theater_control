$(function(){
	
	$('.channel_set_button').on("click", function(){
	    var set_button = $(this).attr('id')
	    var level = 'full'

	    var chanID = $("#channel_full_out").val();

	    if (set_button == 'channelOut'){
	        level = 'out'
	    } else if (set_button == 'channelLevelButton'){
	        chanID = $("#channel_level").val();
	        level = $("#set_level").val();
	        if (!(level >=0 && level <=100)) {
	            alert('Please set level between 1 - 100')
	            return false
	        }
	    }

		if (chanID >= 1 && chanID <=500) {
            var req_data = {level: level, chan_id: chanID};
            $.post('/channelSetAJAX', req_data).done(function(response) {
                $('#etc_status').text(response['text']);
            }).fail(function() {
                $('#etc_status').text('Action Failed. Contact Support');
            });
        } else {
            alert('Please enter Channel Number between 1 - 500')
        }
        return false
	});

	$('#addressLevelButton').on("click", function(){

	    var addrID = $("#address").val();

	    level = $("#addressLevel").val();

	    if (!(level >=0 && level <=100)) {
	        alert('Please set level between 1 - 100')
	        return false
	    }

		if (addrID >= 1 && addrID <=500) {
            var req_data = {level: level, addr_id: addrID};
            $.post('/addressSetAJAX', req_data).done(function(response) {
                $('#etc_status').text(response['text']);
            }).fail(function() {
                $('#etc_status').text('Action Failed. Contact Support');
            });
        } else {
            alert('Please enter an Address Number between 1 - 500')
        }
        return false
	});

	$('#fire_cue').on("click", function(){
	    var cue_number = $("#cue").val();
	    if (!(cue_number >=1 && cue_number<=500)) {
	        alert('Please enter a cue number')
	        return false
	    }
	    var req_data = {level:'cue', cue_number:cue_number}
	    $.post('/channelSetAJAX', req_data).done(function(response) {
                $('#etc_status').text(response['text']);
            }).fail(function() {
                $('#etc_status').text('Action Failed. Contact Support');
            });
        return false
	});

});