import React from "react";
import { ThemedLayoutV2 } from "@refinedev/mui";

import { authProviderServer } from "@providers/auth-provider/auth-provider.server";
import { redirect } from "next/navigation";
import Header from "@components/header";

export default async function Layout({ children }: React.PropsWithChildren) {
  const authData = await getAuthData();

  if (!authData.authenticated) {
    return redirect(authData?.redirectTo || "/login");
  }

  return <ThemedLayoutV2 Header={Header}>{children}</ThemedLayoutV2>;
}

async function getAuthData() {
  const { authenticated, redirectTo } = await authProviderServer.check();

  return {
    authenticated,
    redirectTo,
  };
}
