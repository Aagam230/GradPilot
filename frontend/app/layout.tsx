import "./globals.css";
import type { Metadata } from "next";
import { ThemeProvider } from "@/lib/theme";
import { AppStateProvider } from "@/lib/store";

export const metadata: Metadata = {
  title: "GradPilot — Your graduate application, understood.",
  description: "GradPilot reads your profile, understands your target programs, and shows you where you stand — with evidence.",
};

const themeInitScript = `
(function() {
  try {
    var t = localStorage.getItem('gradpilot.theme');
    var d = t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (d) document.documentElement.classList.add('dark');
  } catch (e) {}
})();
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="bg-canvas text-ink min-h-screen font-sans antialiased">
        <ThemeProvider>
          <AppStateProvider>{children}</AppStateProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
