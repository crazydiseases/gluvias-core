"use client";
import React, { useState } from "react";

export default function VaultUploader() {
  const [uploading, setUploading] = useState(false);
  const [status, setStatus] = useState("");

  const handleUpload = async (e: any) => {
    const file = e.target.files ? e.target.files : null;
    if (!file) return;

    setUploading(true);
    setStatus("Archiving...");

    try {
      const res = await fetch("/api/vault/sign", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fileName: file.name, contentType: file.type }),
      });
      
      const { url } = await res.json();

      await fetch(url, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type },
      });

      setStatus("Success!");
    } catch (err) {
      setStatus("Error");
    } finally {
      setUploading(false);
      setTimeout(() => setStatus(""), 3000);
    }
  };

  return (
    <div style={{ marginTop: "20px", padding: "10px", border: "1px dashed #333", borderRadius: "8px", textAlign: "center" }}>
      <p style={{ fontSize: "0.7rem", color: "#888" }}>{status || "Master Archive"}</p>
      <input type="file" onChange={handleUpload} disabled={uploading} style={{ display: "none" }} id="v-up" />
      <label htmlFor="v-up" style={{ cursor: "pointer", color: "#3b82f6", fontSize: "0.8rem" }}>
        {uploading ? "Processing..." : "+ Upload Book"}
      </label>
    </div>
  );
}