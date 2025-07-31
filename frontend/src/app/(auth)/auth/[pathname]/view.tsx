"use client";

import { Button } from "@/components/ui/button";
import { AuthCard } from "@daveyplate/better-auth-ui";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

export function AuthView({ pathname }: { pathname: string }) {
  const router = useRouter();
  return (
    <main className="container flex grow flex-col items-center justify-center gap-3 self-center p-4 md:p-6">
      {["settings", "security"].includes(pathname) && (
        <Button
          onClick={() => router.back()}
          className="self-start"
          variant={"outline"}
        >
          <ArrowLeft />
          Back
        </Button>
      )}
      <AuthCard pathname={pathname} />
    </main>
  );
}
