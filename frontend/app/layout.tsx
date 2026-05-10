import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Assistant IAM Intelligent",
  description: "Base du projet assistant IAM conscience numerique",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}

