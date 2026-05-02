document.addEventListener('DOMContentLoaded', () => {
	const container = document.querySelector('[data-etcconnect-container]');
    if (!container) return;


	const modeEl = container.querySelector('[data-role="mode"]');
	
    function updateLabels() {
		const mode = modeEl.value; // "channel", "address" or "cue"

		//show or hid the relevant sections
		const activeBlock = (mode === 'cue') ? 'cue' : 'channel';
		
		container.querySelectorAll(".etc_block").forEach(el => {
			const isActive = el.dataset.block === activeBlock;
			el.style.display = isActive ? 'block' : 'none';

			el.querySelectorAll('input, select, button').forEach(child => {
				child.disabled = !isActive;
			});
		});
		

		const this_block = container.querySelector(`[data-block="${activeBlock}"]`);
    	if (this_block) this_block.style.display = "block";

		//Set the labels for the channel/address block
    	container.querySelectorAll('[data-channel]').forEach(el => {
        	el.textContent = el.dataset[mode];
    	});
	}

    // Initial state on page load
    updateLabels();

    // Update when user changes dropdown
    container.addEventListener('change', (event) => {
        if (event.target.matches('[data-role="mode"]')) {
            updateLabels();
        }
    });

	container.addEventListener('click', async (event) => {
        const targetBtn = event.target.closest('.etc_action');
        if (!targetBtn) return;

        event.preventDefault();

        const action = targetBtn.dataset.action;

        // Pull current UI state
		const mode = modeEl.value; // "channel", "address" or "cue"
		const sel_level = (mode === 'cue') ? 'cue' : 'channel';
        const targetEl = container.querySelector('[data-role="target"]');
        const levelEl = container.querySelector(`[data-role="${sel_level}_level"]`);
        const statusEl = container.querySelector('[data-role="status"]');

		let target;

		if (action === 'fire_cue') {
			target = 'fire'
		} else {
			target = parseFloat(targetEl.value);
		}

		let level;

		if (action === 'set_level_full') {
			level = 100;
		} else if (action === 'set_level_out') {
			level = 0;
		} else {
			level = parseFloat(levelEl.value);
		}

        // Basic validation
        if (!target || target < 1) {
            statusEl.textContent = 'Enter a valid channel/address';
            return;
        }

        if (Number.isNaN(level) || level < 0 || level > 100) {
            statusEl.textContent = 'Enter a valid level (0–100)' + level;
            return;
        }

        // Build request based on mode
        const req_data = {
            action,
            mode,     // "channel" or "address"
            target,   // number
            level     // number
        };

        try {
            const response = await fetch('/etcconnect/level_set', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(req_data)
            });

            const data = await response.json();

            if (data.result === 1) {
                statusEl.textContent = data.text;
            } else {
                statusEl.textContent = data.text;
            }
        } catch (err) {
            statusEl.textContent = 'ETC action failed';
        }
    });
});

/* const selectElement = document.getElementById('fruitSelect');
const textElement = document.getElementById('displayText');

// Listen for the "change" event
selectElement.addEventListener('change', (event) => {
  const selectedValue = event.target.value;
  
  if (selectedValue) {
    textElement.textContent = `You selected: ${selectedValue}`;
  } else {
    textElement.textContent = "Choose a fruit to see it here!";
  }
});
/*
document.addEventListener('DOMContentLoaded', () => {
	// Pick a stable parent that contains all your buttons
	const container = document.querySelector('[data-etcconnect-container]');
	if (!container) return; // fail gracefully if not present	

	container.addEventListener('click', async (event) => {
		// Find the closest element with .channel_set_button (handles nested elements)
		const target = event.target.closest('.etcconnect_action');
		if (!target) return; // click wasn't on a relevant element

		event.preventDefault();
		
		const action = target.dataset.action;
		let req_data = {};
		if (action === 'channel_set') {
			const chanID = parseInt(document.getElementById('channel_full_out').value, 10);
			const level = action === 'channel_set' ? 'full' : document.getElementById('set_level').value;

			if (isNaN(chanID) || chanID < 1 || chanID > 500) {
				alert('Please enter Channel Number between 1 - 500');
				return;
			}
			if (level !== 'full' && (isNaN(level) || level < 0 || level > 100)) {
				alert('Please set level between 0 - 100');
				return;
			}

			req_data = { action, chan_id: chanID, level };
		} else if (action === 'address_set') {
			const addrID = parseInt(document.getElementById('address').value, 10);
			const level = document.getElementById('addressLevel').value;

			if (isNaN(addrID) || addrID < 1 || addrID > 500) {
				alert('Please enter an Address Number between 1 - 500');
				return;
			}
			if (isNaN(level) || level < 0 || level > 100) {
				alert('Please set level between 0 - 100');
				return;
			}

			req_data = { action, addr_id: addrID, level };
		} else if (action === 'cue_fire') {
			const cue_number = parseInt(document.getElementById('cue').value, 10);
			if (isNaN(cue_number) || cue_number < 1 || cue_number > 500) {
				alert('Please enter a cue number between 1 - 500');
				return;
			}
			req_data = { action, cue_number };
		} else {
			return; // unrecognized action
		}

		try {
			const response = await fetch(`/etcconnect/${action}AJAX`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(req_data)
			});

			const data = await response.json();

			if (data.result === 1) {
				document.getElementById('etc_status').textContent = data.text;
			} else {
				window.location.href = data.text;
			}
		} catch (err) {
			document.getElementById('etc_status').textContent = 'Action Failed. Contact Support';
		}
	});
}

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
            $.post('/etcconnect/channelSetAJAX', req_data).done(function(response) {
				if (response['result'] == 1) {
                	$('#etc_status').text(response['text']);
				} else {
					window.location.href = response['text'];
				}
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
            $.post('/etcconnect/addressSetAJAX', req_data).done(function(response) {
                if (response['result'] == 1) {
                	$('#etc_status').text(response['text']);
				} else {
					window.location.href = response['text'];
				}
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
	    var req_data = {cue_number:cue_number}
	    $.post('/etcconnect/cueFireAJAX', req_data).done(function(response) {
                if (response['result'] == 1) {
                	$('#etc_status').text(response['text']);
				} else {
					window.location.href = response['text'];
				}
            }).fail(function() {
                $('#etc_status').text('Action Failed. Contact Support');
            });
        return false
	});

});
*/