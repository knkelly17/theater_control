async function call(endpoint, data) { //post function below should replace this one
    const response = await fetch(`/api/${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    return handleFetchResponse(response);
}

const api = {

    async post(endpoint, payload) {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json().catch(() => ({}));

        handleFetchResponse(response);

        if (!response.ok) {
            throw new Error(data.message || `Request failed (${response.status})`);
        }

        return data;
    }
}