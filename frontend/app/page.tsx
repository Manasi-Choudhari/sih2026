import { redirect } from "next/navigation";

/**
 * Root route — placeholder (BUILD_T4.md Task 1 still owes the real login
 * screen). For now this sends visitors straight into the app instead of
 * showing the leftover create-next-app starter page.
 */
export default function RootPage() {
  redirect("/queue");
}
