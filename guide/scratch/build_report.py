"""Generate comprehensive MetroGuard AI Phase-I Technical Report in HTML and compile to PDF."""
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_OUTPUT = PROJECT_ROOT / "MetroGuard_AI_Technical_Report.html"
PDF_OUTPUT = PROJECT_ROOT / "MetroGuard_AI_Technical_Report.pdf"

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>MetroGuard AI — Technical Architecture & Implementation Report</title>
<style>
  @page {
    size: A4;
    margin: 18mm 16mm 18mm 16mm;
    @bottom-right {
      content: counter(page);
    }
  }

  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.6;
    font-size: 10.5pt;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
  }

  /* Headings */
  h1, h2, h3, h4 {
    color: #0f172a;
    font-weight: 700;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    page-break-after: avoid;
  }

  h1 {
    font-size: 22pt;
    color: #1e3a8a;
    border-bottom: 3px solid #2563eb;
    padding-bottom: 8px;
    margin-top: 0;
  }

  h2 {
    font-size: 14pt;
    color: #1e40af;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 1.4em;
  }

  h3 {
    font-size: 11.5pt;
    color: #334155;
    margin-top: 1em;
  }

  h4 {
    font-size: 10.5pt;
    color: #475569;
    font-weight: 600;
  }

  p {
    margin: 0.4em 0 0.8em 0;
    text-align: justify;
  }

  /* Lists */
  ul, ol {
    margin: 0.4em 0 0.8em 1.4em;
    padding: 0;
  }

  li {
    margin-bottom: 0.35em;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }

  th, td {
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
    vertical-align: top;
  }

  th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
  }

  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  /* Code Blocks */
  code {
    font-family: 'Consolas', 'Courier New', Courier, monospace;
    font-size: 9pt;
    background-color: #f1f5f9;
    padding: 1px 4px;
    border-radius: 3px;
    color: #0f172a;
  }

  pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 12px 14px;
    border-radius: 6px;
    overflow-x: auto;
    font-family: 'Consolas', 'Courier New', Courier, monospace;
    font-size: 8.5pt;
    line-height: 1.45;
    margin: 0.8em 0;
    page-break-inside: avoid;
  }

  pre code {
    background: none;
    color: inherit;
    padding: 0;
  }

  /* Callout boxes */
  .callout {
    border-left: 4px solid #2563eb;
    background-color: #eff6ff;
    padding: 10px 14px;
    margin: 1em 0;
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
  }

  .callout.warning {
    border-left-color: #f59e0b;
    background-color: #fffbeb;
  }

  .callout.success {
    border-left-color: #10b981;
    background-color: #f0fdf4;
  }

  .callout-title {
    font-weight: 700;
    margin-bottom: 4px;
    color: #1e3a8a;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .callout.warning .callout-title {
    color: #b45309;
  }

  .callout.success .callout-title {
    color: #047857;
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 8pt;
    font-weight: 600;
    border-radius: 4px;
    text-transform: uppercase;
  }

  .badge-low { background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }
  .badge-med { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
  .badge-high { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }

  /* Formula block */
  .formula-box {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px 16px;
    margin: 0.8em 0;
    font-family: 'Cambria Math', 'Times New Roman', serif;
    font-size: 11pt;
    text-align: center;
    page-break-inside: avoid;
  }

  /* Page break utility */
  .page-break {
    page-break-before: always;
  }

  /* Header Cover Card */
  .header-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
    color: white;
    padding: 24px 28px;
    border-radius: 8px;
    margin-bottom: 24px;
  }

  .header-card h1 {
    color: white;
    border: none;
    font-size: 24pt;
    margin: 0 0 6px 0;
    padding: 0;
  }

  .header-card .subtitle {
    font-size: 12pt;
    color: #93c5fd;
    margin-bottom: 16px;
  }

  .header-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    font-size: 9pt;
    color: #cbd5e1;
    border-top: 1px solid #334155;
    padding-top: 12px;
  }

  .meta-item strong {
    color: #ffffff;
  }
</style>
</head>
<body>

<!-- Header Banner -->
<div class="header-card">
  <h1>MetroGuard AI</h1>
  <div class="subtitle">Comprehensive Technical Architecture & Implementation Report — Phase-I Crowd Density Prototype</div>
  <div class="header-meta">
    <div class="meta-item"><strong>Focus:</strong> Real-Time Occupancy & Crowd Flow Monitoring</div>
    <div class="meta-item"><strong>Detection:</strong> YOLOv11s (COCO Class 0)</div>
    <div class="meta-item"><strong>Tracking:</strong> ByteTrack Association</div>
    <div class="meta-item"><strong>UI:</strong> Streamlit Operator Console</div>
    <div class="meta-item"><strong>Target Domain:</strong> Transit & Metro Security</div>
  </div>
</div>

<!-- Section 1 -->
<h2>1. Executive Summary & Project Purpose</h2>
<p>
Modern urban rail and rapid transit networks transport millions of commuters daily. Overcrowded platforms, stairwells, and turnstile concourses represent severe operational vulnerabilities that can rapidly escalate into stampedes, accidental track falls, boarding delays, or passenger distress. While high-definition CCTV systems are ubiquitous across transit stations, human security operators cannot concurrently monitor dozens of camera feeds with sustained vigilance.
</p>
<p>
<strong>MetroGuard AI (Phase-I)</strong> delivers an automated, real-time computer vision subsystem engineered to measure, classify, and track commuter crowd levels within operator-designated <em>Regions of Interest (ROI)</em>. The system continuously ingests surveillance video streams, detects and tracks human commuters across sequential frames, filters individuals based on ground-plane physical contact, and produces dynamic alert telemetry (LOW, MEDIUM, HIGH) via an interactive operations console and an automated command-line processing pipeline.
</p>

<div class="callout">
  <div class="callout-title">Engineering Discipline: Explicit Phase-I Scope & Scientific Honesty</div>
  <p>
    Unlike conventional speculative prototypes that claim automated violence recognition, anomaly detection, or abandoned baggage identification without validated ground truth, <strong>Phase-I is deliberately and rigorously restricted to verified person counting and occupancy classification</strong>. Furthermore, the system measures <em>image-space occupancy</em> (people per ROI-megapixel) rather than physical density ($people/m^2$), acknowledging that true physical density requires extrinsic camera calibration and homography matrices.
  </p>
</div>

<!-- Section 2 -->
<h2>2. Technologies, Frameworks & Deep Learning Models</h2>
<p>
Every software library, neural architecture, and utility in MetroGuard AI was selected to balance detection recall, tracking consistency, frame processing latency, and operational reproducibility.
</p>

<table>
  <thead>
    <tr>
      <th style="width: 22%;">Technology / Tool</th>
      <th style="width: 26%;">Role in MetroGuard AI</th>
      <th style="width: 28%;">Technical Significance & Rationale</th>
      <th style="width: 24%;">Implementation Detail</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>YOLOv11s<br>(Ultralytics 8.4)</strong></td>
      <td>Primary deep neural detector for extracting bounding boxes of commuters.</td>
      <td>State-of-the-art one-stage detector combining C3k2 building blocks, SPPF (Spatial Pyramid Pooling - Fast), and an anchor-free detection head. Delivers higher mAP at faster inference speeds compared to YOLOv8 and YOLOv5.</td>
      <td>Configured via <code>ultralytics.YOLO()</code> with weights resolution in <code>locate_default_model()</code>. Restricted to <code>classes=[0]</code> (COCO <code>person</code>) to prevent false positive allocations.</td>
    </tr>
    <tr>
      <td><strong>ByteTrack Framework</strong></td>
      <td>Multi-Object Tracking (MOT) across consecutive frames.</td>
      <td>Solves the occlusion problem in crowded environments. Unlike trackers that discard low-confidence detections, ByteTrack associates both high-confidence and low-confidence boxes using Kalman filters and Hungarian matching, maintaining stable person IDs through overlaps.</td>
      <td>Executed natively through <code>model.track(..., persist=True, tracker="bytetrack.yaml")</code>. Track IDs are stored and assigned to per-frame telemetry.</td>
    </tr>
    <tr>
      <td><strong>OpenCV (cv2 5.0)</strong></td>
      <td>Video decoding, frame extraction, spatial graphics rendering, and video encoding.</td>
      <td>High-speed C++ computer vision engine. Efficiently decodes H.264/MP4 streams, applies transparent ROI alpha overlays, draws color-coded bounding boxes and HUD banners, and writes annotated videos.</td>
      <td><code>cv2.VideoCapture</code> for frame iteration; <code>cv2.rectangle</code> and <code>cv2.addWeighted</code> for semi-transparent zone shading; <code>cv2.VideoWriter</code> for annotated MP4 creation.</td>
    </tr>
    <tr>
      <td><strong>Streamlit 1.65</strong></td>
      <td>Interactive web console for transit operators and supervisors.</td>
      <td>Enables rapid reactive UI development in pure Python with zero front-end overhead. Provides dynamic real-time frame streaming, interactive sliders for live ROI adjustment, metric displays, and tabular logs.</td>
      <td><code>dashboard.py</code> utilizes <code>st.empty()</code> containers for atomic DOM element updates without entire page flickering; multi-column layout for side-by-side feed and telemetry.</td>
    </tr>
    <tr>
      <td><strong>NumPy 2.5 & Pandas 3.0</strong></td>
      <td>Vectorized geometric computations and time-series event telemetry.</td>
      <td>NumPy accelerates bounding box matrix calculations (footpoint slicing, coordinates transformations). Pandas organizes state-transition timestamps and powers the empirical evaluation suite.</td>
      <td><code>boxes.xyxy.cpu().numpy()</code> for vector manipulation; <code>pd.DataFrame</code> for event logs and accuracy evaluation metric exports.</td>
    </tr>
    <tr>
      <td><strong>PyTorch 2.14</strong></td>
      <td>Deep learning tensor runtime.</td>
      <td>Executes the YOLOv11 forward-pass, automatically utilizing NVIDIA CUDA GPU acceleration when present and seamlessly falling back to optimized CPU vector instructions.</td>
      <td>Underlying execution engine for <code>ultralytics</code>.</td>
    </tr>
    <tr>
      <td><strong>LAP (Lapjv)</strong></td>
      <td>Linear Assignment Problem solver.</td>
      <td>Computes optimal bipartite matching between predicted Kalman filter trajectories and detected bounding boxes in $O(N^3)$ polynomial time.</td>
      <td>Core backend algorithmic engine utilized by ByteTrack for identity association.</td>
    </tr>
  </tbody>
</table>

<!-- Section 3 -->
<div class="page-break"></div>
<h2>3. Mathematical & Algorithmic Foundations</h2>

<h3>3.1 Normalized Coordinate Space and Region of Interest (ROI)</h3>
<p>
Surveillance video resolutions vary across transit deployments (e.g., 720p, 1080p, 4K). To maintain camera-agnostic portability, the Region of Interest is defined in normalized unit space:
</p>
<div class="formula-box">
  $\text{ROI} = \{ (x, y) \in [0, 1] \times [0, 1] \mid \text{left} \le x \le \text{right} \quad \text{and} \quad \text{top} \le y \le \text{bottom} \}$
</div>
<p>
When applied to a video frame of pixel dimensions $W \times H$, the absolute pixel boundaries are computed via rounding:
</p>
<div class="formula-box">
  $(x_{\min}, y_{\min}, x_{\max}, y_{\max}) = \big( \lfloor \text{left} \cdot W \rceil, \; \lfloor \text{top} \cdot H \rceil, \; \lfloor \text{right} \cdot W \rceil, \; \lfloor \text{bottom} \cdot H \rceil \big)$
</div>

<h3>3.2 Footpoint Formulation: Ground-Contact Geometric Filtering</h3>
<p>
A frequent source of counting error in overhead surveillance systems is upper-body perspective overlap: an individual walking <em>outside</em> the monitored zone may cast a bounding box that intersects the ROI if their head or torso leans across the boundary.
</p>
<div class="callout success">
  <div class="callout-title">The Footpoint Advantage Over Bounding Box Centroids</div>
  <p>
    Standard naive counting checks whether the box centroid $\left(\frac{x_1+x_2}{2}, \frac{y_1+y_2}{2}\right)$ is inside the polygon. In CCTV cameras angled obliquely downwards, a person standing outside the ROI will have their torso falsely projected inside. 
    MetroGuard AI isolates the <strong>bottom-center point (footpoint)</strong> as a reliable proxy for physical floor contact:
  </p>
  <div class="formula-box" style="margin: 6px 0;">
    $\mathbf{p}_{\text{foot}} = \left( \frac{x_1 + x_2}{2}, \; y_2 \right)$
  </div>
  <p>
    The containment predicate evaluates strictly:
  </p>
  <div class="formula-box" style="margin: 6px 0;">
    $\text{Contains}(\text{ROI}, \text{box}) \iff \big(x_{\min} \le \frac{x_1 + x_2}{2} \le x_{\max}\big) \land \big(y_{\min} \le y_2 \le y_{\max}\big)$
  </div>
</div>

<h3>3.3 Operational Density State Machine</h3>
<p>
Raw person counts are mapped into actionable operational security states via configurable boundary thresholds ($T_{\text{med}}$ and $T_{\text{high}}$):
</p>
<div class="formula-box">
  $\text{State}(C) = \begin{cases} 
  \mathbf{LOW} & \text{if } C < T_{\text{med}} \\
  \mathbf{MEDIUM} & \text{if } T_{\text{med}} \le C < T_{\text{high}} \\
  \mathbf{HIGH} & \text{if } C \ge T_{\text{high}}
  \end{cases}$
</div>
<p>
Whenever $\text{State}(C_t) \ne \text{State}(C_{t-1})$, an asynchronous event trigger is dispatched with timestamp telemetry to alert the control room of an emerging bottleneck.
</p>

<h3>3.4 Image-Space Occupancy Metric</h3>
<p>
Because camera calibration matrices and ground-plane homography are not assumed in Phase-I, the project reports normalized image-space occupancy:
</p>
<div class="formula-box">
  $\text{Occupancy per Megapixel} = \frac{C}{\text{Area}_{\text{ROI}}(\text{Mpx})} = \frac{C}{\frac{(x_{\max} - x_{\min}) \cdot (y_{\max} - y_{\min})}{1\,000\,000}}$
</div>

<!-- Section 4 -->
<div class="page-break"></div>
<h2>4. Detailed Codebase & File-by-File Analysis</h2>

<p>The codebase is architected with clear separation between core computer vision algorithms, interactive graphical interfaces, headless execution utilities, and statistical evaluation suites.</p>

<h3>4.1 <code>metroguard/monitor.py</code> (The Core Engine)</h3>
<p>This module implements all detection, tracking, geometric filtering, and annotation primitives.</p>
<ul>
  <li>
    <strong><code>ROI</code> (frozen dataclass):</strong> Stores normalized coordinates <code>left, top, right, bottom</code> with boundary validation (asserting $0 \le \text{left} < \text{right} \le 1$). Provides <code>pixels(width, height)</code> for absolute coordinate conversion, <code>contains_footpoint(box, width, height)</code> for ground-contact testing, and <code>area_megapixels()</code>.
  </li>
  <li>
    <strong><code>MonitorConfig</code> (frozen dataclass):</strong> Encapsulates runtime parameters: <code>model_path</code>, <code>confidence</code> (default 0.35), <code>imgsz</code> (default 1280 to retain high recall for distant passengers), <code>medium_min</code> (default 8), <code>high_min</code> (default 16), <code>roi</code>, and <code>tracker</code> (<code>bytetrack.yaml</code>).
  </li>
  <li>
    <strong><code>FrameResult</code> (dataclass):</strong> Output payload per processed frame, containing <code>frame_index</code>, <code>timestamp_sec</code>, the annotated <code>frame</code> (NumPy ndarray), <code>person_count</code>, <code>density_level</code>, <code>occupancy_per_mpx</code>, list of <code>tracked_ids</code>, and state transition <code>event</code> message.
  </li>
  <li>
    <strong><code>locate_default_model()</code>:</strong> Robust weight resolution utility. Sequentially searches the <code>METROGUARD_MODEL</code> environment variable, local project <code>models/yolo11s.pt</code>, and the local legacy cache (<code>C:\Users\akhia\Downloads\metroguard1\yolo11s.pt</code>), falling back to automatic download.
  </li>
  <li>
    <strong><code>CrowdMonitor</code> (Core Orchestration Class):</strong>
    <ul>
      <li><code>__init__(config)</code>: Instantiates YOLO and isolates the configuration directory to project-local <code>.ultralytics</code> to prevent write permission failures in enterprise/lab environments.</li>
      <li><code>analyze(frame, index, timestamp)</code>: Calls <code>model.track(classes=[0], conf=conf, imgsz=imgsz)</code>, parses bounding boxes and track IDs, executes footpoint filtering inside the ROI, computes occupancy, updates the state transition machine, and renders annotations.</li>
      <li><code>stream(source, max_frames)</code>: Generator yielding <code>FrameResult</code> objects frame-by-frame from video files or live RTSP/webcam feeds.</li>
      <li><code>_annotate(frame, selected, count, level)</code>: Renders a color-coded transparent HUD overlay (Green for LOW, Orange for MEDIUM, Crimson for HIGH), active ROI boundaries, bounding boxes with track IDs and confidence, and an executive top status banner.</li>
    </ul>
  </li>
</ul>

<h3>4.2 <code>dashboard.py</code> (Streamlit Operator Console)</h3>
<p>Provides a browser-based operations interface designed for transit monitoring rooms.</p>
<ul>
  <li><strong>Layout Structure:</strong> Responsive wide-screen layout. Features a dedicated <em>Detection & Zone Settings</em> sidebar for tuning thresholds, confidence, inference resolution, and ROI boundaries.</li>
  <li><strong>Centered Ingestion Portal:</strong> The main center area provides side-by-side video upload (drag-and-drop) and local video path entry (with auto-complete placeholders for sample crowd clips), topped by a prominent "Start Monitoring" control.</li>
  <li><strong>Real-Time Display Loop:</strong> Uses Streamlit's <code>st.empty()</code> reactive placeholders to update the video stream and metric cards (<em>People in ROI</em>, <em>Density Status</em>, <em>System Heartbeat</em>) frame-by-frame without browser page reloads.</li>
  <li><strong>Live Transition Event Log:</strong> Dynamically populates a descending chronological event table highlighting every density state transition with sub-second timestamps.</li>
</ul>

<h3>4.3 <code>run_video.py</code> (Headless Batch Processor)</h3>
<p>Engineered for backend processing, server scripts, and CI/CD pipelines.</p>
<ul>
  <li>Accepts input sources (local file, RTSP network camera, or device index) and parameters via <code>argparse</code>.</li>
  <li>Streams frames through <code>CrowdMonitor</code>, writing the annotated visual stream to disk via <code>cv2.VideoWriter</code> using the <code>mp4v</code> codec.</li>
  <li>Logs real-time density change events to stdout and emits summary statistics upon completion.</li>
</ul>

<h3>4.4 <code>evaluate_counting.py</code> (Empirical Scoring Suite)</h3>
<p>Provides a scientifically defensible method for measuring counting accuracy without requiring external ground-truth bounding-box annotations.</p>
<ul>
  <li><strong><code>prepare</code> sub-command:</strong> Uniformly samples $N$ frames across the video. Exports raw frames, model-annotated frames, and <code>roi_guides/</code> (which show <em>only</em> the ROI boundary with no model predictions to eliminate human confirmation bias during manual counting). Generates a blank <code>count_labels.csv</code>.</li>
  <li><strong><code>score</code> sub-command:</strong> Compares human counts against model predictions, calculating MAE, RMSE, Mean Signed Error (detecting under-counting or over-counting bias), WAPE, and overall accuracy percentage.</li>
</ul>

<!-- Section 5 -->
<div class="page-break"></div>
<h2>5. Empirical Evaluation Methodology & Metrics</h2>

<p>
Object detection benchmark metrics like mAP (Mean Average Precision) require fully annotated bounding boxes for every person in every frame. In real-world metro surveillance deployments, obtaining box annotations is prohibitively expensive. MetroGuard AI Phase-I implements an <strong>ROI Counting Accuracy Protocol</strong>:
</p>

<table>
  <thead>
    <tr>
      <th style="width: 25%;">Metric</th>
      <th style="width: 35%;">Mathematical Definition</th>
      <th style="width: 40%;">Operational Significance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>MAE</strong><br>(Mean Absolute Error)</td>
      <td>$\text{MAE} = \frac{1}{N} \sum_{i=1}^N |\hat{y}_i - y_i|$</td>
      <td>Average number of people by which the model's estimate deviates from the true manual head count per frame.</td>
    </tr>
    <tr>
      <td><strong>RMSE</strong><br>(Root Mean Squared Error)</td>
      <td>$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)^2}$</td>
      <td>Penalizes large outlier estimation errors more heavily than small fluctuations.</td>
    </tr>
    <tr>
      <td><strong>Mean Signed Error</strong><br>(Bias Indicator)</td>
      <td>$\text{Bias} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)$</td>
      <td>Determines whether the detector has a systemic tendency to under-count ($\text{Bias} < 0$) due to occlusion or over-count ($\text{Bias} > 0$) due to false positive detections.</td>
    </tr>
    <tr>
      <td><strong>WAPE</strong><br>(Weighted Absolute % Error)</td>
      <td>$\text{WAPE} = \frac{\sum_{i=1}^N |\hat{y}_i - y_i|}{\sum_{i=1}^N y_i}$</td>
      <td>Total absolute error normalized by the total crowd volume. Avoids division-by-zero instability common in standard MAPE when frame counts are small.</td>
    </tr>
    <tr>
      <td><strong>Counting Accuracy %</strong></td>
      <td>$\text{Accuracy} = \max\left(0, \; 100 \times (1 - \text{WAPE})\right)$</td>
      <td>Executive headline metric representing total fidelity of the crowd estimation within the monitored zone.</td>
    </tr>
  </tbody>
</table>

<!-- Section 6 -->
<h2>6. Project Presentation & Viva Defense Guide</h2>

<div class="callout">
  <div class="callout-title">Key Talking Points for Presentation Slides</div>
  <ol>
    <li><strong>Practical Focus:</strong> Highlight that MetroGuard solves the immediate, mission-critical problem of station congestion and surge management using existing CCTV infrastructure.</li>
    <li><strong>Algorithmic Integrity:</strong> Emphasize the footpoint ground-contact filter, which prevents false alarms caused by people walking outside the platform area.</li>
    <li><strong>Tracking Reliability:</strong> Explain how ByteTrack preserves commuter identity through dense occlusions, preventing double-counting or erratic metric jumping.</li>
    <li><strong>Scientific Grounding:</strong> Showcase the <code>evaluate_counting.py</code> tool to prove that accuracy claims are grounded in reproducible empirical testing, not speculative marketing.</li>
  </ol>
</div>

<h3>Anticipated Technical Questions & Model Answers</h3>

<p><strong>Q1: Why use YOLOv11s instead of YOLOv11x or a heavier Vision Transformer?</strong><br>
<em>Answer:</em> Real-time transit safety requires low-latency inference (typically $\ge 20$ FPS per camera). YOLOv11s achieves optimal Pareto-efficiency: high recall for human commuters while maintaining low computational overhead, enabling multiple video streams to run concurrently on standard GPU hardware or edge accelerators. Furthermore, by increasing inference resolution to <code>imgsz=1280</code>, small and distant commuters are reliably detected without incurring the latency penalty of larger model backbones.</p>

<p><strong>Q2: Why does the system report "occupancy per megapixel" rather than "people per square meter"?</strong><br>
<em>Answer:</em> Calculating physical density ($\text{people}/\text{m}^2$) requires calculating a homography matrix from camera calibration and measuring real-world floor landmarks. Reporting physical density without camera calibration produces mathematically invalid figures. MetroGuard AI reports true image-space occupancy in Phase-I and provides configurable operational thresholds ($T_{\text{med}}$, $T_{\text{high}}$) that operators calibrate per installed camera.</p>

<p><strong>Q3: How does ByteTrack handle commuter occlusion on crowded platforms?</strong><br>
<em>Answer:</em> Traditional trackers (like SORT or DeepSORT) discard detections whose confidence score falls below a fixed threshold (e.g., 0.5). When commuters overlap, their confidence often drops to 0.2–0.4 due to partial visibility, causing classic trackers to drop the track and create a new ID upon reappearance. ByteTrack performs two-stage association: it matches high-confidence boxes first, and then matches remaining unmatched tracks against the low-confidence detections, preserving track continuity through heavy crowd occlusions.</p>

<!-- Section 7 -->
<div class="page-break"></div>
<h2>7. System Requirements & Operational Verification</h2>

<h3>7.1 Environment Setup</h3>
<pre><code># Create and activate Python 3.12 virtual environment
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

# Install core runtime dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt</code></pre>

<h3>7.2 Quick Run Commands</h3>
<table>
  <thead>
    <tr>
      <th style="width: 30%;">Operational Mode</th>
      <th style="width: 70%;">Execution Command</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Interactive Dashboard</strong></td>
      <td><code>.\\.venv\\Scripts\\python.exe -m streamlit run dashboard.py</code></td>
    </tr>
    <tr>
      <td><strong>CLI Video Processing</strong></td>
      <td><code>.\\.venv\\Scripts\\python.exe run_video.py "path\\to\\crowd_clip.mp4" --max-frames 150</code></td>
    </tr>
    <tr>
      <td><strong>Evaluation (Sampling)</strong></td>
      <td><code>.\\.venv\\Scripts\\python.exe evaluate_counting.py prepare "path\\to\\video.mp4" --samples 20</code></td>
    </tr>
    <tr>
      <td><strong>Evaluation (Scoring)</strong></td>
      <td><code>.\\.venv\\Scripts\\python.exe evaluate_counting.py score evaluation/count_labels.csv</code></td>
    </tr>
  </tbody>
</table>

<h3>7.3 Phase-II Evolution Roadmap</h3>
<ul>
  <li><strong>Four-Point Planar Homography:</strong> Allow operators to click four ground points on the dashboard to map 2D camera perspective coordinates directly to 3D station floor blueprints, enabling physical $\text{people}/\text{m}^2$ density calculations.</li>
  <li><strong>Multi-Zone Polygonal ROIs:</strong> Support arbitrary convex polygons (e.g., platform edge hazard zones, escalator entry queues) with differentiated alert thresholds.</li>
  <li><strong>TensorRT Acceleration:</strong> Export the YOLOv11s weights to FP16 TensorRT engine formats for high-density multi-camera edge server deployments.</li>
</ul>

<hr style="border: none; border-top: 1px solid #cbd5e1; margin-top: 30px;">
<div style="text-align: center; font-size: 8.5pt; color: #64748b;">
  MetroGuard AI — Phase-I Crowd Density Monitoring System &bull; Technical Architecture Documentation
</div>

</body>
</html>
"""

# Write HTML file
with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML written to {HTML_OUTPUT}")

# Convert to PDF using Microsoft Edge headless
edge_paths = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
]

browser_exe = None
for p in edge_paths:
    if os.path.exists(p):
        browser_exe = p
        break

if not browser_exe:
    raise RuntimeError("No headless browser found to convert HTML to PDF.")

cmd = [
    browser_exe,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_OUTPUT}",
    str(HTML_OUTPUT)
]

print(f"Compiling PDF with {browser_exe}...")
result = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(PDF_OUTPUT):
    size_kb = os.path.getsize(PDF_OUTPUT) / 1024
    print(f"SUCCESS: PDF created at {PDF_OUTPUT} ({size_kb:.1f} KB)")
else:
    print(f"ERROR: PDF conversion failed.\nStdout: {result.stdout}\nStderr: {result.stderr}")
