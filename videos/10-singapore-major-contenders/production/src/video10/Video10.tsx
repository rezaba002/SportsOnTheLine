import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile } from "remotion";
import timeline from "../../public/video10/timeline.json";
import { MotionScene } from "./MotionScene";
import { FONT } from "../theme";

export const VIDEO10_FRAMES = timeline.frames;
export const Video10: React.FC = () => <AbsoluteFill style={{ background: "#080e15" }}>
  {timeline.scenes.map((scene) => <Sequence key={scene.id} from={scene.fromFrame} durationInFrames={scene.frames}><MotionScene scene={scene} /></Sequence>)}
  <Sequence from={timeline.introFrom} durationInFrames={timeline.introFrames}><OffthreadVideo src={staticFile("video09-v4/intro.mp4")} muted /></Sequence>
  <Sequence from={timeline.frames - 600} durationInFrames={600}><AbsoluteFill style={{ background: "#080e15", color: "#f2f5f7", fontFamily: FONT, justifyContent: "center", alignItems: "center" }}><div style={{ fontSize: 90 }}>THE MAJOR WILL TEST THEM.</div></AbsoluteFill></Sequence>
</AbsoluteFill>;

export const Video10Review: React.FC = () => <AbsoluteFill style={{ background: "#080e15" }}>
  {["hook", "mouz_odds", "vitality_scenario", "vitality_history", "fallen"].map((id, i) => <Sequence key={id} from={i * 180} durationInFrames={180}><MotionScene scene={timeline.scenes.find((scene) => scene.id === id)!} sample /></Sequence>)}
</AbsoluteFill>;
