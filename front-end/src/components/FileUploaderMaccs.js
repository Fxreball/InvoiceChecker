import { useState, useEffect, useCallback } from "react";
import { UploadCloud } from "lucide-react";
import "./FileUploader.css";

export default function RecetteUploader({ onFileUploadSuccess }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleFileUpload = useCallback(async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("https://api.owencoenraad.nl/upload-recettes", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        onFileUploadSuccess(data);
      } else {
        alert("Er is iets misgegaan bij het uploaden van het recettes-bestand.");
      }
    } catch (error) {
      console.error("Upload fout:", error);
      alert("Er is een fout opgetreden bij het uploaden.");
    }
  }, [file, onFileUploadSuccess]);

  useEffect(() => {
    if (file) {
      handleFileUpload();
    }
  }, [file, handleFileUpload]);

  return (
    <div className="file-uploader-container">
      <div className="file-upload-wrapper">
        <label className="file-upload-label">
          <UploadCloud size={20} />
          <span>MaccsBox</span>
          <input type="file" className="hidden" onChange={handleFileChange} />
        </label>
        {file && <p className="file-name">{file.name}</p>}
      </div>
    </div>
  );
}
