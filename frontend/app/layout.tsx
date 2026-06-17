import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import { Toaster } from "@/components/ui/sonner";
import { navLabels } from "@/lib/labels";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "SmartClaim Auditor",
  description: "Consola de auditoría de reclamos de seguros asistida por ORION",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={`${inter.variable} h-full`}>
      <body className="h-full flex flex-col bg-background text-foreground antialiased">
        <header className="shrink-0 border-b border-border bg-card/80 backdrop-blur-sm z-10">
          <div className="px-6 h-12 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Link
                href="/"
                className="font-display text-base text-foreground leading-tight hover:text-primary transition-colors"
              >
                {navLabels.appTitle}
              </Link>
              <span className="hidden sm:block font-mono text-xs text-muted-foreground">
                {navLabels.appSubtitle}
              </span>
            </div>
            <nav className="flex items-center gap-1">
              <Link
                href="/documentos"
                className="font-mono text-xs text-muted-foreground/95 hover:text-primary transition-colors px-3 py-1.5 rounded-md hover:bg-muted/40"
              >
                {navLabels.documents}
              </Link>
              <Link
                href="/clausulas"
                className="font-mono text-xs text-muted-foreground hover:text-primary transition-colors px-3 py-1.5 rounded-md hover:bg-muted/40"
              >
                {navLabels.clauses}
              </Link>
            </nav>
          </div>
        </header>
        <div className="flex-1 min-h-0 flex flex-col">{children}</div>
        <Toaster position="bottom-right" theme="dark" />
      </body>
    </html>
  );
}
