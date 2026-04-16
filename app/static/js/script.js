function isRowComplete(rowData, requiredFields) {
    return requiredFields.every(field => {
        return rowData[field] !== undefined && rowData[field] !== "";
    });
  }

function editCell(cell, table, requiredFields) {
    const row = cell.getRow();
    const rowValues = row.getData();
    const rowID = row.getIndex()

    // Only act on NEW rows (no id yet)
    if (!rowID) {
        if (isRowComplete(rowValues, requiredFields)) {
            console.log("Should be Complete")
            sendNewRowToDB(rowValues, row, table);
        }
        return;
    } else {
        const rowData = {
          "ID": cell.getRow().getIndex(),
          "table": table,
          "field": cell.getField(),
          "value": cell.getValue()
        }
      
        sendFieldToDb(rowData, cell);
    }
}



async function sendNewRowToDB(rowData, row, table) {
    sendItems = {
        table: table,
        rowData: rowData
    }
    const response = await fetch("/insert_db_row", {
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

async function sendFieldToDb(rowData, cell) {
    try {
        const response = await fetch("/update_db_field", {
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
