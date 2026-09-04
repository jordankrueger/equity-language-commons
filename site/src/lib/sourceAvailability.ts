type SourceAccess = {
  live_status: "live" | "offline" | "login-gated" | "404" | "paywalled";
  local_archive?: string | null;
};

export function sourceAvailability(source: SourceAccess): string {
  if (source.live_status === "live") return "Available online";
  if (source.live_status === "login-gated" || source.live_status === "paywalled") {
    return source.local_archive ? "Access restricted; reference copy held" : "Access restricted";
  }
  if (source.local_archive) return "Reference copy held";
  return "Original unavailable";
}
