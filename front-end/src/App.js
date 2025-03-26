import { useState } from "react";
import Header from './components/Header';
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
      const response = await fetch("https://api.owencoenraad.nl/search", {
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
              found_percentage: foundData?.percentage || 'Niet gevonden',
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
      <Header></Header>
      <FileUploaderInvoice onFileUploadSuccess={handleFileUploadSuccess} />
      <FileUploaderPercentage onFileUploadSuccess={handlePercentageUploadSuccess} />
      <CheckButton onSearch={handleSearch} />
      <InvoiceTable invoices={invoices} />
    </div>
  );
}

export default App;