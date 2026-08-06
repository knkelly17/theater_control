async function refreshAvailableStudentOptions(exclude) {

    const select = document.getElementById("studentId");
    const endpoint = `/tech_director/get_list_of_students/${exclude}`
    const payload = ''
    const options =  await api.post(
        endpoint,
        payload
    );

    select.replaceChildren();

    options.forEach(([studentId, fullName]) => {
        select.add(new Option(fullName, studentId));
    });
}