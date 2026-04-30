$(function(){
	$('#submit_login').on("click", function(){
	    var username = $("#username").val();
	    var password = $("#password").val();
	    if (!(username && password)) {
	        alert('Please enter both username and password')
	        return false
	    }
		const now = new Date();
		const year = now.getFullYear();
		const month = String(now.getMonth() + 1).padStart(2, '0');
		const day = String(now.getDate()).padStart(2, '0');
		const hours = String(now.getHours()).padStart(2, '0');
		const minutes = String(now.getMinutes()).padStart(2, '0');
		const seconds = String(now.getSeconds()).padStart(2, '0');

		const formattedDate = `${year}${month}${day}${hours}${minutes}${seconds}`;
	    var req_data = {username: username, password: password, timestamp: formattedDate}
		
	    $.post('/profile/login', req_data).done(function(response) {
				if (response['login_result'] == 1) {
					window.location.href = response['text'];
				} else {
					$('#login_status').text(response['text']);
				}
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
					alert('Password changed successfully. Please log in again.')
					window.location.href = response['text'];
				} else {
					$('#login_status').text(response['text']);
				}
            }).fail(function() {
                $('#login_status').text('Action Failed. Contact Support');
            });
        return false
	});

});