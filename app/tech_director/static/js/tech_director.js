const TechDirectorActions = {

    async  getTeamLabels() {
        const rows = await TabulatorActions.getData(
            "/tech_director/api/list_teams_options/"
        );

        return Object.fromEntries(
            rows.map((team) => [String(team.index_id), team.name])
        );
    },  

    async  getTechTeamLabels() {
        const rows = await TabulatorActions.getData(
            "/tech_director/api/list_tech_teams_options/"
        );

        return Object.fromEntries(
            rows.map((team) => [String(team.index_id), team.name])
        );
    },

    async  getSkillLevels() {
        const rows = await TabulatorActions.getData(
            "/tech_director/api/list_skill_levels/"
        );

        return Object.fromEntries(
            rows.map((skills) => [String(skills.index_id), skills.name])
        );
    },

    async  refreshAvailableStudentOptions(exclude) {

        const select = document.getElementById("student_id");
        const endpoint = `/tech_director/api/get_list_of_students_name_options/${exclude}`
        const payload = ''
        const options =  await api.get(
            endpoint
        );

        select.replaceChildren();

        options.forEach(([student_id, full_name]) => {
            select.add(new Option(full_name, student_id));
        });
    },

    async  getInventoryTypes() {
        const rows = await TabulatorActions.getData(
            "/tech_director/api/list_inventory_type_options/"
        );

        return Object.fromEntries(
            rows.map((team) => [String(team.index_id), team.name])
        );
    }, 

    async uploadGoogleSheet(endpoint, payload, responseDiv) {
        const loader = document.getElementById('ajax-loader');

        loader.style.display = 'block';

        try {
            const data = await api.post(endpoint, payload);
            responseDiv.textContent = data;
        } catch (error) {
            console.error(error);
            responseDiv.textContent = error.message || 'The upload failed.';
        } finally {
            loader.style.display = 'none';
        }
    }

}