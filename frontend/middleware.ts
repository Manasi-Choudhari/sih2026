import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("vajra_token")?.value;
  const pathname = request.nextUrl.pathname;

  // 1. If accessing protected routes (/queue, /cases/*) without token, redirect to /login
  if (pathname.startsWith("/queue") || pathname.startsWith("/cases")) {
    if (!token) {
      const loginUrl = new URL("/login", request.url);
      loginUrl.searchParams.set("from", pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  // 2. If already logged in and visiting /login, redirect to /queue
  if (pathname === "/login" && token) {
    return NextResponse.redirect(new URL("/queue", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/queue/:path*", "/cases/:path*", "/login"],
};
