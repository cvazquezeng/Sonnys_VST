// Custom sorting for MM-DD-YY HH:MM AM/PM format
jQuery.extend(jQuery.fn.dataTableExt.oSort, {
    "date-mm-dd-yy-pre": function(dateString) {
        if (!dateString || dateString === 'N/A' || dateString === 'NaN') {
            return -Infinity; // Place blank or invalid values at the start
        }

        // Split the date string into parts
        const parts = dateString.split(' ');
        const dateParts = parts[0].split('-');
        const timeParts = parts[1].split(':');
        const period = parts[2];

        let hour = parseInt(timeParts[0], 10);
        const minute = parseInt(timeParts[1], 10);

        if (period === 'PM' && hour !== 12) {
            hour += 12;
        } else if (period === 'AM' && hour === 12) {
            hour = 0;
        }

        const parsedDate = new Date(
            2000 + parseInt(dateParts[2], 10),
            parseInt(dateParts[0], 10) - 1,
            parseInt(dateParts[1], 10),
            hour,
            minute
        );

        return parsedDate.getTime();
    },

    "date-mm-dd-yy-asc": function(a, b) {
        return a - b;
    },

    "date-mm-dd-yy-desc": function(a, b) {
        return b - a;
        return b - a;
    }
});

function filterFutureRows() {
    const tableSelector = '#closed-tickets-table';
    const currentTime = new Date();

    $(tableSelector + ' tbody tr').each(function() {
        const requestMadeAt = $(this).find('td').eq(4).text().trim();
        const requestDate = parseDate(requestMadeAt);

        if (requestDate > currentTime) {
            $(this).hide(); // Use .hide() instead of .remove() to maintain the row structure
        } else {
            $(this).show(); // Ensure rows are visible if they aren't filtered
        }
    });
}

function parseDate(dateString) {
    if (!dateString || dateString === 'N/A' || dateString === 'NaN') {
        return new Date(0); // Return epoch time for invalid dates
    }

    // Split the date string into parts
    const parts = dateString.split(' ');
    const dateParts = parts[0].split('-');
    const timeParts = parts[1].split(':');
    const period = parts[2];

    let hour = parseInt(timeParts[0], 10);
    const minute = parseInt(timeParts[1], 10);

    if (period === 'PM' && hour !== 12) {
        hour += 12;
    } else if (period === 'AM' && hour === 12) {
        hour = 0;
    }

    return new Date(
        2000 + parseInt(dateParts[2], 10),
        parseInt(dateParts[0], 10) - 1,
        parseInt(dateParts[1], 10),
        hour,
        minute
    );
}


function calculateDeltaTime(start, end) {
    if (!start || !end) return 0; // Return 0 for invalid inputs

    const startDate = new Date(start);
    const endDate = new Date(end);

    const diffInMs = endDate - startDate;
    const diffInMinutes = Math.round(diffInMs / 60000);

    if (diffInMinutes < 0 || endDate > new Date()) {
        return 0; // Return 0 for future dates
    }

    return diffInMinutes;
}

function initializeDataTable() {
    const tableSelector = '#closed-tickets-table';
    if ($(tableSelector).length) {
        if ($.fn.DataTable.isDataTable(tableSelector)) {
            $(tableSelector).DataTable().destroy();
            console.log("Destroyed previous DataTable instance"); // Debugging
        }

        // Initialize DataTable
        const dataTable = $(tableSelector).DataTable({
            "paging": false,
            "searching": true,
            "ordering": true,
            "info": true,
            "order": [[4, "desc"]],
            "language": {
                "paginate": {
                    "previous": "Previous",
                    "next": "Next"
                },
                "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                "lengthMenu": "Show _MENU_ entries"
            },
            "dom": 'Brti', // Ensure buttons are placed correctly
            "buttons": [
                {
                    extend: 'excelHtml5',
                    text: '<i class="fas fa-file-excel"></i> Export to Excel',
                    className: 'btn btn-success btn-sm ml-2',
                    exportOptions: {
                        columns: ':visible', // Ensure only visible columns are exported
                        modifier: {
                            search: 'applied', // Only export filtered data
                            order: 'applied'   // Maintain the current order
                        }
                    }
                }
            ],
            "columnDefs": [
                {
                    "targets": 4,
                    "type": "date-mm-dd-yy"
                },
                {
                    "targets": -1,
                    "render": function(data, type, row) {
                        const requestMadeAt = row[4];
                        const closedAt = row[6];
                        return calculateDeltaTime(requestMadeAt, closedAt);
                    }
                },
                {
                    "targets": [4, 5, 6],
                    "render": function(data) {
                        if (data === 'N/A' || data === 'NaN' || !data) {
                            return '';
                        }
                        return data;
                    }
                }
            ],
            "createdRow": function(row, data) {
                const requestMadeAt = data[4];
                const closedAt = data[6];
                const deltaTime = calculateDeltaTime(requestMadeAt, closedAt);
                $('td', row).eq(7).text(deltaTime);
            }
        });
        
        

        // Filter rows with future request dates
        filterFutureRows();

        // Event listeners for filter dropdowns
        $('#lineMachineFilter').multiselect({
            includeSelectAllOption: true,
            enableFiltering: true,
            buttonWidth: '100%',
            nonSelectedText: 'Select Line Machines',
            onInitialized: function() {
                $('#lineMachineFilter').show();
            },
            onChange: function() {
                applyLineMachineFilter(dataTable);
            },
            onSelectAll: function() { // Ensuring select all triggers the filter
                applyLineMachineFilter(dataTable);
            }
        });

        $('#monthFilter').multiselect({
            includeSelectAllOption: true,
            enableFiltering: true,
            buttonWidth: '100%',
            nonSelectedText: 'Select Months',
            onInitialized: function() {
                $('#monthFilter').show();
            },
            onChange: function(option, checked) {
                applyMonthFilter(dataTable);
            },
            onSelectAll: function() { // Ensuring select all triggers the filter
                applyMonthFilter(dataTable);
            }
        });

        // Append the export button
        dataTable.buttons().container().appendTo('#exportButtons');
    }
}

function applyMonthFilter(dataTable) {
    const selectedOptions = $('#monthFilter').val();
    if (selectedOptions && selectedOptions.length > 0) {
        // Create a regex pattern to match the start of the date string
        const pattern = selectedOptions.join('|');
        dataTable.column(4).search(`^(${pattern})`, true, false).draw();
    } else {
        dataTable.column(4).search('').draw();
    }
    /*console.log("Month filter applied: ", selectedOptions); // Debugging*/
}

function applyLineMachineFilter(dataTable) {
    const selectedOptions = $('#lineMachineFilter').val();
    const values = selectedOptions.filter(option => option !== "");
    const pattern = values.length > 0 ? `^(${values.join('|')})$` : '';
    dataTable.column(1).search(pattern, true, false).draw();
   /* console.log("Line machine filter applied: ", values); // Debugging */
}



function initializeTooltip() {
    const tableSelector = '#closed-tickets-table';
    if ($(tableSelector).length) {
        $(tableSelector + ' tbody').on('mouseenter', 'td.tooltip-cell', function() {
            var tooltipText = $(this).attr('title');
            var tooltip = $('<div class="tooltip-custom"></div>').text(tooltipText).appendTo('body');
            var offset = $(this).offset();
            tooltip.css({
                top: offset.top + $(this).outerHeight() - 80,
                left: offset.left + $(this).outerWidth() / 2 - tooltip.outerWidth() / 2
            });
            tooltip.show().css('opacity', 1);
        });

        $(tableSelector + ' tbody').on('mouseleave', 'td.tooltip-cell', function() {
            $('.tooltip-custom').remove();
        });
    }
}

function waitForjQuery() {
    if (typeof jQuery !== 'undefined') {
        console.log('jQuery is loaded');
        $(document).ready(function() {
            console.log('Document is ready');
            initializeDataTable();
            initializeTooltip();
        });
    } else {
        console.log('Waiting for jQuery to load...');
        setTimeout(waitForjQuery, 100);
    }
}

waitForjQuery();
