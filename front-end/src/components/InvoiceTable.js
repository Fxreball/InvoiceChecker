export default function InvoiceTable({ invoices }) {
    console.log(invoices); // Controleer of de data hier zichtbaar is
  
    return (
      <div>
        <h2>Facturen</h2>
        {invoices.length === 0 ? (
          <p>Geen facturen beschikbaar.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Percentage</th>
                <th>Titel</th>
                <th>Speelweek</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice, index) => (
                <tr key={index}>
                  <td>{invoice.frm_perc}</td>
                  <td>{invoice.master_title_description}</td>
                  <td>{invoice.play_week}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    );
  }
  