import { staticFile } from "remotion";
import logoIndex from "../public/logos/logos.json";

// Team colours from Liquipedia (team_color in the Major qualification data), keyed by the VRS team name.
const COLORS: Record<string, string> = {
  G2: "#ee3d23", MIBR: "#00325d", M80: "#daff00", Aurora: "#00ffff", FlyQuest: "#02884b", MOUZ: "#ff0000",
  "Ninjas in Pyjamas": "#d8ff00", Spirit: "#ffffff", PARIVISION: "#00c7b1", HEROIC: "#fc0000", "9z": "#9a0ab7",
  "Chinggis Warriors": "#f42535", FURIA: "#ffffff", FaZe: "#e4002b", "Eternal Fire": "#8f815e", "The MongolZ": "#e8b23a",
  "Lynn Vision": "#b27a2d", FUT: "#ec1a39", Astralis: "#e9493e", Liquid: "#0a6ebd", Vitality: "#ffff00",
  Nemiga: "#ed1c24", "Natus Vincere": "#fff243", Falcons: "#01be6e", Legacy: "#ffc900", BETBOOM: "#ff4655",
  Imperial: "#00d75b", HOTU: "#00dfff", Wildcard: "#20acf8", NRG: "#f63d0a", "100 Thieves": "#ea3031",
  fnatic: "#ff5900", BESTIA: "#ffffff", TYLOO: "#e0262b", B8: "#ffffff", Luminosity: "#2fb7e8", paiN: "#e4002b",
};

const LOGOS = logoIndex as Record<string, { file: string }>;

export const teamColor = (name: string) => COLORS[name] ?? "#5d9cec"; // hex, so cards can add an alpha suffix
export const teamLogo = (name: string) => (LOGOS[name] ? staticFile(LOGOS[name].file) : null);
