// Improved tableini.js

function initializeDataTable() {
    const tableSelector = '#closed-tickets-table';
    if ($(tableSelector).length) {
        $(tableSelector).DataTable({
            "paging": true,
            "searching": true,
            "ordering": true,
            "info": true,
            "pageLength": 10, // Number of rows per page
            "lengthMenu": [10, 20, 30, 50], // Options for number of rows per page
            "order": [[6, "desc"]], // Column index 6 (request_made_at) sorted in descending order
            "language": {
                "paginate": {
                    "previous": "Previous",
                    "next": "Next"
                },
                "info": "Showing _START_ to _END_ of _TOTAL_ entries",
                "lengthMenu": "Show _MENU_ entries"
            }
        });
    }
}

function initializeTooltip() {
    const tableSelector = '#closed-tickets-table';
    if ($(tableSelector).length) {
        $(tableSelector + ' tbody').on('mouseenter', 'td.tooltip-cell', function() {
            var tooltipText = $(this).attr('title');
            var tooltip = $('<div class="tooltip-custom"></div>').text(tooltipText).appendTo('body');
            var offset = $(this).offset();
            tooltip.css({
                top: offset.top + $(this).outerHeight() - 80, // Adjust the -80 value as needed
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
        setTimeout(waitForjQuery, 100); // Check again in 100ms
    }
}

waitForjQuery();
