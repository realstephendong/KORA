import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'c.animaapp.com',
        port: '',
        pathname: '/7Y4W5hAe/img/**',
      },
    ],
  },
};

export default nextConfig;
