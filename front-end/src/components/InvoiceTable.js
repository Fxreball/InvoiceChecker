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

  const getBoxofficeCellClass = (invoice) => {
    if (!invoice.found_boxoffice || invoice.found_boxoffice === 'Niet gevonden') {
      return 'gray';
    }

    const foundBoxoffice = parseFloat(invoice.found_boxoffice);
    const invoiceBoxoffice = parseFloat(invoice.boxoffice);

    if (isNaN(foundBoxoffice) || isNaN(invoiceBoxoffice)) {
      return 'gray';
    }

    return foundBoxoffice < invoiceBoxoffice ? 'yellow' 
         : foundBoxoffice === invoiceBoxoffice ? 'green' 
         : 'red';
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
              <th>Factuur Box office</th>
              <th>Werkelijk Box office</th>
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
                <td>{invoice.boxoffice || 'N/A'}</td>
                <td className={getBoxofficeCellClass(invoice)}>
                  {invoice.found_boxoffice || 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
