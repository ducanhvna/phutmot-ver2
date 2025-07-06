/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@refinedev/mui"],
  output: "standalone",
  webpack: (config) => {
    config.resolve.alias = {
      ...(config.resolve.alias || {}),
      // Forward Grid2 imports to Grid for compatibility with @refinedev/mui
      '@mui/material/Grid2': '@mui/material/Grid',
    };
    return config;
  },
};

module.exports = nextConfig;
