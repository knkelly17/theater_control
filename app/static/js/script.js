const originalFetch = window.fetch.bind(window);

const TabulatorActions = {

    async createRow(target, endpoint, requiredFields=[], excludedFields = []) {
        let row = null;

        if (target && typeof target.getData === "function") {
            row = target;
        } else if (target && typeof target.getRow === "function") {
            row = target.getRow();
        }

        if (!row || typeof row.getData !== "function") {
            return Promise.resolve(null);
        }

        const rowValues = row.getData();
        const payloadToSend = removeExcludedFields(rowValues, excludedFields);

        const missingFields = requiredFields.filter(field =>
            payloadToSend[field] === undefined || payloadToSend[field] === ""
        );

        if (missingFields.length > 0) {
            return Promise.reject(
                new Error(`Please complete: ${missingFields.join(", ")}.`)
            );
        }

        const data = await api.post(
            endpoint,
            preparePayload(payloadToSend)
        );

        row.update(data);
        row.getElement().classList.add("w3-pale-green");
        setTimeout(() => row.getElement().classList.remove("w3-pale-green"), 2000);

    },

    async  updateCell(cell, endpoint) {
        const row = cell.getRow();
        const rowValues = row.getData();
        const rowID = row.getIndex()


        const rowData = {
            "ID": cell.getRow().getIndex(),
            "field": cell.getField(),
            "value": cell.getValue()
        };

        payloadToSend = normalizePayloadForDb(rowData)

        try {
            const data = await api.put(
                endpoint,
                preparePayload(payloadToSend)
            );

            cell.getElement().classList.add("w3-pale-green");
            setTimeout(() => cell.getElement().classList.remove("w3-pale-green"), 1000);
        } catch(error) {
            console.error(error);
            // ❌ error feedback
            cell.getElement().classList.add("w3-pale-red");
        }

        //sendFieldToDb(rowData, cell, endpoint);
    }, 

    

}

const PageSetup = {
    
    setupAddRecordControls({
        table,
        addButton,
        cancelButton,
        errorField,
        createEndpoint,
        updateEndpoint,
        requiredFields,
        excludedFields,
    }) {
        let pendingNewRow = null;

        table.on("cellEdited", (cell) => {
            if (excludedFields.includes(cell.getField())) {
                return;
            }

            const row = cell.getRow();

            if (row.getIndex()) {
                TabulatorActions.updateCell(cell, updateEndpoint); 
                return; // Existing-row update handling goes here.
            }

            const value = cell.getValue();
            const isEmpty = value === undefined ||
                            value === null ||
                            (typeof value === "string" && value.trim() === "");

            if (isEmpty) {
                return;
            }

            TabulatorActions.createRow(
                row, createEndpoint, requiredFields, excludedFields
            )
            .then(() => {
                pendingNewRow = null;
                errorField.textContent = "";
                addButton.classList.replace("w3-hide", "w3-show");
                cancelButton.classList.replace("w3-show", "w3-hide");
            })
            .catch((error) => {
                errorField.textContent = error.message;
            });
        });

        addButton.addEventListener("click", () => {

            table.addRow({ ID: null }, true).then((row) => {
                pendingNewRow = row;
                addButton.classList.replace("w3-show", "w3-hide");
                cancelButton.classList.replace("w3-hide", "w3-show");
                row.select()
                setTimeout(function () {
                    row.getCells()[0]?.edit();
                }, 0);
            });
        });

        cancelButton.addEventListener("click", () => {
            pendingNewRow?.delete();
            pendingNewRow = null;
            errorField.textContent = "";
            addButton.classList.replace("w3-hide", "w3-show");
            cancelButton.classList.replace("w3-show", "w3-hide");
        });
    }
}



window.fetch = async function(...args) {
    const response = await originalFetch(...args);

    if (response && response.status === 401 && !window.location.pathname.startsWith('/profile/login')) {
        window.location.href = '/profile/login?next=' + encodeURIComponent(window.location.pathname + window.location.search);
    }

    return response;
};

function handleFetchResponse(response) {
    if (response.status === 401) {
        window.location.href = '/profile/login?next=' + encodeURIComponent(window.location.pathname + window.location.search);
        return null;
    }

    if (response.status === 403) {
        alert('You do not have permission to perform this action.');
        return null;
    }

    if (!response.ok) {
        return response;
    }

    return response;
}

function isRowComplete(rowData, requiredFields) {
    return requiredFields.every(field => {
        return rowData[field] !== undefined && rowData[field] !== "";
    });
  }

function normalizeValueForDb(value) {
    if (typeof value === "boolean") {
        return value ? 1 : 0;
    }

    if (typeof value === "string") {
        const normalized = value.trim().toLowerCase();
        if (normalized === "true") return 1;
        if (normalized === "false") return 0;
    }

    return value;
}

function normalizePayloadForDb(value) { //***this gets replaced by preparePayload 
    if (Array.isArray(value)) {
        return value.map(normalizePayloadForDb);
    }

    if (value && typeof value === "object") {
        return Object.fromEntries(
            Object.entries(value).map(([key, nestedValue]) => [key, normalizePayloadForDb(nestedValue)])
        );
    }

    return normalizeValueForDb(value);
}

function preparePayload(value) {
    if (Array.isArray(value)) {
        return value.map(preparePayload);
    }

    if (value && typeof value === "object") {
        return Object.fromEntries(
            Object.entries(value).map(([key, nestedValue]) => [key, preparePayload(nestedValue)])
        );
    }

    return normalizeValueForDb(value);
}

function sanitizeRowPayloadForDb(rowData, excludedFields = []) { //***replaced by removeExcludedFields
    if (!rowData || typeof rowData !== "object") {
        return rowData;
    }

    const sanitized = { ...rowData };
    excludedFields.forEach((field) => {
        delete sanitized[field];
    });
    return sanitized;
}

function removeExcludedFields(rowData, excludedFields = []) {
    if (!rowData || typeof rowData !== "object") {
        return rowData;
    }

    const sanitized = { ...rowData };
    excludedFields.forEach((field) => {
        delete sanitized[field];
    });
    return sanitized;
}

function editCell(cell, table, endpoint) {
    const row = cell.getRow();
    const rowValues = row.getData();
    const rowID = row.getIndex()


    const rowData = {
        "ID": cell.getRow().getIndex(),
        "table": table,
        "field": cell.getField(),
        "value": cell.getValue()
    };
   
    sendFieldToDb(rowData, cell, endpoint);
}

function addRow(cell, table, requiredFields, endpoint) {
    const row = cell.getRow();
    const rowValues = row.getData(); 

    if (isRowComplete(rowValues, requiredFields)) {
        sendNewRowToDB(rowValues, row, table, endpoint);
    }

    return;
}

async function addRowAPI(target, endpoint, requiredFields=[], excludedFields = []) {
    let row = null;

    if (target && typeof target.getData === "function") {
        row = target;
    } else if (target && typeof target.getRow === "function") {
        row = target.getRow();
    }

    if (!row || typeof row.getData !== "function") {
        return Promise.resolve(null);
    }

    const rowValues = row.getData();
    //const payloadForDb = removeExcludedFields(rowValues, excludedFields);
    const payloadToSend = removeExcludedFields(rowValues, excludedFields);

    const missingFields = requiredFields.filter(field =>
        payloadToSend[field] === undefined || payloadToSend[field] === ""
    );

    if (missingFields.length > 0) {
        return Promise.reject(
            new Error(`Please complete: ${missingFields.join(", ")}.`)
        );
    }

    const data = await api.post(
        endpoint,
        preparePayload(payloadToSend)
    );

    row.update(data);
    row.getElement().classList.add("w3-pale-green");
    setTimeout(() => row.getElement().classList.remove("w3-pale-green"), 2000);

}

async function sendNewRowToDBAPI(rowData, row, endpoint) {
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(normalizePayloadForDb(rowData))
    });
 
    const data = await response.json().catch(() => ({}));

    const handledResponse = handleFetchResponse(response);

    if (!handledResponse) {
        return;
    }

    if (!response.ok) {
        throw new Error(data.message || `Request failed (${response.status})`);
    }

    row.update(data);
    row.getElement().classList.add("w3-pale-green");
    setTimeout(() => row.getElement().classList.remove("w3-pale-green"), 2000);
    
}


async function sendNewRowToDB(rowData, row, table, endpoint) {
    const sendItems = {
        table: table,
        rowData: rowData
    }
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(normalizePayloadForDb(sendItems))
    });

    const handledResponse = handleFetchResponse(response);
    if (!handledResponse) {
        return;
    }

    if (!handledResponse.ok) {
        return;
    }

    const data = await handledResponse.json();

    if (handledResponse.ok) {
        // ✅ assign ID so it becomes a normal row
        row.update({ ID: data.value });

        //row.getElement().style.backgroundColor = "#c8f7c5";
        row.getElement().classList.add("w3-pale-green");
        setTimeout(() => row.getElement().classList.remove("w3-pale-green"), 500);


    }
}

async function callAPIGeneric (endpoint, parameters) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(normalizePayloadForDb(parameters))
        });

        const handledResponse = handleFetchResponse(response);
        if (!handledResponse) {
            return;
        }

        if (!handledResponse.ok) {
            return;
        }

        const data = await handledResponse.json();

        if (!handledResponse.ok) {
            throw new Error(data.message || "Error");
        }

        return data

    } catch (error) {
        console.error(error);
    }  
}

async function editCellAPI(cell, endpoint) {
    const row = cell.getRow();
    const rowValues = row.getData();
    const rowID = row.getIndex()


    const rowData = {
        "ID": cell.getRow().getIndex(),
        "field": cell.getField(),
        "value": cell.getValue()
    };

    payloadToSend = normalizePayloadForDb(rowData)

    try {
        const data = await api.put(
            endpoint,
            preparePayload(payloadToSend)
        );

        cell.getElement().classList.add("w3-pale-green");
        setTimeout(() => cell.getElement().classList.remove("w3-pale-green"), 1000);
    } catch(error) {
        console.error(error);
        // ❌ error feedback
        cell.getElement().classList.add("w3-pale-red");
    }

    //sendFieldToDb(rowData, cell, endpoint);
}

async function sendFieldToDb(rowData, cell, endpoint) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(normalizePayloadForDb(rowData))
        });

        const handledResponse = handleFetchResponse(response);
        if (!handledResponse) {
            return;
        }

        if (!handledResponse.ok) {
            return;
        }

        const data = await handledResponse.json();
        

        if (!handledResponse.ok) {
            throw new Error(data.message || "Error");
        }

        // ✅ success feedback
        //cell.getElement().style.backgroundColor = "#c8f7c5"; // light green
        cell.getElement().classList.add("w3-pale-green");
        setTimeout(() => cell.getElement().classList.remove("w3-pale-green"), 1000);
        // cell.setValue(data.value);

    } catch (error) {
        console.error(error);

        // ❌ error feedback
        //cell.getElement().style.backgroundColor = "#f7c5c5"; // light red
        cell.getElement().classList.add("w3-pale-red");
    }
    
}

function getHighSchoolClass(gradYear) {
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth(); // 0-indexed (0 = January, 5 = June)
  let next_year = 0

  if (currentMonth >= 5) {
    next_year = 1
  }

  const the_grade = next_year + 12 - gradYear + currentYear
  
  switch (the_grade) {
    case 12:
      return "Senior";
    case 11:
      return "Junior";
    case 10:
      return "Sophomore";
    case 9:
      return "Freshman";
    default:
      return gradYear > currentYear ? "Not yet in High School" : "Graduated";
  }
}

function editableForNewRows(cell) {
    return !cell.getRow().getData().indexId;
}

async function activeUpdate(cell) {
    const sendItems = {
        channel: cell.getRow().getIndex(),
        field: cell.getField(),
        value: cell.getValue()
    }
    const response = await fetch('/dm7/update_channel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(sendItems)
    });

    if (response.status === 401) {
        window.location.href = '/profile/login?next=' + encodeURIComponent(window.location.pathname + window.location.search);
        return;
    }

    if (!response.ok) {
        return;
    }

    const data = await response.json();

    if (response.ok) {
        console.log("ok");
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const allButton = document.getElementById("see_all_records");
    const activeButton = document.getElementById("see_active_records");

    //const cancelAddButton = document.getElementById("cancel_add");
    //const addRecordButton = document.getElementById("add_record");
    

    if (allButton && activeButton && pageTable && tableData) {

        let url = tableData;

        const selectorButtons = document.querySelectorAll(".active-selector");
        
        selectorButtons.forEach(button => {
            button.addEventListener('click', (event) => {
                const clickedButton = event.target;
                const clickedSpanLabel = clickedButton.dataset.spanLabel;

                const otherButton = Array.from(selectorButtons).find(btn => btn !== clickedButton);
                const otherSpanLabel = otherButton.dataset.spanLabel;
    
                const action = clickedButton['id']
                if (action == "see_all_records") {
                    url = table_base_url+"/all"
                } else if (action == "see_active_records") {
                    url = table_base_url+"/active"
                }

                clickedButton.classList.replace("w3-show", "w3-hide");
                document.getElementById(clickedSpanLabel).style.display = "inline-block";
                otherButton.classList.replace("w3-hide", "w3-show");
                document.getElementById(otherSpanLabel).style.display = "none";
                pageTable.setData(url);
            });
        });

        //pageTable.setData(url)
    }


   /*
    if (addRecordButton) {
        addRecordButton.addEventListener("click", function () {
            const blankRowData = {
                ID: null
            };

            pageTable.addRow(blankRowData, true)
                .then((row) => {
                cancelAddButton.classList.replace("w3-hide", "w3-show");
                addRecordButton.classList.add("w3-hide");
                row.select();
                setTimeout(function () {
                    const cell = row.getCells()[0];
                    if (cell) {
                    cell.edit();
                    }
                }, 0);
                })
        });
    }
        */
});


