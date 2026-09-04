import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "PAIMANA Intelligence Platform | MoSPI",
  description:
    "Project Intelligence & Early Warning System for monitoring large infrastructure projects — Ministry of Statistics and Programme Implementation",
  keywords: ["PAIMANA", "MoSPI", "infrastructure monitoring", "project tracking", "India"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-slate-950 text-slate-100 min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
