import { useState } from "react";
import FileUploader from './components/FileUploader';
import InvoiceTable from './components/InvoiceTable';

function App() {
  const [invoices, setInvoices] = useState([]); // Opslaan van factuurgegevens

  const handleFileUploadSuccess = (data) => {
    setInvoices(data); // Zet de geüploade gegevens in de state
  };

  return (
    <div>
      <FileUploader onFileUploadSuccess={handleFileUploadSuccess} />
      <InvoiceTable invoices={invoices} /> {/* Geef de facturen door */}
    </div>
  );
}

export default App;
