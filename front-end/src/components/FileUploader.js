import { useState, useEffect } from "react";
import { UploadCloud } from "lucide-react";
import "./FileUploader.css";

export default function FileUploader({ onFileUploadSuccess }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  useEffect(() => {
    // Als er een bestand is geselecteerd, wordt automatisch geüpload
    if (file) {
      handleFileUpload();
    }
  }, [file]); // Dit wordt uitgevoerd elke keer dat de 'file' verandert

  const handleFileUpload = async () => {
    if (!file) {
      return; // Geen bestand, geen upload
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        onFileUploadSuccess(data); // Gegevens naar parent component sturen
      } else {
        alert("Er is iets misgegaan bij het uploaden.");
      }
    } catch (error) {
      console.error("Error tijdens bestand upload:", error);
      alert("Er is iets misgegaan bij het uploaden.");
    }
  };

  return (
    <div className="file-uploader-container">
      <div className="file-upload-wrapper">
        <label className="file-upload-label">
          <UploadCloud size={20} />
          <span>Bestand kiezen</span>
          <input type="file" className="hidden" onChange={handleFileChange} />
        </label>
        {file && <p className="file-name">{file.name}</p>}
      </div>
    </div>
  );
}
