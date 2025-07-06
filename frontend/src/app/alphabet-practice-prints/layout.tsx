"use client";

import React from "react";
import { ThemedLayoutV2 } from "@refinedev/mui";
import Header from "@components/header";

export default function Layout({ children }: React.PropsWithChildren) {
  return <ThemedLayoutV2 Header={Header}>{children}</ThemedLayoutV2>;
}
