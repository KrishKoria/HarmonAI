import { create } from "zustand";
interface PlayerTrack {
  currentTrackId: string | null;
  title: string | null;
  url: string | null;
  artwork?: string | null;
  prompt: string | null;
  createdBy: string | null;
}

interface Player {
  track: PlayerTrack | null;
  setTrack: (track: PlayerTrack) => void;
}

export const usePlayerStore = create<Player>((set) => ({
  track: null,
  setTrack: (track) => set({ track }),
}));
