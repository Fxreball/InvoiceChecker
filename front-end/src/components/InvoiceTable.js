import './InvoiceTable.css';

export default function InvoiceTable({ invoices }) {
  const getCellClass = (invoice) => {
    if (invoice.found_percentage === 'Geen resultaat') {
      return 'gray';
    }
    const foundPercentage = parseFloat(invoice.found_percentage);
    const invoicePercentage = parseFloat(invoice.frm_perc);

    if (isNaN(foundPercentage) || isNaN(invoicePercentage)) {
      return 'gray';
    }

    if (foundPercentage < invoicePercentage) {
      return 'red';
    } else if (foundPercentage === invoicePercentage) {
      return 'green';
    } else if (foundPercentage > invoicePercentage) {
      return 'yellow';
    }
  };

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
              <th>Factuur percentage</th>
              <th>Werkelijk percentage</th> {/* Nieuwe kolom */}
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice, index) => (
              <tr key={index}>
                <td>{invoice.master_title_description}</td>
                <td>{invoice.play_week}</td>
                <td>{invoice.frm_perc}</td>
                <td className={getCellClass(invoice)}>
                  {invoice.found_percentage || 'N/A'}
                </td> {/* Nieuwe kolom */}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}