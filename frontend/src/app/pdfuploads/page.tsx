"use client";

import { Card, CardContent, CardHeader, Box } from "@mui/material";
import React from "react";

const dummyPDFs = [
  {
    id: 1,
    title: "Hướng dẫn Next.js",
    preview: "/sample1.pdf",
  },
  {
    id: 2,
    title: "Báo cáo Công Nghệ 2025",
    preview: "/sample2.pdf",
  },
  {
    id: 3,
    title: "Thiết kế hệ thống",
    preview: "/sample3.pdf",
  },
  {
    id: 4,
    title: "Lập trình TypeScript",
    preview: "/sample4.pdf",
  },
];

export default function QuestionPDFPostList() {
  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, p: 2 }}>
      {dummyPDFs.map((pdf) => (
        <Box key={pdf.id} sx={{ width: { xs: '100%', sm: '45%', md: '30%', lg: '22%' } }}>
          <Card variant="outlined">
            <CardHeader title={pdf.title} />
            <CardContent>
              <iframe
                src={pdf.preview}
                width="100%"
                height="250px"
                style={{ border: "none" }}
              />
            </CardContent>
          </Card>
        </Box>
      ))}
    </Box>
  );
}
