export default function InvoiceTable({ invoices }) {
    return (
      <div>
        <h2>Facturen</h2>
        {invoices.length === 0 ? (
          <p>Geen facturen beschikbaar.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Titel</th>
                <th>Speelweek</th>
                <th>Percentage</th>
                <th>Gevonden Percentage</th> {/* Nieuwe kolom */}
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice, index) => (
                <tr key={index}>
                  <td>{invoice.master_title_description}</td>
                  <td>{invoice.play_week}</td>
                  <td>{invoice.frm_perc}</td>
                  <td>{invoice.found_percentage || 'N/A'}</td> {/* Nieuwe kolom */}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  }
  