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
            const data = await api.post(
                '/etcconnect/api/level_set',
                req_data
            );
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
