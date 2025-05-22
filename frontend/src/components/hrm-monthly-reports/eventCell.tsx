import React from "react";
import { Button } from "antd";

const EventCell: React.FC<{ day: number; employeeId: number; shift: string; onClick: () => void }> = ({ day, shift, onClick }) => {
  return (
    <Button type="text" onClick={onClick}>
      {shift || ""}
    </Button>
  );
};

export default EventCell;
