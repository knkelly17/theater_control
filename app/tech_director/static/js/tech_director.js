async function refreshAvailableStudentOptions(exclude) {

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
}