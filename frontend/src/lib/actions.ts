"use server";

import { db } from "@/server/db";
import { auth } from "./auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { inngest } from "@/inngest/client";

export async function queueSong() {
  const session = await auth.api.getSession({
    headers: await headers(),
  });
  if (!session) {
    redirect("/auth/sign-in");
  }
  const song = await db.song.create({
    data: {
      userId: session.user.id,
      title: "New Song",
      fullDescribedSong:
        "A funky and groovy hip hop rap song with a catchy beat",
    },
  });

  await inngest.send({
    name: "generate-song-event",
    data: {
      songId: song.id,
      userId: song.userId,
    },
  });
}
