"""Interactive operator dashboard for MetroGuard AI with Target Scanner and Dynamic Resuming."""
from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st
import torch

from metroguard import CrowdMonitor, MonitorConfig, ROI, locate_default_model

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="MetroGuard AI | Phase-I", page_icon="🚇", layout="wide")


def level_color(level: str) -> str:
    return {"LOW": "#32cd7b", "MEDIUM": "#f7b731", "HIGH": "#e74c3c"}[level]


def get_preview(source: str, config: MonitorConfig) -> tuple[np.ndarray, list[int]] | None:
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        return None
    ok, frame = capture.read()
    capture.release()
    if not ok or frame is None:
        return None
    scanner = CrowdMonitor(config)
    res = scanner.analyze(frame, 0, 0.0)
    return res.frame, res.tracked_ids


def main() -> None:
    st.title("MetroGuard AI")

    # Initialize Session State
    if "is_monitoring" not in st.session_state:
        st.session_state.is_monitoring = False
    if "current_frame" not in st.session_state:
        st.session_state.current_frame = 0
    if "monitor" not in st.session_state:
        st.session_state.monitor = None
    if "active_target_id" not in st.session_state:
        st.session_state.active_target_id = 0
    if "preview_data" not in st.session_state:
        st.session_state.preview_data = None
    if "last_source_id" not in st.session_state:
        st.session_state.last_source_id = ""
    if "event_logs" not in st.session_state:
        st.session_state.event_logs = []
    if "temp_uploaded_path" not in st.session_state:
        st.session_state.temp_uploaded_path = None

    # Sidebar: Detection & Zone Settings
    with st.sidebar:
        st.header("Detection & Zone Settings")
        model_path = st.text_input("YOLOv11 weights", value=locate_default_model())
        st.divider()

        st.subheader("Active ROI (% of frame)")
        c1, c2 = st.columns(2)
        left = c1.slider("Left", 0, 90, 5) / 100
        right = c2.slider("Right", 10, 100, 95) / 100
        top = c1.slider("Top", 0, 90, 12) / 100
        bottom = c2.slider("Bottom", 10, 100, 95) / 100

        st.subheader("Operational occupancy thresholds")
        medium = st.number_input("Medium from (people)", min_value=1, value=8)
        high = st.number_input("High from (people)", min_value=int(medium) + 1, value=max(16, int(medium) + 1))
        confidence = st.slider("Detection confidence", 0.10, 0.90, 0.35, 0.05)
        inference_size = st.select_slider(
            "Detection detail", options=[640, 960, 1280], value=1280,
            help="Use 1280 for 1080p CCTV: distant people are clearer, but processing is slower."
        )

        if torch.cuda.is_available():
            st.success(f"⚡ GPU: {torch.cuda.get_device_name(0)}")
        else:
            st.info("💻 Processor: CPU")

        max_frames = st.number_input("Frames to process (0 = full video)", min_value=0, value=0, step=25)
        frame_stride = st.slider(
            "Frame step / stride", min_value=1, max_value=4, value=1,
            help="1 = process every frame. 2 = process every 2nd frame (2x faster, retains full 1280px detail)."
        )

        st.divider()
        st.subheader("🎯 Target Tracking (TAM / SOT)")
        enable_target = st.checkbox(
            "Enable Target Person Tracking", value=True,
            help="Track and follow a specific commuter through the crowd"
        )
        enable_tam = False
        enable_trail = True
        if enable_target:
            raw_target = st.text_input(
                "Target Track ID (0 = auto-lock first in ROI)",
                value=str(st.session_state.active_target_id),
                help="Enter the ID number shown on the person's box (e.g. 20). If you enter 20.32, ID 20 will be targeted."
            )
            clean_str = raw_target.upper().replace("ID", "").replace("#", "").strip()
            try:
                st.session_state.active_target_id = int(float(clean_str)) if clean_str else 0
            except ValueError:
                st.session_state.active_target_id = 0

            target_display = f"ID #{st.session_state.active_target_id}" if st.session_state.active_target_id > 0 else "Auto-lock first person in ROI"
            st.caption(f"🎯 Target selected: **{target_display}**")
            st.caption("ℹ️ *Note: Box labels show `ID #<ID> (<confidence>%)`. E.g., `ID #20 (32%)` is Person ID 20.*")
            enable_trail = st.checkbox("Draw Trajectory Trail (Breadcrumbs)", value=True)
            enable_tam = st.checkbox(
                "TAM Segmentation Mask (MobileSAM)", value=False,
                help="Applies Track Anything (MobileSAM) pixel silhouette mask over the target person"
            )

    # Main Center Area: Video input
    st.subheader("Video Source")
    vcol1, vcol2 = st.columns([1, 1])
    with vcol1:
        uploaded = st.file_uploader("Upload a video", type=["mp4", "avi", "mov", "mkv"])
    with vcol2:
        source_path = st.text_input(
            "…or use a local video path",
            value="",
            placeholder=r"e.g. C:\Users\akhia\Downloads\metroguard1\data\crowd\people_walking.mp4",
        )
        st.caption("Tip: Enter a video file path or camera index (e.g. 0 for webcam).")

    # Resolve Video Source Path
    source = None
    source_identifier = ""
    if uploaded is not None:
        source_identifier = uploaded.name
        if st.session_state.last_source_id != source_identifier:
            suffix = Path(uploaded.name).suffix or ".mp4"
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(uploaded.getbuffer())
            temp_file.close()
            st.session_state.temp_uploaded_path = temp_file.name
        source = st.session_state.temp_uploaded_path
    elif source_path.strip():
        source_identifier = source_path.strip()
        source = source_path.strip()

    # If source changed, reset frame position and preview
    if source_identifier and source_identifier != st.session_state.last_source_id:
        st.session_state.last_source_id = source_identifier
        st.session_state.current_frame = 0
        st.session_state.monitor = None
        st.session_state.preview_data = None
        st.session_state.is_monitoring = False
        st.session_state.event_logs = []

    if not source:
        st.divider()
        st.info("Upload a video or enter a local video path above to begin.")
        return

    # Create Configuration
    try:
        roi = ROI(left, top, right, bottom)
        config = MonitorConfig(
            model_path=model_path,
            confidence=confidence,
            imgsz=inference_size,
            medium_min=int(medium),
            high_min=int(high),
            roi=roi,
            target_id=st.session_state.active_target_id if enable_target else None,
            enable_trajectory=enable_trail,
            enable_tam=enable_tam,
        )
    except ValueError as error:
        st.error(str(error))
        return

    # Pre-stream Target Scanner & Candidate ID Picker
    with st.expander("🔍 Target Scanner: Preview First Frame & Pick a Person to Follow", expanded=(st.session_state.current_frame == 0 and not st.session_state.is_monitoring)):
        pcol1, pcol2 = st.columns([2, 1])
        if st.session_state.preview_data is None:
            with pcol1:
                st.caption("Click below to detect all people in the scene and view their candidate IDs.")
                if st.button("📸 Scan Scene & Detect Candidate IDs", type="secondary"):
                    with st.spinner("Scanning frame 0 for commuters..."):
                        preview_res = get_preview(source, config)
                        if preview_res:
                            st.session_state.preview_data = preview_res
                            st.rerun()
                        else:
                            st.error("Could not read frame from video.")
        else:
            prev_img, cand_ids = st.session_state.preview_data
            with pcol1:
                st.image(prev_img[:, :, ::-1], channels="RGB", use_container_width=True, caption="Initial Scene Preview with Detected Person IDs")
            with pcol2:
                st.markdown("#### 🎯 Choose Target")
                options = ["Auto-lock first in ROI (ID: 0)"] + [f"Person ID #{cid}" for cid in sorted(cand_ids)]
                curr_idx = 0
                if st.session_state.active_target_id in cand_ids:
                    curr_idx = options.index(f"Person ID #{st.session_state.active_target_id}")

                chosen = st.selectbox("Select commuter to follow:", options, index=curr_idx)
                if chosen.startswith("Auto"):
                    new_id = 0
                else:
                    new_id = int(chosen.split("#")[1])

                if new_id != st.session_state.active_target_id:
                    st.session_state.active_target_id = new_id
                    if st.session_state.monitor:
                        st.session_state.monitor.active_target_id = new_id
                    st.rerun()

                st.success(f"Locked on: **{chosen}**")
                if st.button("🔄 Re-Scan Frame", use_container_width=True):
                    st.session_state.preview_data = None
                    st.rerun()

    # Playback Control Buttons (Start / Pause / Reset)
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
    with ctrl_col1:
        if not st.session_state.is_monitoring:
            btn_label = "▶️ Start Monitoring" if st.session_state.current_frame == 0 else f"▶️ Resume Monitoring (Frame {st.session_state.current_frame})"
            if st.button(btn_label, type="primary", use_container_width=True):
                st.session_state.is_monitoring = True
                st.rerun()
        else:
            if st.button("⏸️ Pause Monitoring", type="secondary", use_container_width=True):
                st.session_state.is_monitoring = False
                st.rerun()

    with ctrl_col2:
        if st.session_state.current_frame > 0 or st.session_state.is_monitoring:
            if st.button("🔄 Reset from Frame 0", use_container_width=True):
                st.session_state.is_monitoring = False
                st.session_state.current_frame = 0
                st.session_state.monitor = None
                st.session_state.event_logs = []
                st.rerun()

    with ctrl_col3:
        if st.session_state.current_frame > 0:
            st.caption(f"📍 Position: **Frame {st.session_state.current_frame}**")

    # If Monitoring is Paused or Not Started, display summary of where we are
    if not st.session_state.is_monitoring:
        if st.session_state.current_frame > 0:
            st.info(f"Monitoring paused at frame {st.session_state.current_frame}. You can select or change target ID above and click **Resume Monitoring** to continue.")
        return

    # Active Monitoring Loop
    try:
        # Reuse existing monitor to preserve ByteTrack identity states
        if st.session_state.monitor is None:
            st.session_state.monitor = CrowdMonitor(config)
        else:
            monitor = st.session_state.monitor
            monitor.active_target_id = config.target_id
            monitor.config = config

        monitor = st.session_state.monitor

        feed, summary = st.columns([3, 2])
        frame_slot = feed.empty()
        m1, m2, m3 = summary.columns(3)
        count_slot = m1.empty()
        density_slot = m2.empty()
        status_slot = m3.empty()

        target_status_slot = None
        target_dwell_slot = None
        if enable_target:
            summary.markdown("#### 🎯 Target Telemetry")
            t1, t2 = summary.columns(2)
            target_status_slot = t1.empty()
            target_dwell_slot = t2.empty()

        summary.markdown("#### Event log")
        log_slot = summary.empty()
        processing_state = st.empty()

        start_f = st.session_state.current_frame
        for result in monitor.stream(
            source,
            max_frames=int(max_frames) or None,
            stride=int(frame_stride),
            start_frame=start_f,
        ):
            # Update position in session state continuously
            st.session_state.current_frame = result.frame_index + 1

            frame_slot.image(result.frame[:, :, ::-1], channels="RGB", use_container_width=True)
            count_slot.metric("People in ROI (estimate)", result.person_count)
            density_slot.metric("Density", result.density_level)
            status_slot.metric("System", "ACTIVE")

            if enable_target and result.target_telemetry and target_status_slot and target_dwell_slot:
                tt = result.target_telemetry
                if tt.is_locked:
                    loc = "Inside ROI" if tt.inside_roi else "Outside ROI"
                    target_status_slot.metric(f"Target ID #{tt.target_id}", f"LOCKED ({loc})")
                    target_dwell_slot.metric("Target Dwell Time", f"{tt.dwell_time_sec:.1f}s")
                else:
                    target_status_slot.metric(f"Target ID #{tt.target_id}", "SEARCHING...")
                    target_dwell_slot.metric("Target Dwell Time", "—")

            if result.event:
                st.session_state.event_logs.insert(0, {"time": f"{result.timestamp_sec:.1f}s", "event": result.event})

            log_slot.dataframe(
                pd.DataFrame(st.session_state.event_logs or [{"time": "—", "event": "Monitoring active; no change yet."}]),
                hide_index=True,
                use_container_width=True,
            )
            processing_state.caption(f"Processing frame {result.frame_index + 1}…")

        processing_state.empty()
        st.session_state.is_monitoring = False
        st.success(f"Completed: processed up to frame {st.session_state.current_frame} at {datetime.now().strftime('%H:%M:%S')}.")

    except Exception as error:
        st.session_state.is_monitoring = False
        st.error(f"Could not run monitoring: {error}")


if __name__ == "__main__":
    main()
