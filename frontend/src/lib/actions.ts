"use server";

import { db } from "@/server/db";
import { auth } from "./auth";
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { inngest } from "@/inngest/client";
import { revalidatePath } from "next/cache";
import { env } from "@/env";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

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

export async function getPlayUrl(songId: string) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) redirect("/auth/sign-in");

  const song = await db.song.findUniqueOrThrow({
    where: {
      id: songId,
      OR: [{ userId: session.user.id }, { published: true }],
      s3Key: {
        not: null,
      },
    },
    select: {
      s3Key: true,
    },
  });

  await db.song.update({
    where: {
      id: songId,
    },
    data: {
      listenCount: {
        increment: 1,
      },
    },
  });

  return await getPresignedUrl(song.s3Key!);
}

export async function getPresignedUrl(key: string) {
  const s3Client = new S3Client({
    region: env.AWS_REGION,
    forcePathStyle: false,
    credentials: {
      accessKeyId: env.AWS_ACCESS_KEY_ID,
      secretAccessKey: env.AWS_SECRET_ACCESS_KEY,
    },
    endpoint: "https://t3.storage.dev",
  });

  const command = new GetObjectCommand({
    Bucket: env.S3_BUCKET_NAME,
    Key: key,
  });

  return await getSignedUrl(s3Client, command, {
    expiresIn: 3600,
  });
}

export async function setPublishedStatus(songId: string, published: boolean) {
  const session = await auth.api.getSession({
    headers: await headers(),
  });

  if (!session) redirect("/auth/sign-in");

  await db.song.update({
    where: {
      id: songId,
      userId: session.user.id,
    },
    data: {
      published,
    },
  });

  revalidatePath("/create");
}
