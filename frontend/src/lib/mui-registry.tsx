'use client';

import * as React from 'react';
import createCache from '@emotion/cache';
import { useServerInsertedHTML } from 'next/navigation';
import { CacheProvider } from '@emotion/react';
import { useState } from 'react';

// This implementation is from the official MUI example for Next.js App Router
// https://mui.com/material-ui/guides/next-js-app-router/
export default function MuiRegistry({ children }: { children: React.ReactNode }) {
  const [cache] = useState(() => {
    const cache = createCache({
      key: 'mui',
      prepend: true, // This ensures emotion styles are loaded first
      stylisPlugins: [],
    });
    cache.compat = true;
    return cache;
  });

  useServerInsertedHTML(() => {
    // This ensures the emotion styles are collected and inserted correctly during SSR
    const entries = Object.entries(cache.inserted);
    if (entries.length === 0) return null;

    const names = entries.map(([name]) => name);
    const styles = entries.map(([, style]) => style).join(' ');

    return (
      <style
        key={cache.key}
        data-emotion={`${cache.key} ${names.join(' ')}`}
        dangerouslySetInnerHTML={{
          __html: styles,
        }}
      />
    );
  });

  return <CacheProvider value={cache}>{children}</CacheProvider>;
}
