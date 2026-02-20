import type { Metadata } from "next";
import Sidebar from "@/components/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "OpenClaw Dashboard",
  description: "Multi-agent product team dashboard powered by OpenClaw",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <Sidebar />
        <main className="ml-56 min-h-screen p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
