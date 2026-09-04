import { getCollection } from "astro:content";

export async function GET({ site }: { site: URL }) {
  const [terms, chapters, sources] = await Promise.all([
    getCollection("terms"),
    getCollection("chapters"),
    getCollection("sources"),
  ]);
  const paths = ["/", "/about/", "/chapters/", "/contribute/", "/glossary/", "/methodology/", "/sources/"];
  paths.push(...terms.filter((item) => !item.data.stub).map((item) => `/terms/${item.data.slug}/`));
  paths.push(...chapters.filter((item) => !item.data.stub).map((item) => `/chapters/${item.data.slug}/`));
  paths.push(...new Set(sources.map((item) => `/sources/${item.data.org_slug}/`)));
  const urls = paths.sort().map((path) => `  <url><loc>${new URL(path, site)}</loc></url>`).join("\n");
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls}\n</urlset>\n`, {
    headers: { "Content-Type": "application/xml" },
  });
}
