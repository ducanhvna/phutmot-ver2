import React from "react";

interface ModalPdfProps {
  selectedPdf: string | null;
  onClose: () => void;
}

const ModalPdf: React.FC<ModalPdfProps> = ({ selectedPdf, onClose }) => {
  if (!selectedPdf) return null;
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        backgroundColor: "rgba(0,0,0,0.7)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          backgroundColor: "white",
          borderRadius: "10px",
          width: "90%",
          height: "90%",
          padding: "20px",
          position: "relative",
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            right: "15px",
            top: "15px",
            border: "none",
            background: "#f5f5f5",
            width: "30px",
            height: "30px",
            borderRadius: "50%",
            cursor: "pointer",
            fontSize: "16px",
            fontWeight: "bold",
            zIndex: 10,
          }}
        >
          ✕
        </button>
        <iframe
          src={selectedPdf}
          style={{
            width: "100%",
            height: "100%",
            border: "none",
          }}
          title="PDF Preview"
        />
      </div>
    </div>
  );
};

export default ModalPdf;
