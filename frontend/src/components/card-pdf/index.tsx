import React from "react";
import Image from "next/image";

export interface CardPdfItem {
  id: number;
  src: string;
  title: string;
  pdfUrl: string;
}

interface CardPdfProps {
  items: CardPdfItem[];
  onPdfClick: (pdfUrl: string) => void;
}

const CardPdf: React.FC<CardPdfProps> = ({ items, onPdfClick }) => (
  <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
    {items.map((item) => (
      <div
        key={item.id}
        className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer flex flex-col items-center text-center p-4"
        onClick={() => onPdfClick(item.pdfUrl)}
      >
        <div className="relative mb-3 overflow-hidden rounded-md w-[220px] h-[300px] flex items-center justify-center bg-gray-100">
          <Image
            src={item.src}
            alt={item.title}
            width={220}
            height={300}
            className="object-cover w-full h-full"
          />
        </div>
        <div className="text-lg font-semibold text-gray-800 mb-0 truncate w-full" title={item.title}>
          {item.title}
        </div>
        <div className="text-base text-blue-600 mt-1 underline">
          プレビュー表示
        </div>
      </div>
    ))}
  </div>
);

export default CardPdf;
