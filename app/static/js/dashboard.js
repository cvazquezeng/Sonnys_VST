// static/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded and parsed");

  const form = document.getElementById('filter-form');
  if (form) {
    form.addEventListener('submit', function(event) {
      event.preventDefault();
      console.log("Filter form submitted");
      fetchTickets();
    });
  } else {
    console.error("Filter form not found");
  }
});

function fetchTickets() {
  const startDate = document.getElementById('start-date').value;
  const endDate = document.getElementById('end-date').value;
  const lineMachine = document.getElementById('line-machine').value;
  const issueType = document.getElementById('issue-type').value;

  console.log("Fetching tickets with:", { startDate, endDate, lineMachine, issueType });

  fetch('/filter_tickets', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      start_date: startDate,
      end_date: endDate,
      line_machine: lineMachine,
      issue_type: issueType
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log("Received data:", data);
    renderTable(data);
  })
  .catch(error => console.error('Fetch error:', error));
}

function renderTable(data) {
  const summaryTable = document.getElementById('summary-table');
  if (!summaryTable) {
    console.error("Summary table element not found");
    return;
  }
  
  summaryTable.innerHTML = `
    <p>Total Tickets: ${data.total_tickets}</p>
    <p>Average Closing Time: ${data.avg_closing_time}</p>
    <p>Average Acknowledgment Time: ${data.avg_ack_time}</p>
    <p>Tickets Closed Without Acknowledgment: ${data.closed_without_ack}</p>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>ID</th>
          <th>Line Machine</th>
          <th>Issue Type</th>
          <th>Created At</th>
          <th>Acknowledged At</th>
          <th>Closed At</th>
        </tr>
      </thead>
      <tbody>
        ${data.tickets.map(ticket => `
          <tr>
            <td>${ticket.id}</td>
            <td>${ticket.line_machine}</td>
            <td>${ticket.issue_type}</td>
            <td>${ticket.created_at}</td>
            <td>${ticket.acknowledged_at}</td>
            <td>${ticket.closed_at}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}
