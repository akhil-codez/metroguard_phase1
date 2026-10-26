"""Prepare manual count labels and score MetroGuard crowd-count estimates.

This measures *counting accuracy* for the selected camera ROI. It is not a
bounding-box detection mAP evaluation; mAP needs person boxes as ground truth.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from metroguard import CrowdMonitor, MonitorConfig, ROI, locate_default_model


def roi_from_text(value: str) -> ROI:
    try:
        return ROI(*map(float, value.split(",")))
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("ROI must be left,top,right,bottom using values from 0 to 1.") from error


def prepare(args: argparse.Namespace) -> None:
    source = Path(args.source)
    if not source.is_file():
        raise FileNotFoundError(f"Source not found: {source}")

    capture = cv2.VideoCapture(str(source))
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    if total <= 0:
        raise RuntimeError("Could not determine video frame count.")

    frame_indices = np.linspace(0, total - 1, num=args.samples, dtype=int)
    root = Path(args.output)
    raw_dir, guide_dir, annotated_dir = root / "raw_frames", root / "roi_guides", root / "annotated_frames"
    raw_dir.mkdir(parents=True, exist_ok=True)
    guide_dir.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)
    monitor = CrowdMonitor(MonitorConfig(
        model_path=args.model, confidence=args.confidence, imgsz=args.imgsz,
        medium_min=args.medium_min, high_min=args.high_min, roi=args.roi,
    ))
    # Preserve existing ground-truth labels if re-running on the same dataset
    existing_gt: dict[int, object] = {}
    csv_path = root / "count_labels.csv"
    backup_path = root / "ground_truth_benchmark.csv"
    for p in [csv_path, backup_path]:
        if p.is_file():
            try:
                old_df = pd.read_csv(p)
                if "frame_index" in old_df.columns and "ground_truth_count" in old_df.columns:
                    for _, r in old_df.iterrows():
                        val = r["ground_truth_count"]
                        if pd.notna(val) and str(val).strip():
                            existing_gt[int(r["frame_index"])] = int(float(val))
            except Exception:
                pass

    records: list[dict[str, object]] = []
    for frame_index in frame_indices:
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
        ok, frame = capture.read()
        if not ok:
            print(f"Skipping unreadable frame {frame_index}.")
            continue
        result = monitor.analyze(frame, int(frame_index), int(frame_index) / fps)
        name = f"frame_{frame_index:05d}.png"
        cv2.imwrite(str(raw_dir / name), frame)
        guide = frame.copy()
        height, width = guide.shape[:2]
        left, top, right, bottom = args.roi.pixels(width, height)
        cv2.rectangle(guide, (left, top), (right, bottom), (0, 215, 255), 3)
        cv2.putText(guide, "MANUAL COUNT ROI", (left + 8, max(30, top + 30)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 215, 255), 2)
        cv2.imwrite(str(guide_dir / name), guide)
        cv2.imwrite(str(annotated_dir / name), result.frame)
        records.append({
            "frame_index": int(frame_index),
            "timestamp_seconds": round(int(frame_index) / fps, 3),
            "predicted_count": result.person_count,
            "ground_truth_count": existing_gt.get(int(frame_index), ""),
            "raw_frame": f"raw_frames/{name}",
            "roi_guide": f"roi_guides/{name}",
            "annotated_frame": f"annotated_frames/{name}",
        })
        print(f"Prepared frame {frame_index}: model estimate = {result.person_count}")
    capture.release()
    pd.DataFrame(records).to_csv(csv_path, index=False)
    print(f"\nPrepared {len(records)} samples in {root.resolve()}")
    if len(existing_gt) == len(records):
        print("Restored existing ground-truth labels for all frames.")
    else:
        print("Open roi_guides (it has only the ROI boundary, not model detections), then manually count")
        print("every visible person whose footpoint lies in that ROI,")
        print("enter that value in ground_truth_count in count_labels.csv, then run the score command.")


def score(args: argparse.Namespace) -> None:
    csv_path = Path(args.csv)
    data = pd.read_csv(csv_path)
    required = {"predicted_count", "ground_truth_count"}
    if not required.issubset(data.columns):
        raise ValueError("The CSV must contain predicted_count and ground_truth_count columns.")
    data["ground_truth_count"] = pd.to_numeric(data["ground_truth_count"], errors="coerce")
    missing = data["ground_truth_count"].isna()
    if missing.any():
        raise ValueError(f"Enter manual ground-truth counts for all rows before scoring ({missing.sum()} blank).")
    predicted = data["predicted_count"].astype(float)
    truth = data["ground_truth_count"].astype(float)
    error = predicted - truth
    absolute_error = error.abs()
    total_truth = truth.sum()
    wape = absolute_error.sum() / total_truth if total_truth else float("nan")
    report = {
        "sampled_frames": int(len(data)),
        "manual_people_total": int(total_truth),
        "model_people_total": int(predicted.sum()),
        "mean_absolute_error_people": round(float(absolute_error.mean()), 3),
        "root_mean_squared_error_people": round(float(np.sqrt((error**2).mean())), 3),
        "mean_signed_error_people": round(float(error.mean()), 3),
        "weighted_absolute_percentage_error_percent": round(float(wape * 100), 2),
        "count_accuracy_percent": round(float(max(0, 1 - wape) * 100), 2),
    }
    print("Count-accuracy evaluation (ROI occupancy)")
    for label, value in report.items():
        print(f"{label}: {value}")
    report_path = csv_path.with_name("count_accuracy_report.csv")
    pd.DataFrame([report]).to_csv(report_path, index=False)
    print(f"Saved report: {report_path.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MetroGuard Phase-I count evaluation")
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare", help="Export sampled frames and a blank manual-label CSV")
    prep.add_argument("source", help="Crowd video to evaluate")
    prep.add_argument("--output", default="evaluation", help="Folder for raw frames and CSV")
    prep.add_argument("--samples", type=int, default=20, help="Number of evenly spaced frames")
    prep.add_argument("--model", default=locate_default_model())
    prep.add_argument("--confidence", type=float, default=0.10)
    prep.add_argument("--imgsz", type=int, default=1280)
    prep.add_argument("--medium-min", type=int, default=8)
    prep.add_argument("--high-min", type=int, default=16)
    prep.add_argument("--roi", type=roi_from_text, default=ROI(), help="left,top,right,bottom (0-1)")
    scored = commands.add_parser("score", help="Calculate metrics after manual labels are entered")
    scored.add_argument("csv", help="The completed count_labels.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.command == "prepare":
            if args.samples < 1:
                raise ValueError("samples must be at least 1")
            prepare(args)
        else:
            score(args)
    except Exception as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
