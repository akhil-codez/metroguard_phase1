# MetroGuard AI — Phase-I Crowd Density Prototype

This is the initial technical implementation for MetroGuard AI. It is deliberately scoped to a single, demonstrable module:

```text
Video / camera → YOLOv11 person detections → ByteTrack IDs → count within ROI → LOW / MEDIUM / HIGH → annotated feed + dashboard
```

## What the prototype does

- Uses **YOLOv11** to detect the COCO `person` class only. It defaults to 1280-pixel inference to retain more detail for distant people in 1080p CCTV footage; choose 640 only when speed matters more than recall.
- Uses the Ultralytics **ByteTrack** integration to maintain short-term person IDs across frames.
- Counts people whose **bottom-centre point** (a simple ground-contact proxy) falls inside the configured camera ROI.
- Derives an operational **LOW / MEDIUM / HIGH** occupancy level from configurable person-count thresholds.
- Draws boxes, track IDs, the active ROI, count, and density level on the output.
- Provides a Streamlit operator dashboard with a video feed, count, density status, system status, and density-transition event log.

## What it does not claim

The Phase-I module does **not** detect fights, unattended bags, anomalies, passenger behaviour, or incidents. It also does not estimate people per square metre: without camera calibration and a ground-plane mapping, the displayed `people / ROI megapixel` is an **image-space occupancy indicator**, not physical density. The LOW/MEDIUM/HIGH labels are operational count thresholds that should be calibrated per camera in later work.

## Existing local material found

The project does not copy or modify your earlier work. It can directly use the local YOLO model already present at:

`C:\Users\akhia\Downloads\metroguard1\yolo11s.pt`

Suitable Phase-I crowd inputs already present there include:

- `C:\Users\akhia\Downloads\metroguard1\data\crowd\people_walking.mp4`
- `C:\Users\akhia\Downloads\metroguard1\data\crowd\market_square.mp4`

The dashboard will preselect the local weights when that file exists. You can upload one of these videos in the dashboard or paste its path.

## First-time environment setup

Use Python 3.10–3.12. From this folder, use the commands matching your terminal.

**Command Prompt (`cmd`)**

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `python` is not recognised on your computer, install Python 3.12 from python.org, reopen PowerShell, and repeat the commands.

## Run the dashboard

```powershell
.venv\Scripts\python.exe -m streamlit run dashboard.py
```

In the browser: upload a crowd video (or paste a local path), set the rectangular ROI and thresholds, then choose **Start monitoring**.

## Run from the command line

```powershell
.venv\Scripts\python run_video.py "C:\Users\akhia\Downloads\metroguard1\data\crowd\people_walking.mp4" --max-frames 150
```

The annotated result is written to `data\output\annotated_crowd.mp4`. For the first test, use `--max-frames 150`; omit it for the full video.

## Calculate count accuracy

There are no ground-truth annotations for the supplied MetroGuard crowd clips, so an accuracy percentage cannot be inferred from the model output or a dashboard screenshot. Use this reproducible manual-count protocol for the exact camera video:

```bat
.venv\Scripts\python.exe evaluate_counting.py prepare "C:\Users\akhia\Downloads\metroguard1\data\crowd\people_walking.mp4" --output evaluation_people_walking --samples 20 --roi 0.12,0.12,0.95,0.95
```

Count every person inside the yellow ROI in each image under `evaluation_people_walking\roi_guides` (these frames have an ROI guide but no model boxes), then enter those counts into the blank `ground_truth_count` column of `count_labels.csv`. Do not use the annotated images to create the ground truth. Then calculate the report:

```bat
.venv\Scripts\python.exe evaluate_counting.py score evaluation_people_walking\count_labels.csv
```

The report gives mean absolute error (MAE), RMSE, under/over-count bias, WAPE, and `count_accuracy_percent = 100 × (1 − WAPE)`. This is **counting accuracy for the ROI**, not object-detection mAP; mAP additionally requires manually drawn bounding boxes for every person.

## Suggested Phase-I demonstration settings

Start with the default ROI, set `Medium from` to **8** people and `High from` to **16** people, then tune them for the chosen camera. Record the camera, ROI percentage, thresholds, model (`YOLOv11s`), confidence threshold, and input video for reproducibility. A later Phase-II study should calibrate the ROI to physical floor area and evaluate count error against manually annotated frames.
