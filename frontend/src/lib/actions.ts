"use server";

import { db } from "@/server/db";
import { auth } from "./auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { inngest } from "@/inngest/client";
import { revalidatePath } from "next/cache";

export interface GenerateRequest {
  prompt?: string;
  lyrics?: string;
  fullDescribedSong?: string;
  describedLyrics?: string;
  instrumental?: boolean;
}

export async function generateNewSong(generatedRequest: GenerateRequest) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) redirect("/auth/sign-in");
  await queueSong(generatedRequest, 7.5, session.user.id);
  await queueSong(generatedRequest, 15, session.user.id);

  revalidatePath("/create");
}
export async function queueSong(
  generatedRequest: GenerateRequest,
  guidanceScale: number,
  userId: string,
) {
  let title = "Untitled Song";
  if (generatedRequest.describedLyrics) {
    title = generatedRequest.describedLyrics;
  } else if (generatedRequest.fullDescribedSong) {
    title = generatedRequest.fullDescribedSong;
  }
  title = title.charAt(0).toUpperCase() + title.slice(1);

  const song = await db.song.create({
    data: {
      userId: userId,
      title: title,
      prompt: generatedRequest.prompt ?? undefined,
      lyrics: generatedRequest.lyrics ?? undefined,
      describedLyrics: generatedRequest.describedLyrics ?? undefined,
      fullDescribedSong: generatedRequest.fullDescribedSong ?? undefined,
      instrumental: generatedRequest.instrumental,
      guidanceScale: guidanceScale,
      audioDuration: 180,
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
