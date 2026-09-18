"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut, ShieldCheck, User } from "lucide-react";

export default function UserNav() {
  const router = useRouter();
  const [user, setUser] = useState("inv_sharma");
  const [role, setRole] = useState("investigator");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const storedUser = localStorage.getItem("vajra_user");
    const storedRole = localStorage.getItem("vajra_role");
    if (storedUser) setUser(storedUser);
    if (storedRole) setRole(storedRole);
  }, []);

  function handleSignOut() {
    if (typeof window !== "undefined") {
      document.cookie = "vajra_token=; path=/; max-age=0";
      localStorage.removeItem("vajra_token");
      localStorage.removeItem("vajra_role");
      localStorage.removeItem("vajra_user");
    }
    router.push("/login");
    router.refresh();
  }

  if (!mounted) {
    return (
      <div className="flex items-center gap-3 text-xs text-[#8A93A3]">
        <span className="h-6 w-28 rounded-full bg-[#1B1B1D] animate-pulse" />
      </div>
    );
  }

  const isSupervisor = role === "supervisor" || role === "admin";

  return (
    <div className="flex items-center gap-3 text-xs text-[#8A93A3]">
      {/* Role Pill */}
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-medium ${
          isSupervisor
            ? "border-[#E3AE3E]/40 text-[#E3AE3E] bg-[#E3AE3E]/10"
            : "border-[#3FBE8B]/40 text-[#3FBE8B] bg-[#3FBE8B]/10"
        }`}
      >
        <span
          className={`w-2 h-2 rounded-full ${
            isSupervisor ? "bg-[#E3AE3E]" : "bg-[#3FBE8B]"
          }`}
        />
        <span className="capitalize">{role}</span>: <strong className="font-mono-vajra">{user}</strong>
      </span>

      {/* Sign Out Button */}
      <button
        type="button"
        onClick={handleSignOut}
        title="Sign Out of Session"
        className="flex items-center gap-1.5 px-2.5 py-1 rounded-md border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-[#8A93A3] hover:text-[#E7EAEE] transition-colors"
      >
        <LogOut className="h-3.5 w-3.5" />
        <span className="hidden md:inline">Sign Out</span>
      </button>
    </div>
  );
}
