$(function(){
	$('#submit_login').on("click", function(){
	    var username = $("#username").val();
	    var password = $("#password").val();
	    if (!(username && password)) {
	        alert('Please enter both username and password')
	        return false
	    }
	    var req_data = {username: username, password: password}
	    $.post('/', req_data).done(function(response) {
				if (response['login_result'] == 1) {
					window.location.href = response['text'];
				} else {
					$('#login_status').text(response['text']);
				}
				console.log(response)
            }).fail(function() {
                $('#login_status').text('Action Failed. Contact Support');
            });
        return false
	});

	$('#submit_change_password').on("click", function(){
	    var current_password = $("#password").val();
	    var new_password = $("#new_password").val();
	    var confirm_password = $("#confirm_password").val();

	    if (!(current_password && new_password && confirm_password)) {
	        alert('Please fill in all fields')
	        return false
	    }

	    if (new_password !== confirm_password) {
	        alert('New passwords do not match')
	        return false
	    }

	    var req_data = {current_password: current_password, new_password: new_password, confirm_password: confirm_password}
	    $.post('/change_password', req_data).done(function(response) {
				if (response['login_result'] == 1) {
					window.location.href = response['text'];
				} else {
					$('#login_status').text(response['text']);
				}
				console.log(response)
            }).fail(function() {
                $('#login_status').text('Action Failed. Contact Support');
            });
        return false
	});

});