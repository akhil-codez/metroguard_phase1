# Phase-I Method and Evidence Notes

## Processing definition

For each input frame, YOLOv11s detects only COCO class `0` (`person`). The Ultralytics implementation of ByteTrack assigns short-lived IDs to detections across sequential frames. A person contributes to the ROI count only when the bottom-centre of their bounding box lies within the selected rectangular camera zone.

`occupancy count(t) = number of tracked person detections whose footpoint is inside ROI at time t`

The operational density label is derived from that count:

| Label | Rule (default) |
|---|---|
| LOW | count < 8 |
| MEDIUM | 8 ≤ count < 16 |
| HIGH | count ≥ 16 |

The thresholds are editable in the dashboard and command line. They must be tuned independently for each installed camera.

## Valid interpretation

The system produces **image-space crowd occupancy**. `people / ROI-megapixel` is included solely as a normalized image-space indicator. It is not people per square metre, because physical density requires camera calibration, a ground-plane homography, and a known floor-area ROI. This prototype makes no claims about incident reasoning, violence, abandoned objects, or abnormal behaviour.

YOLOv11s can undercount small, distant, overlapping, or occluded pedestrians. The dashboard now defaults to 1280-pixel inference for 1080p input at a processing-speed cost, labels the count as an estimate, and retains every detected box for review. Accuracy claims require comparison against manual counts on sampled frames and reported MAE.

## Suggested demonstration record

Record the following for each Phase-I demo run:

| Field | Record |
|---|---|
| Video/source and permissions | |
| Camera resolution and viewpoint | |
| YOLO weights and confidence threshold | |
| ROI (left, top, right, bottom %) | |
| LOW/MEDIUM/HIGH thresholds | |
| Frames tested / processing rate | |
| Manual count on 20 sampled frames | |
| Observed false positives / missed people | |

For a simple preliminary evaluation, manually count people on 20 evenly spaced frames and report mean absolute count error: `MAE = mean(|predicted count − manual count|)`. This keeps the Phase-I evidence limited to what the module actually measures.

For a single percentage, use weighted absolute percentage error (WAPE):

`WAPE = sum(|predicted count − manual count|) / sum(manual count)`

The project reports `count accuracy = 100 × (1 − WAPE)`, floored at zero. State clearly that this is ROI count accuracy, not detection mAP.
