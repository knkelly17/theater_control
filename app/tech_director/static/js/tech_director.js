async function refreshAvailableStudentOptions(exclude) {

    const select = document.getElementById("student_id");
    const endpoint = `/tech_director/get_list_of_students/${exclude}`
    const payload = ''
    const options =  await api.post(
        endpoint,
        payload
    );

    select.replaceChildren();

    options.forEach(([student_id, full_name]) => {
        select.add(new Option(full_name, student_id));
    });
}