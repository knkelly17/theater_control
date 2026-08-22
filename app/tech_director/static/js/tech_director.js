const TechDirectorActions = {

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
    }

}