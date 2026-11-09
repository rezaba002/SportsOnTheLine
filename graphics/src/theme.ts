import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// SportsOnTheLine palette, same as the Python engine of videos 02–04 (video04/work/engine.py).
export const C = {
  bg: "rgb(14, 17, 23)",
  panel: "rgb(24, 29, 38)",
  line: "rgb(52, 60, 74)",
  white: "rgb(238, 240, 245)",
  muted: "rgb(138, 147, 162)",
  dim: "rgb(78, 86, 100)",
  ct: "rgb(93, 156, 236)",
  t: "rgb(236, 150, 60)",
  win: "rgb(76, 200, 120)",
  loss: "rgb(228, 76, 76)",
  yellow: "rgb(255, 211, 77)",
} as const;

export const FONT = "Bahnschrift";

// Bahnschrift is a variable font (weights 300–700), the channel font since video 02.
loadFont({ family: FONT, url: staticFile("fonts/bahnschrift.ttf"), weight: "300 700" });
