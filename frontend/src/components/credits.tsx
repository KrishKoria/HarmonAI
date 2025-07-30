"use server";

import { auth } from "@/lib/auth";
import { db } from "@/server/db";
import { headers } from "next/headers";

export async function Credits() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) return null;

  const user = await db.user.findUniqueOrThrow({
    where: { id: session.user.id },
    select: { credits: true },
  });

  return (
    <>
      <p className="font-semibold">{user.credits}</p>
      <p className="text-muted-foreground">Credits</p>
    </>
  );
}
