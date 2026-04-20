function isRowComplete(rowData, requiredFields) {
    return requiredFields.every(field => {
        return rowData[field] !== undefined && rowData[field] !== "";
    });
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


async function sendNewRowToDB(rowData, row, table, endpoint) {
    sendItems = {
        table: table,
        rowData: rowData
    }
    const response = await fetch(endpoint, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(sendItems)
    });

    const data = await response.json();

    if (response.ok) {
        // ✅ assign ID so it becomes a normal row
        row.update({ ID: data.value });

        row.getElement().style.backgroundColor = "#c8f7c5";
    }
}

async function sendFieldToDb(rowData, cell, endpoint) {
    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(rowData)
        });

        const data = await response.json();
        

        if (!response.ok) {
            throw new Error(data.message || "Error");
        }

        // ✅ success feedback
        cell.getElement().style.backgroundColor = "#c8f7c5"; // light green
        // cell.setValue(data.value);

    } catch (error) {
        console.error(error);

        // ❌ error feedback
        cell.getElement().style.backgroundColor = "#f7c5c5"; // light red
    }
    
}
