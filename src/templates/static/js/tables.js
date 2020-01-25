
var table, workstationTable
$(document).ready( function () {
    workstationTable = $('#workstation_table').DataTable({
        searching: false,
        paging: false,
        info: false
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
        })
}
