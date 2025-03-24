import { useState } from "react";
import FileUploaderInvoice from './components/FileUploaderInvoice';
import FileUploaderPercentage from './components/FileUploaderPercentage'; // Nieuwe component voor percentages
import InvoiceTable from './components/InvoiceTable';
import CheckButton from './components/CheckButton';  // Nieuwe knop component

function App() {
  const [invoices, setInvoices] = useState([]); // Opslaan van factuurgegevens

  // Functie voor bestand uploaden
  const handleFileUploadSuccess = (data) => {
    setInvoices(data); // Zet de geüploade gegevens in de state
  };

  // Functie voor percentages uploaden
  const handlePercentageUploadSuccess = (data) => {
    console.log("Percentage upload succesvol:", data); // Log de upload voor controle
  };

  // Functie voor zoekactie na klikken op de "Controleer" knop
  const handleSearch = async () => {
    try {
      const response = await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(invoices),
      });

      if (response.ok) {
        const data = await response.json();
        setInvoices(prevInvoices => {
          return prevInvoices.map((invoice, index) => {
            const foundData = data[index];
            return {
              ...invoice,
              found_percentage: foundData?.percentage || 'Geen resultaat',
            };
          });
        });
      } else {
        alert("Er is iets misgegaan bij het zoeken.");
      }
    } catch (error) {
      console.error("Error tijdens zoekactie:", error);
      alert("Er is iets misgegaan bij het zoeken.");
    }
  };

  return (
    <div>
      <FileUploaderInvoice onFileUploadSuccess={handleFileUploadSuccess} />
      <FileUploaderPercentage onFileUploadSuccess={handlePercentageUploadSuccess} /> {/* Nieuwe component voor percentages */}
      <InvoiceTable invoices={invoices} />
      <CheckButton onSearch={handleSearch} /> {/* De zoekknop */}
    </div>
  );
}

export default App;