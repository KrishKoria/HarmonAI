import { queueSong } from "@/lib/actions";
import { Button } from "./ui/button";

export default function CreateSong() {
  return <Button onClick={queueSong}>Create Song</Button>;
}
