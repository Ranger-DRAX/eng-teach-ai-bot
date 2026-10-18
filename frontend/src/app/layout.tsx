import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "English Learning Chatbot",
  description: "Safe, interactive English learning chatbot for children under 7",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased bg-slate-50 text-slate-800">
        {children}
      </body>
    </html>
  );
}
