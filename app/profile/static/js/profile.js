document.addEventListener('DOMContentLoaded', () => {
	const l_container = document.querySelector('[data-login-container]');
    if (!l_container) return; // fail gracefully if not present

	l_container.addEventListener('click', async (event) => {
        // Find the closest element with .login_action (handles nested elements)
        const target = event.target.closest('.login_action');
        if (!target) return; // click wasn't on a relevant element

        event.preventDefault();

        const username = l_container.querySelector('[data-role="username"]').value;
        const password = l_container.querySelector('[data-role="password"]').value;
        const statusEl = l_container.querySelector('[data-role="login_status"]');

        const urlParams = new URLSearchParams(window.location.search);
        let nextPage = urlParams.get('next');
        if (!nextPage && window.location.pathname !== '/profile/login') {
            nextPage = window.location.pathname + window.location.search;
        }
		console.log(nextPage)

        if (!(username && password)) {
            alert('Please enter both username and password');
            return false;
        }

		const now = new Date();
		const year = now.getFullYear();
		const month = String(now.getMonth() + 1).padStart(2, '0');
		const day = String(now.getDate()).padStart(2, '0');
		const hours = String(now.getHours()).padStart(2, '0');
		const minutes = String(now.getMinutes()).padStart(2, '0');
		const seconds = String(now.getSeconds()).padStart(2, '0');

		const formattedDate = `${year}${month}${day}${hours}${minutes}${seconds}`;
		const req_data = {
            username: username,
            password: password,
            timestamp: formattedDate,
            next: nextPage
        } 

		
		try {
            const response = await fetch('/profile/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(req_data)
            });

            const data = await response.json();
 
            if (data.login_result === 1) {
                window.location.href = data['text'];
			} else {
				statusEl.textContent = data['text'];
			}
        } catch (err) {
            statusEl.textContent = 'Login failed';
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
	const p_container = document.querySelector('[data-profile-container]');
    if (!p_container) return; // fail gracefully if not present

	p_container.addEventListener('click', async (event) => {
        // Find the closest element with .login_action (handles nested elements)
        const target = event.target.closest('.profile_action');
        if (!target) return; // click wasn't on a relevant element

        event.preventDefault();

		const current_password = p_container.querySelector('[data-role="password"]').value;
		const new_password = p_container.querySelector('[data-role="new_password"]').value;
		const confirm_password = p_container.querySelector('[data-role="confirm_password"]').value;
		const statusEl = p_container.querySelector('[data-role="profile_status"]')

		if (!(current_password && new_password && confirm_password)) {
	        alert('Please fill in all fields')
	        return false
	    }

	    if (new_password !== confirm_password) {
	        alert('New passwords do not match')
	        return false
	    }

		const req_data = {
			current_password: current_password, 
			new_password: new_password, 
			confirm_password: confirm_password
		}
	   
		
		try {
            const response = await fetch('/profile/change_password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(req_data)
            });

            const data = await response.json();
 
            if (data.login_result === 1) {
                alert('Password changed successfully. Please log in again.')
					window.location.href = response['text'];
				} else {
					statusEl.textContent = data['text'];
				}
        } catch (err) {
            statusEl.textContent = 'Action Failed. Contact Support';
        }


	});
})



/*
$(function(){


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
*/