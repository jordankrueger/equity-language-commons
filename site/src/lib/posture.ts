/**
 * Split a host_posture value into one or more discrete chip labels.
 *
 * `private-mirror-link-out` represents two distinct facts — the Commons has a
 * private archived copy AND links out to the original — and must render as two
 * chips, not one run-on phrase.
 */
export function posturePills(posture: string): string[] {
  switch (posture) {
    case "private-mirror-link-out":
      return ["Private mirror", "Links out"];
    case "host-publicly":
      return ["Hosts publicly"];
    case "link-out-only":
      return ["Links out only"];
    default:
      return [posture.replaceAll("-", " ")];
  }
}
