import type { NextConfig } from "next";

// Browser requests stay on the AIMN origin; Next.js proxies to the private API.
const apiOrigin = (process.env.AIMN_INTERNAL_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const nextConfig: NextConfig = {
  poweredByHeader: false,
  async rewrites() {
    return [{ source: "/api/:path*", destination: apiOrigin + "/api/:path*" }];
  },
};
export default nextConfig;
