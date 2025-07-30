import { auth } from "@/lib/auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";

export default async function HomePage() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  if (!session) {
    redirect("/auth/sign-in");
  }
  return (
    <main className="container flex grow flex-col items-center justify-center gap-3 self-center p-4 md:p-6">
      <h1 className="text-4xl font-bold">Welcome to HarmonAI</h1>
      <p className="text-lg">
        A platform for Composing and generating AI Music
      </p>
      dashboard
    </main>
  );
}
