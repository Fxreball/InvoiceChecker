import { useState } from "react";
import './index.css';
import Header from './components/Header';
import Footer from './components/Footer';
import FileUploaderInvoice from './components/FileUploaderInvoice';
import FileUploaderPercentage from './components/FileUploaderPercentage';
import FileUploaderMaccs from './components/FileUploaderMaccs'; // Toegevoegd: uploader voor recettes
import InvoiceTable from './components/InvoiceTable';
import CheckButton from './components/CheckButton';

function App() {
  const [invoices, setInvoices] = useState([]);

  const handleFileUploadSuccess = (data) => {
    setInvoices(data);
  };

  const handlePercentageUploadSuccess = (data) => {
    console.log("Percentage upload succesvol:", data);
  };

  const handleMaccsUploadSuccess = (data) => {
    console.log("Recettes upload succesvol:", data);
  };

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
              found_boxoffice: foundData?.boxoffice || 'Niet gevonden', // Hier voeg je de gevonden boxoffice toe
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
      <Header />
      <div className="content">
        <FileUploaderInvoice onFileUploadSuccess={handleFileUploadSuccess} />
        <FileUploaderPercentage onFileUploadSuccess={handlePercentageUploadSuccess} />
        <FileUploaderMaccs onFileUploadSuccess={handleMaccsUploadSuccess} />
        <CheckButton onSearch={handleSearch} />
        <InvoiceTable invoices={invoices} />
      </div>
      <Footer />
    </div>
  );
}

export default App;
