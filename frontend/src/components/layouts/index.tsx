"use client";

import React from "react";
import { ThemedLayoutV2, ThemedSiderV2 } from "@refinedev/mui";
import Header from "@components/header";
import { AppIcon } from "@components/app-icon";
import { Box } from "@mui/material";

interface LayoutMuiProps extends React.PropsWithChildren {
  showSider?: boolean;
}

export default function LayoutMui({
  children,
  showSider = true,
}: LayoutMuiProps) {
  return (
    <ThemedLayoutV2
      Title={() => (
        <Box className="p-2">
          <AppIcon />
        </Box>
      )}
      Header={() => <Header showSider={showSider} />}
      Sider={
        showSider
          ? () => (
              <ThemedSiderV2
                Title={({ collapsed }) => <AppIcon />}
                render={({ items, logout, collapsed }) => (
                  <>
                    {/* Apply custom styling to each item */}
                    <Box className="custom-sider-items">{items}</Box>
                    {logout}
                  </>
                )}
              />
            )
          : () => null
      }
      childrenBoxProps={!showSider ? { sx: { p: 0 } } : undefined}
    >
      {children}
    </ThemedLayoutV2>
  );
}
