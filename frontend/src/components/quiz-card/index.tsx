import React from "react";
import { Card, CardContent, CardHeader } from "@mui/material";

interface QuizCardProps {
  title: string;
  content: React.ReactNode;
  backgroundColor?: string;
}

const QuizCard: React.FC<QuizCardProps> = ({
  title,
  content,
  backgroundColor = "#17a098",
}) => {
  return (
    <Card sx={{ height: "100%" }}>
      <CardHeader
        title={title}
        sx={{ backgroundColor, color: "white" }}
      />
      <CardContent>
        {content}
      </CardContent>
    </Card>
  );
};

export default QuizCard;
