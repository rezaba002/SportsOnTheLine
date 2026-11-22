import { Composition, registerRoot } from "remotion";
import { Video08CodexV2 } from "./Film";
import { TOTAL_FRAMES } from "./duration";

const Root: React.FC = () => (
  <Composition
    id="Video08CodexV2"
    component={Video08CodexV2}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{ burnCaptions: true, nativeVideo: true }}
  />
);
registerRoot(Root);
