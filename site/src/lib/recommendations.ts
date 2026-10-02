export type Recommendation =
  | "use"
  | "non-preferred"
  | "avoid"
  | "use-with-care"
  | "contested"
  | "evolving"
  | "reclaimed-in-community";

export const REC_LABEL: Record<Recommendation, string> = {
  use: "Use",
  "non-preferred": "Non-preferred",
  avoid: "Avoid",
  "use-with-care": "Use with care",
  contested: "Contested",
  evolving: "Evolving",
  "reclaimed-in-community": "Reclaimed in community",
};
