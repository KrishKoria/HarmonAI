"use client";

import { authClient } from "@/lib/auth-client";
import { Button } from "./ui/button";

export default function Upgrade() {
  const upgrade = async () => {
    await authClient.checkout({
      products: [
        "f710882e-0b61-453b-b3c7-6f2cbfe48289",
        "33899a68-01f8-4fe1-a492-7f866c500e95",
        "e14f083c-52d8-4908-9f68-3d9dc0e48312",
      ],
    });
  };
  return (
    <Button
      variant="outline"
      size="sm"
      className="ml-2 cursor-pointer text-orange-400"
      onClick={upgrade}
    >
      Upgrade
    </Button>
  );
}
