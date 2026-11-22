"""Continuous camera points, subpixel resampling and explicit transition handles."""
import json
import math

import numpy as np

from settings import HERE


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * u * (10 + u * (-15 + 6 * u))


def build(edit):
    keys = [{"frame": 0, "z": 1.015, "x": 0.0, "y": 0.0, "point": "opening"}]
    for i, shot in enumerate(edit["shots"]):
        style = shot["style"]
        end = shot["from"] + shot["frames"] - 1
        if style in ["ident", "end"]:
            keys.append({"frame": min(end, shot["from"] + 45), "z": 1.0, "x": 0.0, "y": 0.0, "point": style + " / wide"})
            if keys[-1]["frame"] < end:
                keys.append({**keys[-1], "frame": end})
            continue
        if style in ["interview", "video"]:
            z, x, y = 1.028, [3, -3, 0][i % 3], -1
        elif "chart" in style or style in ["raw_compare", "rank_flip", "fourteen_careers"]:
            z, x, y = [1.025, 1.037][i % 2], [-7, 7][i % 2], -3
        elif style.startswith("baltic_"):
            z, x, y = 1.022, 2, 2
        else:
            z, x, y = [1.04, 1.025, 1.044, 1.03][i % 4], [0, 6, -5, 3][i % 4], [-3, 2, 0, -2][i % 4]
        keys.append({"frame": end, "z": z, "x": x, "y": y, "point": shot["id"]})
    poses = []
    k = 0
    for frame in range(edit["totalFrames"]):
        while k + 1 < len(keys) and keys[k + 1]["frame"] < frame:
            k += 1
        a, b = keys[k], keys[min(k + 1, len(keys) - 1)]
        u = smooth((frame - a["frame"]) / max(1, b["frame"] - a["frame"]))
        poses.append([a[name] + (b[name] - a[name]) * u for name in ["z", "x", "y"]])
    p = np.asarray(poses)
    # Corners stay outside the canvas: no exposed edge during a move.
    left = 960 - 960 * p[:, 0] + p[:, 1]
    right = 960 + 960 * p[:, 0] + p[:, 1]
    top = 540 - 540 * p[:, 0] + p[:, 2]
    bottom = 540 + 540 * p[:, 0] + p[:, 2]
    assert left.max() < .01 and right.min() > 1919.99 and top.max() < .01 and bottom.min() > 1079.99
    corners = np.column_stack([left, right, top, bottom])
    velocity = np.diff(corners, axis=0)
    acceleration = np.diff(velocity, axis=0)
    assert np.max(np.abs(velocity)) < 2.0
    assert np.max(np.abs(acceleration)) < .25
    transitions = []
    for a, b in zip(edit["shots"], edit["shots"][1:]):
        native = a["style"] in ["video", "interview"] or b["style"] in ["video", "interview"]
        duration = 12 if "ident" in [a["style"], b["style"]] else 8 if native else 6
        duration = min(duration, b["frames"] - 1)
        transitions.append({"frame": b["from"], "previous_frame": b["from"] - 1, "frames": duration, "from": a["id"], "to": b["id"], "kind": "archive dissolve" if native else "matched graphic dissolve"})
    data = {"keys": keys, "transitions": transitions, "max_corner_velocity_px_per_frame": float(np.max(np.abs(velocity))), "max_corner_acceleration": float(np.max(np.abs(acceleration))), "interpolation": "quintic ease / cubic subpixel resampling", "poses": poses}
    (HERE / "camera.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def expression(keys, name):
    parts = [f"{keys[0][name]:.8f}"]
    for a, b in zip(keys, keys[1:]):
        delta = b[name] - a[name]
        if abs(delta) < 1e-10:
            continue
        u = f"clip((on-{a['frame']})/{max(1, b['frame'] - a['frame'])},0,1)"
        ease = f"pow({u},3)*(10+({u})*(-15+6*({u})))"
        parts.append(f"({delta:.8f})*({ease})")
    return "+".join(parts)


def filter_camera(camera):
    z, x, y = [expression(camera["keys"], name) for name in ["z", "x", "y"]]
    left, right = f"W/2-W/2*({z})+({x})", f"W/2+W/2*({z})+({x})"
    top, bottom = f"H/2-H/2*({z})+({y})", f"H/2+H/2*({z})+({y})"
    return f"perspective=sense=destination:eval=frame:interpolation=cubic:x0='{left}':y0='{top}':x1='{right}':y1='{top}':x2='{left}':y2='{bottom}':x3='{right}':y3='{bottom}'"


if __name__ == "__main__":
    edit = json.loads((HERE / "edit.json").read_text(encoding="utf-8"))
    data = build(edit)
    print(f"{len(data['keys'])} continuous camera points; max speed {data['max_corner_velocity_px_per_frame']:.3f}px/frame, acceleration {data['max_corner_acceleration']:.3f}.")
