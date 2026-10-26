# MetroGuard AI
## A Multi-Event Incident Intelligence Platform for Smart Metro Surveillance

---

## 1. Project Vision

MetroGuard AI is a real-time intelligent surveillance system designed for metro environments.

Instead of treating every detected event as an independent alert, MetroGuard:

> **Detects → Tracks → Interprets → Correlates → Assesses Risk → Prioritizes → Explains**

The initial project will focus on **three major metro-safety events**:

1. **Fight / Physical Altercation Detection**
2. **Crowd Density Monitoring**
3. **Abandoned Object Detection**

The system will combine these independent event outputs through a **Context-Aware Incident Intelligence Engine**.

The important research idea is not simply detecting these three events. Existing research already addresses individual event detection. MetroGuard's focus is on determining:

> **"Are these detected events related, how serious is the combined situation, and which incident should security personnel respond to first?"**

---

# 2. Final System Architecture

```text
                    ┌──────────────────────┐
                    │    CCTV / Video      │
                    │        Input         │
                    └──────────┬───────────┘
                               │
                               ▼
                 ┌─────────────────────────┐
                 │ Video Preprocessing      │
                 │ • Frame extraction      │
                 │ • Resize / normalize    │
                 └──────────┬──────────────┘
                            │
                            ▼
              ┌──────────────────────────────┐
              │ YOLO11 Object Detection      │
              │ + ByteTrack Tracking         │
              └────────────┬─────────────────┘
                           │
           ┌───────────────┼────────────────┐
           │               │                │
           ▼               ▼                ▼
    ┌─────────────┐ ┌─────────────┐ ┌────────────────┐
    │ Fight       │ │ Crowd       │ │ Abandoned      │
    │ Detection   │ │ Monitoring  │ │ Object         │
    │             │ │             │ │ Detection      │
    └──────┬──────┘ └──────┬──────┘ └───────┬────────┘
           │               │                 │
           └───────────────┼─────────────────┘
                           ▼
              ┌────────────────────────────┐
              │ Event Representation Layer │
              │ • Event type               │
              │ • Timestamp                │
              │ • Camera ID                │
              │ • Location / Zone          │
              │ • Track IDs                │
              │ • Confidence               │
              │ • Duration                 │
              └──────────────┬─────────────┘
                             │
                             ▼
          ┌────────────────────────────────────┐
          │ Context-Aware Incident Intelligence│
          │ Engine                             │
          │                                    │
          │ • Temporal correlation             │
          │ • Spatial correlation              │
          │ • Event co-occurrence              │
          │ • Context analysis                 │
          │ • Risk calculation                 │
          │ • Incident grouping               │
          └──────────────────┬─────────────────┘
                             │
                             ▼
              ┌────────────────────────────┐
              │ Incident Prioritization    │
              │                            │
              │ P1 — Critical              │
              │ P2 — High                  │
              │ P3 — Medium                │
              │ P4 — Low                   │
              └──────────────┬─────────────┘
                             │
                             ▼
             ┌───────────────────────────────┐
             │ Explainable Incident Report  │
             │                               │
             │ What happened?               │
             │ Where?                       │
             │ When?                        │
             │ Which events are related?    │
             │ Why is it high risk?         │
             └──────────────┬────────────────┘
                            │
                            ▼
               ┌──────────────────────────┐
               │ MetroGuard Dashboard     │
               │ + Alerts + Incident Log  │
               └──────────────────────────┘
```

---

# 3. Development Philosophy

Do **not** try to develop everything simultaneously.

Build MetroGuard in layers:

### Layer 1 — Detection

Make each individual detector work.

### Layer 2 — Tracking

Give people and objects persistent IDs.

### Layer 3 — Event Generation

Convert model predictions into meaningful events.

### Layer 4 — Context

Add time, location, duration and relationships.

### Layer 5 — Incident Fusion

Combine related events.

### Layer 6 — Risk Assessment

Calculate severity.

### Layer 7 — Dashboard

Present the result to an operator.

This modular structure makes debugging and evaluation much easier.

---

# 4. Module 1 — Video Input

## Objective

Accept video from:

- CCTV video files
- Webcam
- Recorded metro footage
- Synthetic CCTV videos
- Eventually RTSP/IP camera streams

For the initial project, **video files are enough**.

### Recommended tools

- Python
- OpenCV
- NumPy

### Processing pipeline

```text
Video
 ↓
OpenCV VideoCapture
 ↓
Frame
 ↓
Resize
 ↓
Inference
 ↓
Event analysis
 ↓
Display / Store
```

Do not start with live CCTV.

First make the complete system work on recorded videos.

---

# 5. Module 2 — Object Detection

## Recommended model

**YOLO11**

The detector should initially identify:

- person
- backpack
- suitcase
- handbag / relevant luggage objects

You can later add additional classes if required.

The purpose of YOLO here is not to detect "incidents."

It provides the basic visual information needed by the downstream modules.

Example:

```text
Frame 1032

Person      → confidence 0.94
Person      → confidence 0.91
Backpack    → confidence 0.87
Person      → confidence 0.89
```

The project should maintain the distinction:

> **Object detection ≠ incident detection**

---

# 6. Module 3 — ByteTrack

Use ByteTrack to maintain identities across frames.

Ultralytics currently supports ByteTrack directly as a tracking backend and describes it as a lightweight tracker particularly suitable for static or near-static cameras. [Ultralytics tracking documentation](https://docs.ultralytics.com/modes/track?utm_source=chatgpt.com)

Example:

```text
Frame 1:
Person → ID 12

Frame 2:
Person → ID 12

Frame 3:
Person → ID 12

Frame 4:
Person → ID 12
```

This is critical because MetroGuard needs to know:

- who moved away from a bag
- how long a bag has remained stationary
- how many people are around an incident
- which people are involved in a fight
- how crowd density changes over time

---

# 7. Module 4 — Fight Detection

## Goal

Detect physical altercations from video sequences.

Do not attempt to classify a single frame as "fight."

A fight is fundamentally a **temporal activity**.

Recommended pipeline:

```text
Video frames
     ↓
Person detection
     ↓
Person tracking
     ↓
Motion / pose information
     ↓
Temporal sequence
     ↓
Fight classifier
     ↓
Fight probability
```

## Possible implementation

### Option A — Start simple

Use a pretrained / publicly available fight-detection model or train a lightweight temporal classifier using a suitable fight dataset.

### Option B — Research-oriented

Use:

- YOLO11 for people
- pose estimation
- temporal CNN / LSTM / 3D CNN

The literature supports temporal and pose/motion-based approaches for violence recognition.

Your MetroGuard implementation should initially prioritize **reliable detection over architectural complexity**.

---

# 8. Fight Event Representation

The fight model should not directly send:

```text
FIGHT = TRUE
```

Instead create a structured event:

```json
{
  "event_id": "F001",
  "event_type": "FIGHT",
  "camera_id": "CAM03",
  "timestamp": "10:32:14",
  "zone": "PLATFORM_2_CENTER",
  "track_ids": [12, 17],
  "confidence": 0.91,
  "duration": 8
}
```

This becomes the input to your Incident Intelligence Engine.

---

# 9. Module 5 — Crowd Density Monitoring

Your uploaded 2025 IADL-CDE paper is highly relevant here.

It combines crowd-density classification with anomaly detection and uses ShanghaiTech and UCSD datasets. The paper specifically classifies crowd density into sparse, medium and dense categories and argues for density-aware anomaly interpretation.

MetroGuard can simplify this into:

```text
Person detections
       ↓
Count / density estimation
       ↓
Density classification
       ↓
Sparse / Medium / High
```

## Initial implementation

Start with person counting.

Example:

```text
Zone A → 12 people → LOW
Zone B → 38 people → MEDIUM
Zone C → 74 people → HIGH
```

Later you can improve this using:

- perspective correction
- density maps
- dedicated crowd-counting models

---

# 10. Crowd Context Is More Important Than Crowd Alone

This is an important MetroGuard concept.

A high crowd does **not automatically mean danger**.

Example:

```text
Train arrives
      ↓
Passenger count increases
      ↓
HIGH CROWD
      ↓
Normal situation
```

But:

```text
Fight detected
      ↓
People gather
      ↓
HIGH CROWD
      ↓
Potential escalation
```

Therefore:

> Crowd density should be treated as **context**, not necessarily as an incident by itself.

This is one of the strongest reasons for having an Incident Intelligence Engine.

---

# 11. Crowd Event Representation

```json
{
  "event_id": "C014",
  "event_type": "HIGH_CROWD",
  "camera_id": "CAM03",
  "timestamp": "10:32:17",
  "zone": "PLATFORM_2_CENTER",
  "person_count": 67,
  "density_level": "HIGH",
  "confidence": 0.88
}
```

---

# 12. Module 6 — Abandoned Object Detection

Your uploaded paper:

**Abandoned Object Detection and Classification Using Deep Embedded Vision**

is directly relevant to this module.

The paper proposes a two-stage system involving temporal classification and YOLOv8l localization, and evaluates on PETS 2006 and ABODA.

MetroGuard should preserve the important concept:

> An object is not abandoned merely because it is detected.

It must satisfy temporal and ownership-related conditions.

---

# 13. Abandoned Object Logic

Use:

```text
Object detected
      ↓
Track object
      ↓
Is object stationary?
      ↓
YES
      ↓
Was associated person nearby?
      ↓
Person moves away
      ↓
Timer starts
      ↓
No owner returns
      ↓
ABANDONED OBJECT EVENT
```

For example:

```text
Backpack detected → 10:32:00
Owner detected     → ID 31

Owner moves away  → 10:32:12

Distance > threshold

Stationary duration → 30 sec
```

Then:

```text
ABANDONED_OBJECT = TRUE
```

For a real deployment, the threshold should be configurable rather than hard-coded.

---

# 14. Abandoned Object Event Representation

```json
{
  "event_id": "A008",
  "event_type": "ABANDONED_OBJECT",
  "camera_id": "CAM03",
  "timestamp": "10:32:25",
  "zone": "PLATFORM_2_CENTER",
  "object_type": "BACKPACK",
  "object_track_id": 42,
  "owner_track_id": 31,
  "stationary_duration": 25,
  "confidence": 0.94
}
```

---

# 15. The Most Important Layer — Event Representation

This layer connects all three models.

Every detector should produce a common event format.

### Common schema

```text
Event ID
Event Type
Camera ID
Timestamp
Zone
Track IDs
Confidence
Duration
Bounding Box
Additional Attributes
```

For example:

```text
F001
FIGHT
CAM03
10:32:14
PLATFORM_2_CENTER
Tracks: 12,17
0.91
8 sec
```

```text
C014
HIGH_CROWD
CAM03
10:32:17
PLATFORM_2_CENTER
67 people
0.88
```

```text
A008
ABANDONED_OBJECT
CAM03
10:32:25
PLATFORM_2_CENTER
Backpack
0.94
25 sec
```

Now the fusion engine has structured information instead of raw model outputs.

---

# 16. Module 7 — Context-Aware Incident Intelligence Engine

This is the **heart of MetroGuard**.

The engine asks:

### Temporal question

Did the events occur close together?

```text
Fight: 10:32:14
Crowd: 10:32:17
Bag:   10:32:25

Temporal relationship = STRONG
```

### Spatial question

Did they occur in the same zone?

```text
Fight → Platform 2 Center
Crowd → Platform 2 Center
Bag   → Platform 2 Center

Spatial relationship = STRONG
```

### Semantic question

Do the events make sense together?

```text
Fight + Crowd
```

is potentially related.

But:

```text
Fight Platform 2
+
Bag Platform 5
```

should not automatically be fused.

---

# 17. Spatial Correlation

Start with simple zones.

Divide the platform into:

```text
┌─────────────┬─────────────┬─────────────┐
│   Zone A    │   Zone B    │   Zone C    │
│             │             │             │
├─────────────┼─────────────┼─────────────┤
│   Zone D    │   Zone E    │   Zone F    │
│             │             │             │
└─────────────┴─────────────┴─────────────┘
```

Each event receives a zone.

Then:

```text
Same zone → strong relationship
Adjacent zone → moderate relationship
Far zone → weak/no relationship
```

This is much easier to implement and explain than attempting complicated geographic reasoning initially.

---

# 18. Temporal Correlation

Define a configurable time window.

Example:

```text
Δt ≤ 5 sec      → Strong
5 < Δt ≤ 15 sec → Moderate
15 < Δt ≤ 30 sec → Weak
Δt > 30 sec     → No relation
```

These are **initial engineering parameters**, not scientifically fixed values.

You should tune them experimentally using your dataset.

---

# 19. Event Relationship Score

Create a simple relationship score.

For example:

```text
Relationship Score =
    Spatial Score
  + Temporal Score
  + Event Compatibility
```

Normalize it to:

```text
0 – 100
```

Example:

```text
Fight + Crowd

Spatial relationship      = 35
Temporal relationship     = 30
Event compatibility       = 25

Relationship Score = 90
```

---

# 20. Incident Formation

Suppose the engine receives:

```text
10:32:14 → FIGHT
10:32:17 → HIGH CROWD
10:32:25 → ABANDONED OBJECT
```

and all three occur in:

```text
CAM03
PLATFORM_2_CENTER
```

The engine creates:

```text
INCIDENT_001
```

containing:

```text
FIGHT
HIGH_CROWD
ABANDONED_OBJECT
```

Instead of producing three separate alerts.

---

# 21. False Correlation Example

This is extremely important for your research.

Suppose:

```text
10:32:14
Fight
Platform 2

10:32:17
Abandoned Bag
Platform 5
```

The system should **not** automatically create:

```text
Fight + Abandoned Bag = Critical
```

Instead:

```text
Spatial relation = weak
Temporal relation = strong
Overall relationship = low
```

Therefore:

```text
INCIDENT A → Fight
INCIDENT B → Abandoned Object
```

This demonstrates that MetroGuard is actually performing **contextual reasoning**, rather than simply adding alerts together.

---

# 22. Risk Assessment Engine

Once related events form an incident, calculate risk.

A simple initial model could be:

```text
Risk =
Event Severity
× Confidence
× Context Factor
× Relationship Strength
```

Alternatively, use a weighted score:

```text
Risk Score =
Wf × Fight
+
Wc × Crowd
+
Wa × AbandonedObject
+
Wt × TemporalRelation
+
Ws × SpatialRelation
```

All values should be normalized.

For example:

```text
Fight              = 40
High Crowd         = 20
Abandoned Object   = 25
Temporal relation  = 7
Spatial relation   = 8

Total = 100
```

The actual weights should be determined experimentally and documented as part of your methodology.

---

# 23. Risk Categories

Start with four levels:

```text
0–24     LOW
25–49    MEDIUM
50–74    HIGH
75–100   CRITICAL
```

Again, these are initial thresholds that should be validated experimentally.

---

# 24. Example Risk Scenarios

### Scenario A

```text
High crowd only
```

Risk:

```text
MEDIUM / contextual warning
```

depending on the operating conditions.

---

### Scenario B

```text
Fight only
```

Risk:

```text
HIGH
```

---

### Scenario C

```text
Abandoned object only
```

Risk:

```text
HIGH
```

depending on stationary duration and location.

---

### Scenario D

```text
Fight + High Crowd
```

Risk:

```text
CRITICAL
```

---

### Scenario E

```text
Fight + High Crowd + Abandoned Object
```

Risk:

```text
CRITICAL
```

---

### Scenario F

```text
Fight Platform 2
+
Abandoned Object Platform 5
```

Risk:

```text
Two separate incidents
```

This should become one of your key demonstration scenarios.

---

# 25. Explainability Layer

Do not only display:

```text
CRITICAL ALERT
```

Instead explain why.

Example:

```text
┌────────────────────────────────────┐
│       CRITICAL INCIDENT             │
│                                    │
│ Platform 2 — Camera CAM03          │
│                                    │
│ ✓ Fight detected — 91%             │
│ ✓ High crowd — 67 people           │
│ ✓ Abandoned backpack — 94%         │
│ ✓ Same spatial zone                │
│ ✓ Events within 11 seconds         │
│                                    │
│ Risk Score: 93/100                 │
│ Priority: P1                       │
│                                    │
│ Reason:                             │
│ Multiple high-risk events occurred │
│ within the same platform zone.     │
└────────────────────────────────────┘
```

This is much more impressive in a project demonstration than simply drawing bounding boxes.

---

# 26. Dashboard

The dashboard can be built using:

### Simple option

**Streamlit**

### More advanced

**React + FastAPI**

For a B.Tech project, I recommend:

```text
Python Backend
+
FastAPI
+
Streamlit
+
OpenCV
```

Initially use Streamlit because development is much faster.

---

# 27. Dashboard Layout

### Left

Live/recorded CCTV feed.

### Right

Current incident status:

```text
ACTIVE INCIDENTS

P1  CRITICAL
Platform 2
Fight + Crowd + Bag

P2  HIGH
Platform 4
Abandoned Object

P3  MEDIUM
Platform 1
High Crowd
```

### Bottom

Incident timeline:

```text
10:32:14 Fight
10:32:17 Crowd ↑
10:32:25 Bag detected
10:32:29 Incident formed
10:32:30 Risk = 93
```

---

# 28. Incident Database

Store incidents using SQLite initially.

Tables:

### events

```text
event_id
event_type
camera_id
timestamp
zone
confidence
track_ids
duration
```

### incidents

```text
incident_id
created_at
camera_id
zone
risk_score
priority
status
```

### incident_events

```text
incident_id
event_id
relationship_score
```

This allows you to reconstruct why an incident received its priority.

---

# 29. Dataset Strategy

You do **not** need one gigantic dataset containing all MetroGuard events.

Use a multi-dataset strategy.

### Fight

Use an appropriate public fight/violence dataset.

### Crowd

Your uploaded IADL-CDE paper identifies:

- ShanghaiTech
- UCSD Pedestrian Database

as datasets for crowd density/anomaly analysis.

### Abandoned object

Your uploaded abandoned-object paper evaluates:

- PETS 2006
- ABODA

and therefore gives you a strong starting point for this module.

---

# 30. Synthetic Metro Dataset

This is where your AI-generated CCTV videos can be useful.

Create controlled metro scenarios:

### Group A — Normal

10–15 videos

### Group B — Fight

10 videos

### Group C — Crowd

10 videos

### Group D — Abandoned object

10 videos

### Group E — Fight + crowd

10 videos

### Group F — Crowd + abandoned object

10 videos

### Group G — Fight + abandoned object

10 videos

### Group H — Fight + crowd + abandoned object

10 videos

### Group I — Unrelated simultaneous events

10 videos

Approximately:

**80–100 short synthetic CCTV scenarios**

is a reasonable starting target.

Do not claim these are real-world recordings. Clearly label them:

> Synthetic CCTV scenarios for controlled multi-event incident evaluation.

---

# 31. Why the "Unrelated Events" Dataset Is Important

This is potentially one of the strongest parts of your evaluation.

Create examples like:

```text
Camera 1:
Fight

Camera 2:
Abandoned object
```

or:

```text
Platform 1:
Fight

Platform 3:
High crowd
```

The system should avoid combining them.

Your evaluation can therefore measure:

> **Can MetroGuard distinguish related events from coincidental simultaneous events?**

That is more interesting than simply asking:

> "Can the system detect a fight?"

---

# 32. Incident Dataset

After running your detectors on videos, save structured outputs.

Example CSV:

```text
incident_id
event_types
camera_id
zone
fight_confidence
crowd_level
abandoned_object_confidence
time_difference
spatial_relation
relationship_score
risk_score
priority
ground_truth
```

Example:

```text
INC001,
FIGHT+CROWD,
CAM03,
ZONE_B,
0.91,
HIGH,
0,
3,
STRONG,
87,
CRITICAL,
CRITICAL
```

Another:

```text
INC002,
FIGHT+ABANDONED_OBJECT,
CAM03,
ZONE_B,
0.89,
MEDIUM,
0.92,
8,
STRONG,
82,
CRITICAL,
CRITICAL
```

---

# 33. Training vs Fusion Dataset

This distinction should be clearly stated in your report.

### Individual model training

```text
Public datasets
      ↓
Train individual detectors
```

### Fusion evaluation

```text
Detector outputs
      ↓
Structured event dataset
      ↓
Incident Intelligence Engine
```

The fusion layer initially does **not need to be another deep neural network**.

A rule-based/weighted reasoning engine is easier to:

- explain
- debug
- validate
- demonstrate
- compare

You can later experiment with ML-based fusion if time permits.

---

# 34. Recommended Fusion Implementation — Version 1

Use deterministic rules.

```text
IF
    Fight = TRUE
AND Crowd = HIGH
AND SpatialRelation = STRONG
AND TemporalRelation = STRONG

THEN
    Create CRITICAL INCIDENT
```

Another:

```text
IF
    AbandonedObject = TRUE
AND StationaryDuration > threshold
AND OwnerDistance > threshold

THEN
    Create HIGH INCIDENT
```

Another:

```text
IF
    Fight = TRUE
AND AbandonedObject = TRUE
AND SameZone = TRUE
AND TimeDifference < threshold

THEN
    Create CRITICAL INCIDENT
```

---

# 35. Version 2 — Weighted Fusion

After Version 1 works, introduce numerical scores.

```text
Event Score
+
Spatial Score
+
Temporal Score
+
Confidence
=
Risk Score
```

This gives you a quantitative methodology for evaluation.

---

# 36. Version 3 — Optional ML Fusion

Only attempt this if the rest of the project is already stable.

Input:

```text
fight_confidence
crowd_density
abandoned_object_confidence
time_difference
distance
event_count
duration
```

Output:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Possible models:

- Random Forest
- XGBoost
- Logistic Regression
- Small MLP

You do **not need another deep-learning model**.

A lightweight ML model may actually make more sense because your fusion data is structured/tabular.

---

# 37. Research Contribution

Your project should be presented as:

### Existing research

Individual systems detect:

```text
Fight
Crowd
Abandoned Object
```

### MetroGuard contribution

MetroGuard investigates:

```text
Multiple independent event outputs
            ↓
Temporal + spatial context
            ↓
Event correlation
            ↓
Incident formation
            ↓
Risk assessment
            ↓
Priority
            ↓
Explainable response
```

This avoids the weak claim:

> "We combined three existing models."

Instead:

> "We propose a context-aware incident reasoning framework that transforms heterogeneous event detections into correlated and prioritized metro-security incidents."

---

# 38. Literature Mapping

Your uploaded papers fit the architecture as follows.

### Primary conceptual base

**ABDviaMSIFAT**

It uses multiple information sources, parallel pipelines, contextual information and fuzzy reasoning for abnormal crowd behavior. This is the closest conceptual foundation for MetroGuard's multi-source reasoning layer.

### Crowd module

**Intelligent Anomaly Detection and Localization With Crowd Density Estimation**

Supports density-aware anomaly analysis and public-safety monitoring.

### Abandoned-object module

**Abandoned Object Detection and Classification Using Deep Embedded Vision**

Supports temporal abandoned-object detection and object localization.

### Recent supporting literature

The 2025 IEEE spatio-temporal semantic anomaly work supports combining spatial and temporal semantics rather than considering frames independently.

The 2025 EdgeGuardNet work is particularly relevant to MetroGuard because it combines anomaly detection with **threat-level classification and interpretable security alerts**.

A 2026 IEEE/ACIS paper on AI surveillance also explicitly combines object detection, temporal validation, multi-source fusion and scene interpretation for public-safety surveillance, making it useful as a contemporary supporting reference.

---

# 39. Evaluation Metrics

Do not evaluate only the final "accuracy."

Evaluate each module separately.

## Fight Detection

- Accuracy
- Precision
- Recall
- F1-score
- False Positive Rate
- Detection latency

## Crowd

- MAE / RMSE if doing counting
- Density classification accuracy
- Precision / Recall / F1

## Abandoned Object

- Precision
- Recall
- F1
- Detection delay
- False alarm rate

## Tracking

- ID consistency
- ID switches
- Tracking accuracy where appropriate

## Incident Fusion

This is especially important.

Measure:

### Incident Detection Accuracy

Did MetroGuard identify the correct incident?

### Event Correlation Accuracy

Did it correctly determine which events belong together?

### False Fusion Rate

How often did unrelated events get incorrectly merged?

### Missed Fusion Rate

How often did related events fail to form one incident?

### Risk Classification

Compare predicted:

```text
LOW / MEDIUM / HIGH / CRITICAL
```

against ground truth.

### Response latency

```text
Time of event
      ↓
Time of incident generation
```

This is important because MetroGuard is intended for real-time surveillance.

---

# 40. Most Important Experiment

Your strongest experiment should compare:

### System A

Independent event alerts.

```text
Fight Alert
Crowd Alert
Bag Alert
```

versus

### System B

MetroGuard.

```text
Fight
+
Crowd
+
Bag
↓
One correlated incident
↓
Risk = Critical
↓
P1
```

Then demonstrate:

> **Alert reduction + better prioritization + contextual explanation**

This directly supports your motivation slide.

---

# 41. Demo Scenario

For your final review/demo, use one controlled video.

### Timeline

```text
00:00–00:05
Normal metro platform

00:05–00:12
Fight begins

00:10–00:18
People gather

00:18–00:25
Backpack left behind

00:25–00:35
Owner moves away
```

The dashboard should show:

```text
10:05:12
Fight detected

10:05:17
Crowd → HIGH

10:05:25
Backpack → suspicious

10:05:30
Events correlated

10:05:31
INCIDENT CREATED

Risk Score: 93
Priority: P1
```

Then show a second video:

```text
Fight → Platform 2

Bag → Platform 5
```

and demonstrate that MetroGuard produces:

```text
INCIDENT 001
Fight
Platform 2

INCIDENT 002
Abandoned Object
Platform 5
```

This will be a **very strong demonstration of the fusion concept**.

---

# 42. Suggested Project Folder Structure

```text
MetroGuard/
│
├── data/
│   ├── fight/
│   ├── crowd/
│   ├── abandoned_object/
│   └── synthetic_incidents/
│
├── models/
│   ├── yolo/
│   ├── fight/
│   ├── crowd/
│   └── abandoned_object/
│
├── detection/
│   ├── person_detector.py
│   ├── object_detector.py
│   └── tracker.py
│
├── events/
│   ├── fight_event.py
│   ├── crowd_event.py
│   └── abandoned_object_event.py
│
├── fusion/
│   ├── spatial.py
│   ├── temporal.py
│   ├── correlation.py
│   ├── risk_engine.py
│   └── incident_manager.py
│
├── dashboard/
│   ├── app.py
│   ├── video_view.py
│   └── incident_panel.py
│
├── database/
│   ├── models.py
│   └── database.py
│
├── evaluation/
│   ├── metrics.py
│   └── experiments.py
│
├── configs/
│   └── metroguard.yaml
│
├── main.py
└── requirements.txt
```

---

# 43. Recommended Technology Stack

## Programming

**Python**

## Computer Vision

**OpenCV**

## Object Detection

**Ultralytics YOLO11**

## Tracking

**ByteTrack**

## Deep Learning

**PyTorch**

## Numerical processing

**NumPy**

## Data analysis

**Pandas**

## Fusion

**Python rule engine / custom reasoning layer**

Optionally:

**scikit-learn / XGBoost**

## Backend

**FastAPI**

## Dashboard

**Streamlit**

## Database

**SQLite**

## Visualization

**Plotly / Matplotlib**

---

# 44. Development Phases

## Phase 1 — Environment

Set up:

- Python environment
- PyTorch
- OpenCV
- Ultralytics
- NumPy
- Pandas
- Streamlit
- FastAPI

Deliverable:

> Basic video plays successfully through Python.

---

## Phase 2 — YOLO + ByteTrack

Implement:

```text
Video
 ↓
YOLO11
 ↓
ByteTrack
 ↓
Bounding boxes + IDs
```

Deliverable:

> People and objects have persistent IDs.

---

## Phase 3 — Fight Detection

Train/test fight model.

Deliverable:

```text
Fight probability
```

and:

```text
Fight Event
```

---

## Phase 4 — Crowd Detection

Implement:

```text
Person count
 ↓
Density
 ↓
LOW / MEDIUM / HIGH
```

Deliverable:

> Real-time crowd status.

---

## Phase 5 — Abandoned Object

Implement:

```text
Object
 ↓
Track
 ↓
Stationary duration
 ↓
Owner separation
 ↓
Abandoned
```

Deliverable:

> Abandoned-object event.

---

## Phase 6 — Event Schema

Convert all outputs into a common format.

Deliverable:

> JSON/CSV event stream.

---

## Phase 7 — Context Engine

Implement:

- spatial relationship
- temporal relationship
- event compatibility

Deliverable:

```text
Related / Unrelated
```

---

## Phase 8 — Incident Engine

Implement:

```text
Related Events
 ↓
Incident
```

Deliverable:

```text
INCIDENT_001
```

---

## Phase 9 — Risk Engine

Implement:

```text
Incident
 ↓
Risk Score
 ↓
Priority
```

Deliverable:

```text
93 / 100
P1 Critical
```

---

## Phase 10 — Explainability

Generate:

```text
What happened?
Where?
When?
Which events?
Why related?
Why high risk?
```

Deliverable:

> Explainable incident card.

---

## Phase 11 — Dashboard

Connect:

```text
Video
+
Events
+
Incidents
+
Risk
```

Deliverable:

> Complete MetroGuard interface.

---

## Phase 12 — Evaluation

Run controlled experiments.

Compare:

```text
Independent detection
vs.
Context-aware MetroGuard
```

Deliverable:

> Results, graphs and confusion matrices.

---

# 45. What NOT to Build

To keep the project achievable, avoid adding these unless the core system is finished:

- Face recognition
- Child safety
- Platform intrusion
- Weapon detection
- License plate recognition
- Audio gunshot detection
- Emotion recognition
- Multi-camera person re-identification
- LLM-based autonomous decision making
- Mobile application
- Cloud deployment

These can be listed under **future scope**.

Your current three modules are already sufficient for a major project.

---

# 46. Minimum Viable MetroGuard

If time becomes limited, your minimum successful system should be:

```text
YOLO11
   +
ByteTrack
   +
Fight Detection
   +
Crowd Detection
   +
Abandoned Object
   ↓
Event Schema
   ↓
Spatial + Temporal Correlation
   ↓
Rule-Based Risk Engine
   ↓
Incident Priority
   ↓
Streamlit Dashboard
```

If this works reliably, **you already have a complete project**.

---

# 47. Advanced Version

If everything works early, add:

```text
                 MetroGuard AI
                      │
          ┌───────────┴───────────┐
          │                       │
      Detection               Tracking
          │                       │
          └───────────┬───────────┘
                      │
                Event Layer
                      │
            ┌─────────┴─────────┐
            │                   │
      Spatial Reasoning   Temporal Reasoning
            │                   │
            └─────────┬─────────┘
                      │
                 Event Graph
                      │
                      ▼
              Risk Assessment
                      │
                      ▼
             Incident Priority
                      │
                      ▼
             Explainable Alert
```

A graph representation can be considered as an advanced research extension because recent surveillance/anomaly literature is increasingly using spatial-temporal relationships and semantic fusion rather than purely frame-level classification.

---

# 48. Final Research Question

Your project can ultimately be framed around this question:

> **Can contextual correlation of heterogeneous surveillance events reduce redundant alerts and improve incident prioritization compared with isolated event detection?**

This is a much stronger research question than:

> "Can AI detect fights in metro stations?"

The second problem is already heavily researched.

The first is where **MetroGuard's contribution** lies.

---

# 49. Final Expected Output

At the end, the system should transform:

```text
RAW CCTV
```

into:

```text
OBJECTS
   ↓
TRACKS
   ↓
EVENTS
   ↓
CONTEXT
   ↓
INCIDENTS
   ↓
RISK
   ↓
PRIORITY
   ↓
EXPLANATION
```

For example:

```text
INPUT

Metro CCTV footage
        ↓

DETECTION

Fight = 0.91
Crowd = HIGH
Bag = 0.94
        ↓

CONTEXT

Same camera
Same zone
Within 11 seconds
        ↓

FUSION

Related events
        ↓

INCIDENT

Fight + High Crowd + Abandoned Object
        ↓

RISK

93 / 100
        ↓

PRIORITY

P1 — CRITICAL
        ↓

EXPLANATION

"Multiple high-risk events occurred
within the same platform zone within
a short time interval."
```

That is the **complete MetroGuard AI pipeline** you should aim to build.

---

## Recommended order for your team

If you are starting implementation now, **do not start with the dashboard or Incident Intelligence Engine**.

Build in this exact order:

**1. YOLO11 + ByteTrack**

→ **2. Fight detection**

→ **3. Crowd density**

→ **4. Abandoned-object detection**

→ **5. Common event JSON**

→ **6. Temporal correlation**

→ **7. Spatial correlation**

→ **8. Incident formation**

→ **9. Risk scoring**

→ **10. Explainable incident card**

→ **11. Dashboard**

→ **12. Evaluation**

This order ensures that every stage has something testable before you move to the next one.