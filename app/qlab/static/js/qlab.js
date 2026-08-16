document.addEventListener('DOMContentLoaded', () => {
    // Pick a stable parent that contains all your buttons
    const container = document.querySelector('[data-qlab-container]');
    if (!container) return; // fail gracefully if not present



    container.addEventListener('click', async (event) => {
        // Find the closest element with .qlab_action (handles nested elements)
        const target = event.target.closest('.qlab_action');
        if (!target) return; // click wasn't on a relevant element

        event.preventDefault();

		const action = target.dataset.action;
        const statusEl = document.getElementById('qlab_status')
        let req_data = {};

        if (action === 'fire_qlab_cue' || action === 'stop_qlab_cue') {
            const cueInput = document.getElementById('cue');
            const cue_number = parseInt(cueInput.value, 10);

            if (!(cue_number >= 1 && cue_number <= 500)) {
                alert('Please enter a cue number');
                return;
            }

            req_data = { action, cue_number };
        } else {
            req_data = { action };
        }

        try {

            const data = await api.post(
                '/qlab/api/qlab_cue_action',
                req_data
            );

            statusEl.textContent = data.text;

            if (data.result === 1) {
                statusEl.textContent = data.text;
            } else {
                statusEl.textContent = `${data.text} Contact Support`;
            }
        } catch (err) {
            statusEl.textContent = 'Action Failed. Contact Support';
        }
    });
});