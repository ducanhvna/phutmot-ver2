"use client";

import LayoutMui from "@components/layouts";
import React from "react";

export default function Layout({ children }: React.PropsWithChildren) {
  return <LayoutMui showSider={false}>{children}</LayoutMui>;
}
