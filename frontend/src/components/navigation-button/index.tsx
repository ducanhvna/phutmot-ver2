import React from "react";
import { Button } from "@mui/material";
import { useRouter } from "next/navigation";

interface NavigationButtonProps {
  text: string;
  backgroundColor: string;
  route?: string;
  textColor?: string;
  onClick?: () => void;
}

const NavigationButton: React.FC<NavigationButtonProps> = ({
  text,
  backgroundColor,
  route,
  textColor = "#fff",
  onClick,
}) => {
  const router = useRouter();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else if (route) {
      router.push(route);
    }
  };

  return (
    <Button
      variant={backgroundColor === "#f39801" ? "contained" : "outlined"}
      sx={{
        backgroundColor,
        height: "150px",
        fontSize: "26px",
        fontWeight: "bold",
        color: textColor,
        whiteSpace: "normal",
        lineHeight: 1.2,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        width: "100%"
      }}
      onClick={handleClick}
    >
      {text}
    </Button>
  );
};

export default NavigationButton;
