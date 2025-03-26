import './InvoiceTable.css';

export default function InvoiceTable({ invoices }) {
  const getCellClass = (invoice) => {
    if (!invoice.found_percentage || invoice.found_percentage === 'Geen resultaat') {
      return 'gray';
    }

    const foundPercentage = parseFloat(invoice.found_percentage);
    const invoicePercentage = parseFloat(invoice.frm_perc);

    if (isNaN(foundPercentage) || isNaN(invoicePercentage)) {
      return 'gray';
    }
    return foundPercentage < invoicePercentage ? 'red' 
         : foundPercentage === invoicePercentage ? 'green' 
         : 'yellow';
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
              <th>Werkelijk percentage</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((invoice, index) => (
              <tr key={index}>
                <td>{invoice.master_title_description || 'N/A'}</td>
                <td>{invoice.play_week || 'N/A'}</td>
                <td>{invoice.frm_perc || 'N/A'}</td>
                <td className={getCellClass(invoice)}>
                  {invoice.found_percentage || 'Nog te controleren'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
