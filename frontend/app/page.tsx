import { redirect } from "next/navigation";

/**
 * Root route — strictly gates entry into the platform.
 * Unauthenticated users are sent to the login terminal.
 */
export default function RootPage() {
  redirect("/login");
}
