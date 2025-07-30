import { AppSidebar } from "@/components/app-sidebar";
import DashboardBreadcrumb from "@/components/dashboardBreadcrumb";
import { Providers, ThemeProvider } from "@/components/providers";
import { ModeToggle } from "@/components/theme-toggle";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/sonner";
import "@/styles/globals.css";

import { type Metadata } from "next";
import { Geist } from "next/font/google";

export const metadata: Metadata = {
  title: "HarmonAI",
  description: "A platform for Composing and generating AI Music",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geist.variable}`} suppressHydrationWarning>
      <body className="bg-background flex min-h-svh flex-col antialiased">
        <Providers>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <SidebarProvider>
              <AppSidebar />
              <SidebarInset className="flex h-screen flex-col">
                <header className="bg-background sticky-top z-10 flex justify-between border-b px-4 py-2">
                  <div className="flex shrink-0 grow items-center gap-2">
                    <SidebarTrigger className="-ml-1" />
                    <Separator
                      orientation={"vertical"}
                      className="mr-2 data-[orientation=vertical]:h-4"
                    />
                    <DashboardBreadcrumb />
                  </div>
                  <ModeToggle />
                </header>
                <main className="flex-1 overflow-y-auto">{children}</main>
              </SidebarInset>
            </SidebarProvider>
            <Toaster />
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  );
}
