export type CameraKey = { f: number; x: number; z: number; dur: number };

// Exact critically damped response. Retargeting carries the current position
// and velocity instead of jumping to the previous key's unfinished destination.
const advance = (p: number, v: number, target: number, omega: number, t: number) => {
  const offset = p - target, carry = v + omega * offset, decay = Math.exp(-omega * t);
  return [target + (offset + carry * t) * decay, (v - omega * carry * t) * decay];
};

export const framing = (keys: CameraKey[], frame: number) => {
  let x = 960, z = .94, vx = 0, vz = 0, tx = 960, tz = .94, at = 0, omega = 3.75;
  for (const key of keys) {
    if (key.f > frame) break;
    const dt = Math.max(0, key.f - at) / 30;
    [x, vx] = advance(x, vx, tx, omega, dt);
    [z, vz] = advance(z, vz, tz, omega, dt);
    at = key.f; tx = key.x; tz = key.z;
    omega = 6 / (Math.max(48, key.dur) / 30);
  }
  const dt = Math.max(0, frame - at) / 30;
  return { x: advance(x, vx, tx, omega, dt)[0], z: advance(z, vz, tz, omega, dt)[0] };
};

// Both the entire portrait and the chart stay inside the picture throughout.
export const soloFramingKeys = (blocks: { from: number; dur: number }[], start: number): CameraKey[] => [
  { f: 0, x: 1020, z: 1, dur: 60 },
  ...blocks.flatMap(b => [
    { f: b.from - start + 42, x: 1020, z: 1.01, dur: 60 },
    { f: b.from - start + Math.max(120, b.dur * .68), x: 1020, z: 1, dur: 60 },
  ]),
].sort((a, b) => a.f - b.f);
