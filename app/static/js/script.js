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
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(rowData)
        });

        if (response.status === 401) {
            window.location.href = '/profile/login?next=' + encodeURIComponent(window.location.pathname + window.location.search);
            return;
        }

        if (!response.ok) {
            return;
        }

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


