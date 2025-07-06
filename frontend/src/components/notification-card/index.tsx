import React from "react";
import {
  Card,
  CardHeader,
  CardContent,
  List,
  ListItem,
  ListItemText
} from "@mui/material";

interface NotificationCardProps {
  title: string;
  notifications: string[];
  backgroundColor?: string;
}

const NotificationCard: React.FC<NotificationCardProps> = ({
  title,
  notifications,
  backgroundColor = "#17a098",
}) => {
  return (
    <Card sx={{ height: "100%" }}>
      <CardHeader
        title={title}
        sx={{
          backgroundColor,
          color: "white",
        }}
      />
      <CardContent>
        <List>
          {notifications.map((item, index) => (
            <ListItem key={index}>
              <ListItemText primary={item} />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default NotificationCard;
