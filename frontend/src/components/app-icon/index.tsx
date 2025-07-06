"use client";

import Image from "next/image";
import React from "react";
export const AppIcon: React.FC = () => {
  return <Image width={190} height={50} src="/images/logo.png" alt="Logo" className="px-0.5"/>;
};
