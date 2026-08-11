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

const api_v1 = {

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
    },

    async put(endpoint, payload) {
        const response = await fetch(endpoint, {
            method: "PUT",
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
};

const api = {

    async _request(method, endpoint, payload = null) {

        const options = {
            method,
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            }
        };

        if (payload !== null) {
            options.body = JSON.stringify(payload);
        }

        const response = await fetch(endpoint, options);

        const data = await response.json().catch(() => ({}));

        handleFetchResponse(response);

        if (!response.ok) {
            throw new Error(data.message || `Request failed (${response.status})`);
        }

        return data;
    },

    get(endpoint) {
        return this._request("GET", endpoint);
    },

    post(endpoint, payload) {
        return this._request("POST", endpoint, payload);
    },

    put(endpoint, payload) {
        return this._request("PUT", endpoint, payload);
    },

    delete(endpoint) {
        return this._request("DELETE", endpoint);
    }
};