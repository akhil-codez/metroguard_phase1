"""YOLOv11 + ByteTrack person counting within a configurable image-space ROI.

This Phase-I module detects COCO's ``person`` class and tracks detections with
ByteTrack.  It labels operational crowd occupancy from the tracked count inside
one selected camera zone.  It is deliberately not an incident-reasoning module.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

import cv2
import numpy as np

# Keeping Ultralytics settings next to the project also avoids depending on a
# machine-specific AppData configuration.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# Use a project-local setting directory.  This avoids failures on lab machines
# whose AppData (or a pre-existing temporary YOLO_CONFIG_DIR) is read-only.
os.environ["YOLO_CONFIG_DIR"] = str(PROJECT_ROOT / ".ultralytics")
(PROJECT_ROOT / ".ultralytics").mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class ROI:
    """A rectangular region of interest in normalized image coordinates."""

    left: float = 0.05
    top: float = 0.12
    right: float = 0.95
    bottom: float = 0.95

    def __post_init__(self) -> None:
        if not (0 <= self.left < self.right <= 1 and 0 <= self.top < self.bottom <= 1):
            raise ValueError("ROI values must be in [0, 1] with left<right and top<bottom.")

    def pixels(self, width: int, height: int) -> tuple[int, int, int, int]:
        return (
            round(self.left * width),
            round(self.top * height),
            round(self.right * width),
            round(self.bottom * height),
        )

    def contains_footpoint(self, box: np.ndarray, width: int, height: int) -> bool:
        x1, _, x2, y2 = box.astype(float)
        x, y = (x1 + x2) / 2, y2
        left, top, right, bottom = self.pixels(width, height)
        return left <= x <= right and top <= y <= bottom

    def area_megapixels(self, width: int, height: int) -> float:
        left, top, right, bottom = self.pixels(width, height)
        return max((right - left) * (bottom - top) / 1_000_000, 0.000001)


@dataclass(frozen=True)
class MonitorConfig:
    model_path: str
    confidence: float = 0.35
    # Preserve detail for small, distant people in 1080p CCTV footage.
    # Users may lower this to 640 when real-time speed is more important.
    imgsz: int = 1280
    medium_min: int = 8
    high_min: int = 16
    roi: ROI = ROI()
    tracker: str = "bytetrack.yaml"
    target_id: Optional[int] = None       # Specific person ID to track (0 = auto-lock first in ROI)
    enable_trajectory: bool = True        # Draw motion trail/breadcrumbs for tracked target
    enable_tam: bool = False              # Run Segment Anything Model (MobileSAM) mask
    sam_model_path: str = "mobile_sam.pt" # Path to MobileSAM weights

    def __post_init__(self) -> None:
        if not (0 <= self.confidence <= 1):
            raise ValueError("confidence must be between 0 and 1")
        if self.medium_min < 1 or self.high_min <= self.medium_min:
            raise ValueError("Set positive thresholds with high_min > medium_min.")


@dataclass
class TargetTelemetry:
    """Real-time tracking and trajectory telemetry for a single person of interest."""
    target_id: int
    is_locked: bool
    box: Optional[np.ndarray] = None
    footpoint: Optional[tuple[int, int]] = None
    inside_roi: bool = False
    dwell_time_sec: float = 0.0
    total_distance_px: float = 0.0
    trajectory: list[tuple[int, int]] = field(default_factory=list)


@dataclass
class FrameResult:
    frame_index: int
    timestamp_sec: float
    frame: np.ndarray
    person_count: int
    density_level: str
    occupancy_per_mpx: float
    tracked_ids: list[int]
    event: Optional[str]
    target_telemetry: Optional[TargetTelemetry] = None


def locate_default_model() -> str:
    """Prefer a local YOLO11s weight when available; otherwise let Ultralytics resolve it."""
    candidates = [
        Path(os.environ["METROGUARD_MODEL"]) if "METROGUARD_MODEL" in os.environ else None,
        PROJECT_ROOT / "models" / "yolo11s.pt",
        Path(r"C:\Users\akhia\Downloads\metroguard1\yolo11s.pt"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return str(candidate)
    return "yolo11s.pt"


class CrowdMonitor:
    """Processes frames with YOLOv11 detection, ByteTrack, and target tracking (TAM/SOT)."""

    def __init__(self, config: MonitorConfig):
        from ultralytics import YOLO

        self.config = config
        self.model = YOLO(config.model_path)
        self.previous_level: Optional[str] = None

        # Target tracking state
        self.active_target_id: Optional[int] = config.target_id
        self.trajectory_history: dict[int, list[tuple[int, int]]] = {}
        self.target_first_seen: dict[int, float] = {}
        self.target_total_distance: dict[int, float] = {}

        # Optional TAM (Segment Anything Model)
        self.sam_model = None
        if config.enable_tam:
            from ultralytics import SAM
            sam_candidate = Path(config.sam_model_path)
            if not sam_candidate.is_file():
                local_sam = PROJECT_ROOT / "mobile_sam.pt"
                if local_sam.is_file():
                    sam_candidate = local_sam
            self.sam_model = SAM(str(sam_candidate))

    def density_level(self, person_count: int) -> str:
        if person_count >= self.config.high_min:
            return "HIGH"
        if person_count >= self.config.medium_min:
            return "MEDIUM"
        return "LOW"

    def analyze(self, frame: np.ndarray, frame_index: int, timestamp_sec: float) -> FrameResult:
        """Detect, track, count people in ROI, and follow selected target person."""
        height, width = frame.shape[:2]
        result = self.model.track(
            frame,
            persist=True,
            tracker=self.config.tracker,
            classes=[0],  # COCO class 0 = person
            conf=self.config.confidence,
            imgsz=self.config.imgsz,
            verbose=False,
        )[0]

        boxes = result.boxes
        all_detections: list[tuple[np.ndarray, float, Optional[int], bool]] = []
        selected: list[tuple[np.ndarray, float, Optional[int]]] = []
        if boxes is not None and len(boxes):
            xyxy = boxes.xyxy.cpu().numpy()
            confidence = boxes.conf.cpu().numpy()
            ids = boxes.id.int().cpu().tolist() if boxes.id is not None else [None] * len(xyxy)
            for box, score, track_id in zip(xyxy, confidence, ids):
                in_roi = self.config.roi.contains_footpoint(box, width, height)
                all_detections.append((box, float(score), track_id, in_roi))
                if in_roi:
                    selected.append((box, float(score), track_id))

        count = len(selected)
        level = self.density_level(count)
        event = None
        if self.previous_level is None:
            event = f"Monitoring started: {level} density ({count} people in ROI)"
        elif level != self.previous_level:
            event = f"Density changed: {self.previous_level} → {level} ({count} people in ROI)"
        self.previous_level = level

        # Target Tracking Logic (SOT / TAM)
        target_telemetry: Optional[TargetTelemetry] = None
        target_mask: Optional[np.ndarray] = None

        if self.config.target_id is not None:
            # Auto-lock onto first tracked person inside ROI if set to 0 and not locked yet
            if self.active_target_id in (None, 0):
                for box, score, track_id, in_roi in all_detections:
                    if in_roi and track_id is not None:
                        self.active_target_id = track_id
                        break

            curr_id = self.active_target_id
            if curr_id is not None and curr_id > 0:
                target_box = None
                target_in_roi = False
                for box, score, track_id, in_roi in all_detections:
                    if track_id == curr_id:
                        target_box = box
                        target_in_roi = in_roi
                        break

                if target_box is not None:
                    footpoint = (int((target_box[0] + target_box[2]) / 2), int(target_box[3]))
                    if curr_id not in self.target_first_seen:
                        self.target_first_seen[curr_id] = timestamp_sec
                        self.trajectory_history[curr_id] = []
                        self.target_total_distance[curr_id] = 0.0

                    history = self.trajectory_history[curr_id]
                    if history:
                        prev_pt = history[-1]
                        dist = float(np.hypot(footpoint[0] - prev_pt[0], footpoint[1] - prev_pt[1]))
                        self.target_total_distance[curr_id] += dist
                    history.append(footpoint)

                    # Run MobileSAM segmentation mask if enabled
                    if self.sam_model is not None:
                        try:
                            sam_res = self.sam_model(frame, bboxes=[target_box.tolist()], verbose=False)
                            if sam_res and sam_res[0].masks is not None:
                                target_mask = sam_res[0].masks.data[0].cpu().numpy()
                        except Exception:
                            target_mask = None

                    dwell = timestamp_sec - self.target_first_seen[curr_id]
                    target_telemetry = TargetTelemetry(
                        target_id=curr_id,
                        is_locked=True,
                        box=target_box,
                        footpoint=footpoint,
                        inside_roi=target_in_roi,
                        dwell_time_sec=dwell,
                        total_distance_px=self.target_total_distance.get(curr_id, 0.0),
                        trajectory=list(history),
                    )
                else:
                    # Target currently occluded or outside camera view
                    target_telemetry = TargetTelemetry(
                        target_id=curr_id,
                        is_locked=False,
                        trajectory=list(self.trajectory_history.get(curr_id, [])),
                        total_distance_px=self.target_total_distance.get(curr_id, 0.0),
                    )

        annotated = self._annotate(frame.copy(), selected, count, level, target_telemetry, target_mask)
        return FrameResult(
            frame_index=frame_index,
            timestamp_sec=timestamp_sec,
            frame=annotated,
            person_count=count,
            density_level=level,
            occupancy_per_mpx=count / self.config.roi.area_megapixels(width, height),
            tracked_ids=[track_id for _, _, track_id in selected if track_id is not None],
            event=event,
            target_telemetry=target_telemetry,
        )

    def stream(self, source: str | int, max_frames: int | None = None, stride: int = 1, start_frame: int = 0) -> Iterator[FrameResult]:
        capture = cv2.VideoCapture(source)
        if not capture.isOpened():
            raise ValueError(f"Could not open source: {source}")
        if start_frame > 0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
        index = start_frame
        try:
            while max_frames is None or index < max_frames:
                ok, frame = capture.read()
                if not ok:
                    break
                if stride > 1 and ((index - start_frame) % stride != 0):
                    index += 1
                    continue
                yield self.analyze(frame, index, index / fps)
                index += 1
        finally:
            capture.release()

    def _annotate(
        self,
        frame: np.ndarray,
        selected: list[tuple[np.ndarray, float, Optional[int]]],
        count: int,
        level: str,
        target_telemetry: Optional[TargetTelemetry] = None,
        target_mask: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        height, width = frame.shape[:2]
        left, top, right, bottom = self.config.roi.pixels(width, height)
        colors = {"LOW": (46, 204, 113), "MEDIUM": (0, 190, 255), "HIGH": (52, 73, 232)}
        color = colors[level]

        # 1. Active ROI shading and boundary
        overlay = frame.copy()
        cv2.rectangle(overlay, (left, top), (right, bottom), color, -1)
        frame = cv2.addWeighted(overlay, 0.12, frame, 0.88, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, "ACTIVE ROI", (left + 8, top + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

        # 2. TAM Segmentation Mask Overlay
        if target_mask is not None:
            mask_resized = cv2.resize((target_mask > 0).astype(np.uint8), (width, height), interpolation=cv2.INTER_NEAREST)
            colored_mask = np.zeros_like(frame)
            colored_mask[mask_resized > 0] = (0, 215, 255)  # Bright gold/amber highlight
            mask_overlay = cv2.addWeighted(frame, 0.65, colored_mask, 0.35, 0)
            frame = np.where(mask_resized[:, :, None] > 0, mask_overlay, frame)

        # 3. Target Trajectory Trail (Breadcrumbs)
        if self.config.enable_trajectory and target_telemetry and target_telemetry.trajectory:
            trail = target_telemetry.trajectory
            if len(trail) > 1:
                for i in range(1, len(trail)):
                    cv2.line(frame, trail[i - 1], trail[i], (0, 235, 255), 2, cv2.LINE_AA)
                    cv2.circle(frame, trail[i], 3, (0, 255, 255), -1, cv2.LINE_AA)

        # 4. Normal commuter bounding boxes
        for box, confidence, track_id in selected:
            # Skip if this is the active target (target gets specialized reticle below)
            if target_telemetry and target_telemetry.is_locked and track_id == target_telemetry.target_id:
                continue
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            if track_id is not None:
                identity = f"ID #{track_id} ({int(confidence * 100)}%)"
            else:
                identity = f"person ({int(confidence * 100)}%)"
            cv2.putText(frame, identity, (x1, max(18, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 2)

        # 5. Targeted Person Reticle / High-Visibility Brackets
        if target_telemetry and target_telemetry.is_locked and target_telemetry.box is not None:
            tx1, ty1, tx2, ty2 = map(int, target_telemetry.box)
            t_color = (0, 215, 255)  # Bright gold
            bracket_len = max(10, min(24, (tx2 - tx1) // 3, (ty2 - ty1) // 3))
            # Corner brackets
            cv2.line(frame, (tx1, ty1), (tx1 + bracket_len, ty1), t_color, 3)
            cv2.line(frame, (tx1, ty1), (tx1, ty1 + bracket_len), t_color, 3)
            cv2.line(frame, (tx2, ty1), (tx2 - bracket_len, ty1), t_color, 3)
            cv2.line(frame, (tx2, ty1), (tx2, ty1 + bracket_len), t_color, 3)
            cv2.line(frame, (tx1, ty2), (tx1 + bracket_len, ty2), t_color, 3)
            cv2.line(frame, (tx1, ty2), (tx1, ty2 - bracket_len), t_color, 3)
            cv2.line(frame, (tx2, ty2), (tx2 - bracket_len, ty2), t_color, 3)
            cv2.line(frame, (tx2, ty2), (tx2, ty2 - bracket_len), t_color, 3)
            cv2.rectangle(frame, (tx1, ty1), (tx2, ty2), t_color, 1)

            t_zone = "IN ROI" if target_telemetry.inside_roi else "OUTSIDE ROI"
            t_label = f"TARGET ID #{target_telemetry.target_id} [LOCKED] ({t_zone})"
            cv2.putText(frame, t_label, (tx1, max(18, ty1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, t_color, 2)

        # 6. Top HUD Banner
        panel_height = 82
        cv2.rectangle(frame, (0, 0), (width, panel_height), (22, 28, 38), -1)
        header_title = "METROGUARD AI  |  Crowd Density & Target Tracking (Phase-I)"
        cv2.putText(frame, header_title, (16, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.63, (236, 240, 241), 2)

        status_line = f"ROI people: {count}     Density: {level}"
        if target_telemetry and target_telemetry.target_id:
            t_status = "LOCKED" if target_telemetry.is_locked else "SEARCHING"
            status_line += f"   |   Target ID #{target_telemetry.target_id}: {t_status} ({target_telemetry.dwell_time_sec:.1f}s)"
        cv2.putText(frame, status_line, (16, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.64, color, 2)
        return frame
