import {
  List,
  ListItem,
  ListItemText,
  Box,
  Typography,
  Badge,
  Divider,
  Button,
  IconButton,
  AppBar,
  Toolbar,
  Chip,
} from "@mui/material";
import { 
  NotificationsActive as NotificationIcon,
  CalendarMonth as CalendarIcon, 
  Lightbulb as LightbulbIcon,
  BarChart as StatsIcon,
  Search as SearchIcon,
  KeyboardArrowDown as ExpandMoreIcon,
} from '@mui/icons-material';
import React from "react";

type NotificationType = 'calendar' | 'learning' | 'stats' | 'test' | 'task';

type TypeNotifications = {
  id: number;
  content: string;
  time: string;
  read: boolean;
  type: NotificationType;
  actionText?: string;
  actionUrl?: string;
  isNew?: boolean;
}[];

type PropsNotifications = {
  notifications: TypeNotifications;
  expanded?: boolean;
  title?: string;
  showHeader?: boolean;
  onToggleExpand?: () => void;
  unreadCount?: number;
};

// Helper function to get icon based on notification type
const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case 'calendar':
      return <CalendarIcon sx={{ color: 'var(--color-blue)' }} />;
    case 'learning':
      return <LightbulbIcon sx={{ color: 'var(--color-orange)' }} />;
    case 'stats':
      return <StatsIcon sx={{ color: 'var(--color-purple)' }} />;
    case 'test':
      return <CalendarIcon sx={{ color: 'var(--color-green)' }} />;
    case 'task':
      return <NotificationIcon sx={{ color: 'var(--color-red)' }} />;
    default:
      return <NotificationIcon sx={{ color: 'var(--color-blue)' }} />;
  }
};

// Format date function to Japanese format
const formatDateJP = (dateString: string) => {
  const date = new Date(dateString);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

function Notifications({ 
  notifications, 
  expanded = false, 
  title = "まなびボード", 
  showHeader = false,
  onToggleExpand,
  unreadCount = 0
}: PropsNotifications) {
  return (
    <Box sx={{ width: "100%" }}>
      {showHeader && (
        <AppBar position="static" color="transparent" elevation={0} sx={{ 
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
          mb: 2
        }}>
          <Toolbar sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            py: 1
          }}>
            <Typography variant="h6" component="div" sx={{ 
              fontWeight: 'bold',
              fontSize: { xs: '1.1rem', sm: '1.3rem' },
              display: 'flex',
              alignItems: 'center',
              color: 'var(--color-blue)'
            }}>
              {title}
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton size="medium" sx={{ color: 'var(--color-blue)' }}>
                <CalendarIcon />
              </IconButton>
              <IconButton size="medium" sx={{ color: 'var(--color-blue)' }}>
                <LightbulbIcon />
              </IconButton>
              <IconButton size="medium" sx={{ color: 'var(--color-blue)' }}>
                <StatsIcon />
              </IconButton>
              <IconButton size="medium" sx={{ color: 'var(--color-blue)' }}>
                <SearchIcon />
              </IconButton>
              <IconButton 
                size="medium" 
                sx={{ color: 'var(--color-blue)' }}
              >
                <Badge badgeContent={unreadCount} color="error">
                  <NotificationIcon />
                </Badge>
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>
      )}
      
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between',
        alignItems: 'center',
        mb: 2,
        mt: showHeader ? 0 : 2
      }}>
        <Typography variant="h6" sx={{ 
          fontWeight: 'bold',
          fontSize: { xs: '1rem', sm: '1.1rem' },
          color: 'var(--color-blue)'
        }}>
          お知らせ
        </Typography>
        {onToggleExpand && (
          <Button 
            onClick={onToggleExpand}
            endIcon={<ExpandMoreIcon />}
            sx={{ 
              color: 'var(--color-blue)',
              fontWeight: 'medium',
              textTransform: 'none',
              fontSize: { xs: '0.8rem', sm: '0.9rem' }
            }}
          >
            {expanded ? '折りたたむ' : 'すべて表示'}
          </Button>
        )}
      </Box>

      <List sx={{ pb: 1, width: "100%" }}>
        {notifications
          .slice(0, expanded ? notifications.length : 2)
          .map((notification) => (
            <React.Fragment key={notification.id}>
              <ListItem
                alignItems="flex-start"
                sx={{
                  bgcolor: notification.read
                    ? "transparent"
                    : "rgba(3, 121, 217, 0.05)",
                  borderRadius: 2,
                  mb: 1.5,
                  p: { xs: 1.5, sm: 2 },
                  transition: "all 0.2s ease",
                  boxShadow: notification.read
                    ? "none"
                    : "0 2px 8px rgba(3, 121, 217, 0.1)",
                  "&:hover": {
                    bgcolor: notification.read
                      ? "rgba(3, 121, 217, 0.03)"
                      : "rgba(3, 121, 217, 0.08)",
                    transform: { sm: "translateX(4px)" },
                  },
                }}
              >
                <Box sx={{ mr: 2, mt: 0.5 }}>
                  {getNotificationIcon(notification.type)}
                </Box>
                <ListItemText
                  primary={
                    <Box
                      sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        mb: 0.5,
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography
                          variant="body2"
                          sx={{
                            color: 'text.secondary',
                            fontSize: { xs: '0.75rem', sm: '0.8rem' },
                          }}
                        >
                          {formatDateJP(notification.time)}
                        </Typography>
                        
                        {notification.isNew && (
                          <Chip 
                            label="NEW" 
                            color="error" 
                            size="small" 
                            sx={{ 
                              height: 20, 
                              fontSize: '0.65rem',
                              fontWeight: 'bold' 
                            }} 
                          />
                        )}
                      </Box>

                      {!notification.read && (
                        <Badge
                          color="error"
                          variant="dot"
                          sx={{
                            "& .MuiBadge-dot": {
                              height: 10,
                              width: 10,
                              borderRadius: "50%",
                              boxShadow: "0 0 0 2px white",
                            },
                          }}
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <>
                      <Typography
                        variant="body1"
                        sx={{
                          fontWeight: !notification.read ? "bold" : "medium",
                          color: !notification.read
                            ? "var(--color-blue)"
                            : "inherit",
                          fontSize: { xs: "0.9rem", sm: "1rem" },
                          mb: 1.5,
                          lineHeight: 1.4,
                        }}
                      >
                        {notification.content}
                      </Typography>
                      
                      {notification.actionText && (
                        <Button
                          variant="text"
                          size="small"
                          href={notification.actionUrl || '#'}
                          sx={{
                            color: 'var(--color-blue)',
                            fontWeight: 'bold',
                            textTransform: 'none',
                            fontSize: '0.8rem',
                            p: '3px 8px',
                            minWidth: 'unset',
                            ml: -1,
                            borderRadius: 1,
                            '&:hover': {
                              backgroundColor: 'rgba(3, 121, 217, 0.1)',
                            }
                          }}
                        >
                          {notification.actionText}
                        </Button>
                      )}
                    </>
                  }
                />
              </ListItem>
              <Divider
                component="li"
                sx={{
                  ml: 0,
                  borderColor: "rgba(0,0,0,0.06)",
                  mb: 2,
                }}
              />
            </React.Fragment>
          ))}
      </List>
      
      {notifications.length > 2 && !expanded && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1, mb: 2 }}>
          <Button 
            onClick={onToggleExpand}
            variant="outlined"
            size="small"
            endIcon={<ExpandMoreIcon />}
            sx={{ 
              borderRadius: 4,
              color: 'var(--color-blue)',
              borderColor: 'var(--color-blue)',
              textTransform: 'none',
              fontSize: '0.8rem',
              '&:hover': {
                backgroundColor: 'rgba(3, 121, 217, 0.05)',
                borderColor: 'var(--color-blue)',
              }
            }}
          >
            すべての通知を表示
          </Button>
        </Box>
      )}
    </Box>
  );
}

export default Notifications;
