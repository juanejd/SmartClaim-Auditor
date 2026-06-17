import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "SmartClaim Auditor",
  description: "Consola de auditoría de reclamos de seguros asistida por IA",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className="h-full flex flex-col bg-background text-foreground antialiased">
        {children}
        <Toaster position="bottom-right" theme="dark" />
      </body>
    </html>
  );
}
