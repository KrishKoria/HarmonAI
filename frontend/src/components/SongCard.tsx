"use client";

import { getPlayUrl, toggleLikeSong } from "@/lib/actions";
import { cn } from "@/lib/utils";
import { usePlayerStore } from "@/store/usePlayer";
import type { Category, Like, Song } from "@prisma/client";
import { Heart, Loader2, Music, Play } from "lucide-react";
import Image from "next/image";
import { useState, useTransition } from "react";
import { Button } from "./ui/button";

type SongWithRelation = Song & {
  user: { name: string | null };
  _count: {
    likes: number;
  };
  categories: Category[];
  thumbnailUrl?: string | null;
  likes?: Like[];
};

export function SongCard({ song }: { song: SongWithRelation }) {
  const [isLoading, startTransition] = useTransition();
  const setTrack = usePlayerStore((state) => state.setTrack);
  const [isLiked, setIsLiked] = useState(
    song.likes ? song.likes.length > 0 : false,
  );
  const [likesCount, setLikesCount] = useState(song._count.likes);

  const handlePlay = () => {
    startTransition(async () => {
      const playUrl = await getPlayUrl(song.id);

      setTrack({
        currentTrackId: song.id,
        title: song.title,
        url: playUrl,
        artwork: song.thumbnailUrl,
        prompt: song.prompt,
        createdBy: song.user.name,
      });
    });
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.stopPropagation();

    setIsLiked(!isLiked);
    setLikesCount(isLiked ? likesCount - 1 : likesCount + 1);

    await toggleLikeSong(song.id);
  };

  return (
    <div>
      <div onClick={handlePlay} className="cursor-pointer">
        <div className="group relative aspect-square w-full overflow-hidden rounded-md bg-gray-200 group-hover:opacity-75">
          {song.thumbnailUrl ? (
            <Image
              className="h-full w-full object-cover object-center"
              src={song.thumbnailUrl}
              alt={song.title}
              fill
            />
          ) : (
            <div className="bg-muted flex h-full w-full items-center justify-center">
              <Music className="text-muted-foreground h-12 w-12" />
            </div>
          )}

          <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 transition-opacity group-hover:opacity-100">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-black/60 transition-transform group-hover:scale-105">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin text-white" />
              ) : (
                <Play className="h-6 w-6 fill-white text-white" />
              )}
            </div>
          </div>
        </div>

        <h3 className="dark:text-primary text-md mt-2 truncate font-medium text-gray-900">
          {song.title}
        </h3>

        <p className="text-sm text-gray-500 dark:text-gray-300">
          {song.user.name}
        </p>

        <div className="dark:text-muted-foreground mt-1 flex items-center justify-between text-sm text-gray-900">
          <span className="flex h-8 items-center leading-none tracking-tight">
            {song.listenCount} listens
          </span>
          <Button
            onClick={handleLike}
            className="flex h-8 cursor-pointer items-center gap-1 p-0"
            variant={"ghost"}
            size={"sm"}
          >
            <Heart
              className={cn("size-4", isLiked && "fill-red-500 text-red-500")}
            />
            {likesCount} likes
          </Button>
        </div>
      </div>
    </div>
  );
}
