// @ts-check
import { defineConfig } from "astro/config";

// https://astro.build/config
export default defineConfig({
  site: "https://equitylanguagecommons.org",
  trailingSlash: "always",
  build: {
    format: "directory",
  },
  vite: {
    server: {
      // Allow dev access via Tailscale MagicDNS hostname from Jordan's MBP
      allowedHosts: [
        "localhost",
        "127.0.0.1",
        "100.118.178.64",
        "jordans-mac-mini",
        "jordans-mac-mini.tailnet.ts.net",
      ],
    },
  },
});
