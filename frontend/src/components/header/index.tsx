import { ColorModeContext } from "@contexts/color-mode";
import { useGetIdentity } from "@refinedev/core";
import { useContext } from "react";
import { HamburgerMenu } from "@refinedev/mui";

import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Avatar from "@mui/material/Avatar";
import { AppIcon } from "@components/app-icon";
import { User } from "@api/authApi";

type PropsHeader = {
  showSider?: boolean;
};

function Header({ showSider = false }: PropsHeader) {
  const { data: user } = useGetIdentity<User>();
  const { mode, setMode } = useContext(ColorModeContext);
  return (
    <AppBar
      style={{
        backgroundColor: "var(--color-white)",
      }}
      position="sticky"
    >
      <Toolbar>
        {showSider && (
          <Box style={{ color: "var(--color-green)" }}>
            <HamburgerMenu />
          </Box>
        )}
        <Box
          sx={{
            display: "flex",
            alignItems: "baseline",
            justifyContent: "center",
            gap: 1,
          }}
        >
          {!showSider && <AppIcon />}
          <Typography fontSize={27} fontWeight="400" color="textPrimary">
            まなびサポート
          </Typography>
        </Box>
        <Box sx={{ flexGrow: 1, display: { xs: "flex" } }} />
        <Box>
          {/* <IconButton
            onClick={() => setMode(mode === "light" ? "dark" : "light")}
          >
            {mode === "dark" ? (
              <LightModeOutlined style={{ color: "var(--color-yellow)" }} />
            ) : (
              <DarkModeOutlined style={{ color: "#fff" }} />
            )}
          </IconButton> */}
          <Box sx={{ display: "inline-block", ml: 2, mr: 2 }}>
            <Typography color="textPrimary">{user?.username}</Typography>
          </Box>
          <IconButton>
            <Avatar
              src={user?.avatar}
              alt={user?.name}
              sx={{
                width: 44,
                height: 44,
              }}
            />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
export default Header;
