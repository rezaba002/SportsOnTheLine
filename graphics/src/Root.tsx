import { Composition, Folder, Still } from "remotion";
import { ThumbA, ThumbB } from "./video05/Thumb05";
import * as M from "./cards/Mockups";
import { Video05, VIDEO05_FRAMES } from "./video05/Video05";
import { Thumb02A, Thumb02B, Thumb02C } from "./video02/Thumb02";
import { Video07, VIDEO07_FRAMES } from "./video07/Video07";
import { Thumb07 } from "./video07/Thumb07";
import { Thumb07B } from "./video07/Thumb07B";
import { Thumb07V } from "./video07/Thumb07V";
import { Thumb07W } from "./video07/Thumb07W";
import { RankingRace, rankingRaceSchema, calculateRankingRaceMetadata } from "./RankingRace";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Folder name="video05-field">
        <Composition id="Video05" component={Video05} durationInFrames={VIDEO05_FRAMES} fps={30} width={1920} height={1080} />
        <Still id="Thumb07" component={Thumb07} width={1280} height={720} />
        <Still id="Thumb07B" component={Thumb07B} width={1280} height={720} />
        <Still id="Thumb07WA" component={() => <Thumb07W v="A" />} width={1280} height={720} />
        <Still id="Thumb07WB" component={() => <Thumb07W v="B" />} width={1280} height={720} />
        <Still id="Thumb07WC" component={() => <Thumb07W v="C" />} width={1280} height={720} />
        <Still id="Thumb07VA" component={() => <Thumb07V v="A" />} width={1280} height={720} />
        <Still id="Thumb07VB" component={() => <Thumb07V v="B" />} width={1280} height={720} />
        <Still id="Thumb07VC" component={() => <Thumb07V v="C" />} width={1280} height={720} />
        <Composition id="Video07" component={Video07} durationInFrames={VIDEO07_FRAMES} fps={30} width={1920} height={1080} />
        <Still id="Thumb05A" component={ThumbA} width={1280} height={720} />
        <Still id="Thumb02A" component={Thumb02A} width={1280} height={720} />
        <Still id="Thumb02B" component={Thumb02B} width={1280} height={720} />
        <Still id="Thumb02C" component={Thumb02C} width={1280} height={720} />
        <Still id="Thumb05B" component={ThumbB} width={1280} height={720} />
        <Composition
          id="RaceEurope"
          component={RankingRace}
          schema={rankingRaceSchema}
          calculateMetadata={calculateRankingRaceMetadata}
          durationInFrames={300}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{ dataset: "eu", highlight: ["B8"], rows: 24, secondsPerStep: 2, holdSeconds: 3 }}
        />
        <Composition
          id="RaceEuropeDaily"
          component={RankingRace}
          schema={rankingRaceSchema}
          calculateMetadata={calculateRankingRaceMetadata}
          durationInFrames={300}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{ dataset: "euDaily", highlight: ["B8"], rows: 24, secondsPerStep: 0.6, holdSeconds: 3 }}
        />
        <Composition
          id="RaceAmericasDaily"
          component={RankingRace}
          schema={rankingRaceSchema}
          calculateMetadata={calculateRankingRaceMetadata}
          durationInFrames={300}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{ dataset: "amDaily", highlight: ["NRG", "Wildcard"], rows: 14, secondsPerStep: 0.6, holdSeconds: 3 }}
        />
        <Composition
          id="RaceAsiaDaily"
          component={RankingRace}
          schema={rankingRaceSchema}
          calculateMetadata={calculateRankingRaceMetadata}
          durationInFrames={300}
          fps={30}
          width={1920}
          height={1080}
          defaultProps={{ dataset: "asDaily", highlight: ["TYLOO"], rows: 10, secondsPerStep: 0.6, holdSeconds: 3 }}
        />
      </Folder>
      <Folder name="video05-cards">
        <Composition id="CardReel" component={M.CardReel} durationInFrames={M.REEL_FRAMES} fps={30} width={1920} height={1080} />
        <Composition id="MomentNormal" component={M.MomentNormal} durationInFrames={150} fps={30} width={1920} height={1080} />
        <Composition id="MomentBig" component={M.MomentBig} durationInFrames={M.REEL[1].frames} fps={30} width={1920} height={1080} />
        <Composition id="MomentNoPlay" component={M.MomentNoPlay} durationInFrames={160} fps={30} width={1920} height={1080} />
        <Composition id="MomentRoster" component={M.MomentRoster} durationInFrames={M.REEL[3].frames} fps={30} width={1920} height={1080} />
        <Composition id="MomentVerdict" component={M.MomentVerdict} durationInFrames={330} fps={30} width={1920} height={1080} />
      </Folder>
    </>
  );
};
