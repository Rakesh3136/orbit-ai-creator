import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AIMN | Media Network Command Center",
  description: "The command center for your autonomous AI media network.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
