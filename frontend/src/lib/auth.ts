import { env } from "@/env";
import { db } from "@/server/db";
import { betterAuth } from "better-auth";
import { prismaAdapter } from "better-auth/adapters/prisma";
import { Polar } from "@polar-sh/sdk";
import { polar, checkout, portal, webhooks } from "@polar-sh/better-auth";

const polarClient = new Polar({
  accessToken: env.POLAR_ACCESS_TOKEN,
  server: "sandbox",
});
export const auth = betterAuth({
  database: prismaAdapter(db, {
    provider: "postgresql",
  }),
  emailAndPassword: {
    enabled: true,
  },
  plugins: [
    polar({
      client: polarClient,
      createCustomerOnSignUp: true,
      use: [
        checkout({
          products: [
            {
              productId: "f710882e-0b61-453b-b3c7-6f2cbfe48289",
              slug: "large",
            },
            {
              productId: "33899a68-01f8-4fe1-a492-7f866c500e95",
              slug: "medium",
            },
            {
              productId: "e14f083c-52d8-4908-9f68-3d9dc0e48312",
              slug: "small",
            },
          ],
          successUrl: "/",
          authenticatedUsersOnly: true,
        }),
        portal(),
        webhooks({
          secret: env.POLAR_WEBHOOK_SECRET,
          onOrderPaid: async (payload) => {
            const externalCustomerId = payload.data.customer.externalId;
            if (!externalCustomerId) {
              throw new Error("Customer external ID is missing");
            }
            const productID = payload.data.productId;
            let creditAmount = 0;
            switch (productID) {
              case "e14f083c-52d8-4908-9f68-3d9dc0e48312":
                creditAmount = 10;
                break;
              case "33899a68-01f8-4fe1-a492-7f866c500e95":
                creditAmount = 25;
                break;
              case "f710882e-0b61-453b-b3c7-6f2cbfe48289":
                creditAmount = 50;
                break;
            }
            await db.user.update({
              where: { id: externalCustomerId },
              data: {
                credits: {
                  increment: creditAmount,
                },
              },
            });
          },
        }),
      ],
    }),
  ],
});
