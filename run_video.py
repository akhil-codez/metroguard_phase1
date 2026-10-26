"""Command-line runner for the MetroGuard Phase-I crowd-density module."""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2

from metroguard import CrowdMonitor, MonitorConfig, ROI, locate_default_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MetroGuard Phase-I crowd-density monitor")
    parser.add_argument("source", help="Path to a video file, image sequence, or camera index")
    parser.add_argument("--model", default=locate_default_model(), help="YOLOv11 .pt weights path")
    parser.add_argument("--output", default="data/output/annotated_crowd.mp4")
    parser.add_argument("--confidence", type=float, default=0.35)
    parser.add_argument("--imgsz", type=int, default=1280,
                        help="YOLO inference size; 1280 improves small-person recall, while 640 is faster.")
    parser.add_argument("--medium-min", type=int, default=8, help="Count at which density becomes MEDIUM")
    parser.add_argument("--high-min", type=int, default=16, help="Count at which density becomes HIGH")
    parser.add_argument("--roi", default="0.05,0.12,0.95,0.95", help="left,top,right,bottom as 0-1 values")
    parser.add_argument("--max-frames", type=int, default=None, help="Use a short run for a quick test")
    parser.add_argument("--target-id", type=str, default=None, help="Track a specific person ID (e.g. 20, or 0 for auto-lock)")
    parser.add_argument("--enable-tam", action="store_true", help="Enable MobileSAM pixel-level segmentation mask on target")
    parser.add_argument("--no-trajectory", action="store_true", help="Disable trajectory trail drawing")
    parser.add_argument("--stride", type=int, default=1, help="Process every Nth frame (e.g. 2 for 2x faster, 0 detail loss)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    roi = ROI(*map(float, args.roi.split(",")))
    target_id = None
    if args.target_id is not None:
        clean = args.target_id.upper().replace("ID", "").replace("#", "").strip()
        try:
            target_id = int(float(clean))
        except ValueError:
            target_id = None

    monitor = CrowdMonitor(MonitorConfig(
        model_path=args.model,
        confidence=args.confidence,
        imgsz=args.imgsz,
        medium_min=args.medium_min,
        high_min=args.high_min,
        roi=roi,
        target_id=target_id,
        enable_trajectory=not args.no_trajectory,
        enable_tam=args.enable_tam,
    ))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    last = None
    source: str | int = int(args.source) if args.source.isdigit() else args.source
    for result in monitor.stream(source, max_frames=args.max_frames, stride=args.stride):
        if writer is None:
            height, width = result.frame.shape[:2]
            writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), 25, (width, height))
        writer.write(result.frame)
        if result.event:
            print(f"[{result.timestamp_sec:6.1f}s] {result.event}")
        last = result
    if writer is not None:
        writer.release()
    if last is None:
        raise RuntimeError("No frames were processed.")
    print(f"Saved annotated output: {output.resolve()}")
    print(f"Final status: {last.person_count} people | {last.density_level} | "
          f"{last.occupancy_per_mpx:.1f} people/ROI-megapixel")
    if last.target_telemetry and last.target_telemetry.target_id:
        tt = last.target_telemetry
        lock_str = "LOCKED" if tt.is_locked else "SEARCHING"
        zone_str = "Inside ROI" if tt.inside_roi else "Outside ROI"
        print(f"Target Tracking: ID {tt.target_id} [{lock_str}] ({zone_str}) | "
              f"Dwell Time: {tt.dwell_time_sec:.1f}s | Traveled: {tt.total_distance_px:.0f}px")


if __name__ == "__main__":
    main()
