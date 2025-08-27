import { useState } from "react";
import './index.css';
import Header from './components/Header';
import Footer from './components/Footer';
import FileUploaderInvoice from './components/FileUploaderInvoice';
import FileUploaderPercentage from './components/FileUploaderPercentage';
import FileUploaderMaccs from './components/FileUploaderMaccs';
import InvoiceTable from './components/InvoiceTable';
import CheckButton from './components/CheckButton';

function App() {
  const [invoices, setInvoices] = useState([]);

  const handleFileUploadSuccess = (data) => {
    setInvoices(data); // originele invoices
  };

  const handlePercentageUploadSuccess = (data) => {
    console.log("Percentage upload succesvol:", data);
  };

  const handleMaccsUploadSuccess = (data) => {
    console.log("Recettes upload succesvol:", data);
  };

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
        // Voeg found_percentage en found_boxoffice toe aan invoices
        setInvoices(prevInvoices =>
          prevInvoices.map((invoice, index) => {
            const foundData = data[index];
            return {
              ...invoice,
              found_percentage: foundData?.found_percentage ?? 'Niet gevonden',
              found_boxoffice: foundData?.found_boxoffice ?? 'Niet gevonden',
            };
          })
        );
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
