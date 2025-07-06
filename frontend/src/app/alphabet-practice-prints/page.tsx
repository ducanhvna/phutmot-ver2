"use client";

import React from "react";
import { Typography, Divider } from "@mui/material";
import CardPdf from "@components/card-pdf";
import ModalPdf from "@components/modal-pdf";

const dummyItems = Array.from({ length: 30 }).map((_, i) => ({
  id: i + 1,
  src: `/images/sample-${(i % 8) + 1}.png`,
  title: `学習ノート ${i + 1}`,
  pdfUrl: "https://pdfobject.com/pdf/sample.pdf",
}));

export default function AlphabetPracticePrintPage() {
  const [selectedPdf, setSelectedPdf] = React.useState<string | null>(null);

  // Function to handle PDF click
  const handlePdfClick = (pdfUrl: string) => {
    setSelectedPdf(pdfUrl);
  };

  // Function to close PDF preview
  const handleClosePdf = () => {
    setSelectedPdf(null);
  };

  return (
    <div style={{ padding: 20 }}>
      <Typography variant="h2">アルファベット練習プリント</Typography>
      <Typography variant="h3">教育支援ツールの一部として設計</Typography>

      <Typography variant="body1">
        このページでは、教師が英語の授業をサポートするための罫線ノートを提供します。
        ノートは学習者が文字を綺麗に書けるようにデザインされ、使いやすいフォーマットを備えています。
      </Typography>

      <Divider />

      <CardPdf items={dummyItems} onPdfClick={handlePdfClick} />
      {/* PDF Preview Modal */}
      <ModalPdf selectedPdf={selectedPdf} onClose={handleClosePdf} />
    </div>
  );
}
