
var table, inProgressTable, workstationTable
$(document).ready( function () {
    inProgressTable = $('#in_progress_table').DataTable({
        searching: false,
        paging: false,
        info: false,
        "columns": [
            {"data": "mode"},
            {"data": "base"},
            {"data": "from"},
            {"data": "work"},
            {"data": "save"},

        ]
    })

    inProgressTable.row.add({
        "mode": "Empty",
        "base": "Empty",
        "from": "Empty",
        "work": "Empty",
        "save": "Empty",
    })

    table = $('#log_table').DataTable();
} );

setInterval(fetchData, 500)

function fetchData() {
    fetch("/long_poll")
        .then((response) => {
            return response.json()
        })
        .then((response) => {
            console.log(response)
            inProgressTable.row(0).data(response)
            inProgressTable.draw()
        })
}
