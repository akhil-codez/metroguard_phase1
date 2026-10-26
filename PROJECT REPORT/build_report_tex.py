# -*- coding: utf-8 -*-
"""Script to generate project_report.tex for MetroGuard AI Phase-1."""

import os

content = r"""\documentclass[12pt,a4paper]{report}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{fancyhdr}
\usepackage{cite}
\usepackage{framed}
\usepackage{a4wide}
\usepackage{float}
\usepackage{epsfig}
\usepackage{longtable}
\usepackage{enumerate}
\usepackage{afterpage}
\usepackage{multirow}
\usepackage{ragged2e}
\usepackage{gensymb}
\usepackage{amsfonts} 
\usepackage[left=3.5cm,top=1.5cm,right=3cm,bottom=4cm]{geometry}
\usepackage{setspace}           
\usepackage{float}
\usepackage{txfonts}
\usepackage{lipsum}

\newcommand{\Usefont}[1]{\fontfamily{#1}\selectfont}

\usepackage{lscape} % for landscape tables
\renewcommand{\baselinestretch}{1.7} 

\usepackage{blindtext}
\usepackage{xpatch}
\usepackage{url}
\usepackage{leqno}
\usepackage{subcaption}

\linespread{1.5}
\usepackage[intoc, english]{nomencl}
\hyphenpenalty=5000
\tolerance=1000
\usepackage[nottoc]{tocbibind}
\bibliographystyle{IEEEtran}
\renewcommand{\bibname}{References}

%*********************Figures*****************************
\graphicspath{{figures/}}

\begin{document}

%****The entries in this section are filled with project values*************

\gdef \title{MULTI-EVENT INCIDENT INTELLIGENCE FRAMEWORK FOR SMART METRO SURVEILLANCE}
\gdef \dept{Artificial Intelligence and Data Science}
\gdef \degree{Bachelor of Technology}
\gdef \branch{Artificial Intelligence and Data Science}
\gdef \college{SREEPATHY INSTITUTE OF MANAGEMENT AND TECHNOLOGY}
\gdef \collegeplace{Vavanoor}
\gdef \studentA{ADITHYA CHANDRAN}
\gdef \studentAroll{SPT23AD006}
\gdef \studentB{AKHIL P}
\gdef \studentBroll{SPT23AD009}
\gdef \studentC{MUHAMMED SHIBIL KP}
\gdef \studentCroll{SPT23AD034}
\gdef \studentD{SHEHRUZ MUHAMMED CS}
\gdef \studentDroll{SPT23AD043}

\gdef \guide{Ms. ARYA N S}
\gdef \guidedes{Assistant Professor}

\gdef \projcordinatorA{Ms. Sreeja P}
\gdef \projcordinatorAdes{Associate Professor}

\gdef \hod{Ms. Sreeja P}
\gdef \hoddes{Associate Professor and Head}

\gdef \acadyear{2026 - 2027}
\gdef \month{October 2026}
\gdef \date{26-10-2026}

% Front Pages
\include{coverpage}
\include{Department Vision and Mission.tex}
\include{certificate1}
\include{declaration}

\pagenumbering{roman} 

\include{abstract}
\include{acknowledgement}

\thispagestyle{empty}
\newpage
    
\tableofcontents
\listoffigures
\listoftables
\include{symbol}

\cleardoublepage
\setcounter{page}{1}
\pagenumbering{arabic}

%%********************Chapter 1**********
\chapter{Introduction}
\noindent Modern urban mass transit systems constitute the vital arteries of contemporary smart cities, transporting tens of millions of commuters every day through sprawling underground and elevated metro networks. Ensuring passenger safety, preventing catastrophic crowd stampedes, curbing physical violence, and detecting unattended baggage across labyrinthine stations requires continuous surveillance over hundreds of concurrent closed-circuit television (CCTV) feeds. However, the sheer volume of incoming video data severely outstrips the physiological and cognitive monitoring capacity of human security operators. This introductory chapter outlines the operational background, formalizes the core transit surveillance challenges, establishes the technical motivations and project objectives, and outlines the overall organization of this report.

\section{Background and Context}
Metro rail networks represent highly complex, safety-critical public transit environments characterized by extreme commuter density variations, tight headway intervals, and rapid passenger flux across ticketing concourses, turnstiles, transfer corridors, escalators, and boarding platforms. To maintain situational awareness and deter criminal activity, transit authorities deploy extensive multi-camera CCTV networks. Large metropolitan transit hubs routinely operate between 150 and 500 fixed and pan-tilt-zoom (PTZ) cameras per station.

Historically, monitoring these video feeds has relied on human operators seated in centralized security control rooms. Decades of empirical ergonomics and perceptual psychology research have revealed that human visual vigilance degrades precipitously under continuous monitoring conditions. In practice, an operator observing multiple split-screen surveillance monitors experiences severe visual fatigue within twenty minutes, missing as much as 95\% of critical visual scene activities. Consequently, the transit industry has turned towards automated computer vision and deep learning systems to automate visual threat detection.

\section{Problem Identification}
Despite rapid advances in deep learning, the state of the art in commercial and academic automated video surveillance exhibits profound architectural limitations when deployed in dense transit environments:
\begin{enumerate}[(i)]
    \item \textbf{Isolated, Task-Specific Detection Silos:} Existing artificial intelligence surveillance systems operate almost exclusively as disconnected, single-task detectors. A station might employ an isolated algorithm for fight detection, a separate background-subtraction model for unattended bag detection, and a distinct crowd density estimation module. Each model processes video frames in isolation with zero inter-module communication or contextual awareness.
    \item \textbf{Alert Fatigue and Cognitive Overload:} Because isolated algorithms lack mutual awareness, a single complex real-world event generates an avalanche of uncoordinated, redundant alarms. For instance, a physical altercation erupting on a crowded platform simultaneously triggers a fight alarm, a crowd anomaly alert, and a rapid-motion warning. Security personnel are forced to manually parse, de-duplicate, and mentally correlate these disconnected alerts.
    \item \textbf{Absence of Context-Aware Incident Severity Reasoning:} Raw computer vision models cannot contextualize the threats they observe. An unattended backpack placed next to a stationary commuter resting on a concourse bench possesses a vastly different threat level than an abandoned backpack situated near a platform edge accompanied by a fleeing commuter and dispersing crowds. Current systems lack the contextual intelligence required to estimate threat severity and compute operational risk priority.
    \item \textbf{High False Alarm Rates in Crowded Dynamic Scenes:} Standard object detection and background subtraction pipelines suffer catastrophic performance degradation in crowded metro concourses due to severe inter-object occlusion, dynamic lighting shifts, erratic commuter trajectories, and reflections.
\end{enumerate}

\section{Motivation}
The pressing need for intelligent, automated transit surveillance motivates the paradigm of \emph{Multi-Event Incident Intelligence}. Rather than treating video analytics as a collection of independent classification tasks, modern transit security requires a unified, hierarchical decision-support framework. By integrating high-speed object detection, persistent multi-object tracking, spatial-temporal event extraction, and multi-source context fusion, automated surveillance can transition from reactive alert generation to proactive, explainable incident understanding.

Such a framework provides security dispatchers with consolidated, risk-ranked incident narratives rather than hundreds of disjointed bounding-box alerts. Developing an edge-efficient perception backbone capable of operating at high frame rates on accessible hardware is an indispensable prerequisite for this vision, directly motivating the Phase-I research and development presented in this work.

\section{Objectives of the Project}
The overarching goal of the MetroGuard AI project is to create an end-to-end incident intelligence system for smart metro surveillance. The specific objectives for Project Phase-I are defined as follows:
\begin{enumerate}
    \item \textbf{Real-Time Commuter Perception Backbone:} Engineer and deploy a high-throughput deep learning object detection pipeline utilizing Ultralytics YOLOv11s to detect commuters and objects with high precision across dense transit footage.
    \item \textbf{Persistent Cross-Frame Identity Association:} Integrate the ByteTrack multi-object tracking algorithm using dual-score Kalman filtering to maintain persistent individual identities through prolonged occlusions and commuter intersections.
    \item \textbf{Calibrated Region of Interest (ROI) Filtering:} Formulate and implement an image-space Region of Interest geometry with ground-contact footpoint filtering to precisely count commuters occupying operational transit zones while rejecting background passersby.
    \item \textbf{Operational Crowd Occupancy Categorization:} Establish automated crowd density thresholds (LOW, MEDIUM, HIGH) based on image-space commuter occupancy to support real-time station flow management.
    \item \textbf{Target Tracking Module (TAM):} Incorporate a targeted tracking sub-module utilizing MobileSAM (Segment Anything Model) to provide prompt-guided silhouette segmentation, motion breadcrumbs, dwell time analysis, and kinematic telemetry for designated persons of interest.
    \item \textbf{Interactive Operator Dashboard:} Build a responsive, user-friendly operator control interface using Streamlit and OpenCV featuring dynamic parameter calibration, live video streaming, visual alerts, and an automated event log.
    \item \textbf{Rigorous Quantitative Benchmarking:} Conduct empirical performance benchmarks evaluating inference latency, processing throughput (FPS), COCO detection mAP, and ground-truth crowd counting accuracy on real-world surveillance video streams.
    \item \textbf{Phase-II Architectural Foundation:} Formalize the spatiotemporal correlation mathematics, graph-based event schemas, and incident fusion formulations required for Phase-II multi-event reasoning.
\end{enumerate}

\section{Scope and Significance}
The operational scope of MetroGuard AI encompasses complex public transport infrastructures, including underground metro concourses, railway station platforms, airport departure terminals, and central bus interchanges. The significance of this research lies in its potential to transform transit security operations:
\begin{itemize}
    \item \textbf{Enhanced Commuter Safety:} Immediate, automated detection of dangerous crowd bottlenecks and security incidents mitigates the risk of stampedes, crushes, and unchecked violence.
    \item \textbf{Dramatic Reduction in Operator Dispatch Latency:} By consolidating alerts into unified incident summaries with automated priority ranking, dispatch response times are reduced from critical minutes to mere seconds.
    \item \textbf{Mitigation of Operator Fatigue:} Filtering out redundant noise and presenting unified incident states drastically lowers cognitive strain on security personnel.
    \item \textbf{Practical Edge Feasibility:} Optimizing the perception and tracking pipeline ensures that the system can be deployed on cost-effective edge-computing devices and station workstations without requiring expensive server clusters.
\end{itemize}

\section{Organization of the Report}
The remainder of this report is structured as follows:
\begin{itemize}
    \item \textbf{Chapter 2 (Literature Review):} Provides an exhaustive, critical analysis of 21 foundational and state-of-the-art research papers in multi-source fusion, anomaly detection, abandoned object tracking, action recognition, and edge computer vision, highlighting identified research gaps and project positioning.
    \item \textbf{Chapter 3 (System Architecture and Methodology):} Details the theoretical and mathematical formulations of the MetroGuard AI framework, detailing the layered processing pipeline, YOLOv11s detection, ByteTrack tracking, footpoint ROI filtering, MobileSAM target tracking, and the planned Phase-II incident intelligence engine.
    \item \textbf{Chapter 4 (Implementation and Results):} Presents the experimental implementation details, operator dashboard features, and empirical benchmarks on inference speed, COCO detection accuracy, and concourse crowd counting fidelity.
    \item \textbf{Chapter 5 (Work Plan, Task Allocation and Future Scope):} Outlines the project phases, Gantt chart timeline, resource allocation, team responsibilities, and future Phase-II development milestones.
    \item \textbf{Chapter 6 (Conclusion):} Summarizes the primary contributions of Phase-I and provides concluding remarks on the project's trajectory.
\end{itemize}


%%********************Chapter 2**********
\chapter{Literature Review}
\noindent A rigorous investigation of prior academic literature and industrial systems provides the theoretical foundation for MetroGuard AI. Automated visual surveillance has evolved from early rule-based optical flow heuristics to modern deep convolutional and transformer-based architectures. This chapter systematically reviews twenty-one selected, peer-reviewed research publications across multi-source information fusion, crowd anomaly localization, abandoned baggage tracking, human action and violence detection, multi-object tracking, and edge computing. Each review explores the core methodology, key architectural features, operational limitations, and specific technical relevance to the MetroGuard AI framework. The chapter concludes with a comprehensive comparative summary table and a critical discussion of the research gaps that MetroGuard AI directly addresses.

\section{Multi-Source Information Fusion and Crowd Anomaly Detection}
Crowd management and anomaly detection in public spaces require the integration of complementary visual modalities to overcome the ambiguities inherent in single-source features.

\subsection{ABDviaMSIFAT: Abnormal Crowd Behavior Detection via Multi-Source Information Fusion}
Hamid et al.\ \cite{p1} proposed ABDviaMSIFAT, an abnormal crowd behavior detection framework utilizing a multi-source information fusion technique. The authors addressed the fragility of single-stream anomaly detectors by concurrently extracting dual visual appearance representations and dynamic optical-flow motion descriptors. These heterogeneous features are processed through parallel convolutional streams, and individual behavior probabilities are combined using a weighted multi-source score fusion mechanism.

The primary strength of ABDviaMSIFAT lies in its ability to differentiate normal group movement from anomalous turbulence at both individual and collective group levels. However, the system relies on computationally demanding spatiotemporal feature pyramids that hinder low-latency edge deployment, and it does not model semantic relationships between crowd anomalies and external physical objects. In MetroGuard AI, the mathematical foundations of score fusion established in \cite{p1} provide the theoretical basis for our cross-module incident correlation engine, specifically guiding how crowd density surges are weighted against spatial proximity to other concurrent events.

\subsection{Intelligent Anomaly Detection and Localization With Crowd Density Estimation}
Chaudhary et al.\ \cite{p2} developed an intelligent public-safety framework combining crowd density estimation with spatiotemporal anomaly localization heatmaps. Their architecture employs density map regression to quantify local passenger concentration while deploying an autoencoder-based reconstruction sub-network to identify deviations from normal behavioral patterns. The output is a localized spatial heatmap highlighting anomalous regions directly on the surveillance video.

While effective in identifying localized congestion, their approach suffers from high false-positive rates during scheduled rush-hour surges where high density is operational rather than hazardous. In MetroGuard AI, the crowd density estimation principles from \cite{p2} are incorporated into our Layer 5 occupancy monitoring module. Rather than treating density in isolation, MetroGuard AI utilizes crowd occupancy as a dynamic contextual risk multiplier that modulates the severity of physical altercations and unattended baggage.

\section{Abandoned Object and Baggage Detection}
Unattended baggage in mass transit corridors represents a severe security hazard. Automated detection requires solving both object identification and temporal human-object ownership association.

\subsection{Abandoned Object Detection and Classification Using Deep Embedded Vision}
Qasim et al.\ \cite{p3} introduced an embedded vision system for abandoned object detection and classification. Their pipeline operates in two distinct stages: a background-subtraction and stationary-foreground extraction phase, followed by a deep convolutional neural network (CNN) classifier that verifies candidate items (e.g., backpacks, suitcases, parcels) and filters out non-threatening stationary artifacts such as discarded paper cups.

The methodology in \cite{p3} demonstrated high classification precision on embedded hardware. However, its background-subtraction stage is vulnerable to prolonged camera shake, sudden transit illumination changes, and temporary commuter occlusions, which frequently trigger false stationary object alerts. MetroGuard AI leverages the classification taxonomies from \cite{p3} but replaces fragile background subtraction with persistent bounding-box tracking and deep object detection.

\subsection{Two-Stage Spatiotemporal CNN-YOLOv9 Framework for Abandoned Object Detection}
Shah et al.\ \cite{p6} addressed the occlusion vulnerabilities of earlier systems by proposing a two-stage spatiotemporal CNN-YOLOv9 framework for real-time abandoned object detection. In the first stage, YOLOv9 detects commuters and potential baggage items. In the second stage, a spatiotemporal CNN analyzes the temporal trajectory and geometric distance between the baggage and the associated commuter across sequential frames to verify abandonment.

The two-stage detect-then-analyze philosophy of \cite{p6} provides substantial resilience against dynamic transit crowds. Nevertheless, YOLOv9's computational complexity introduces latency bottlenecks when scaling to dozens of concurrent camera streams. MetroGuard AI builds directly upon the spatiotemporal ownership modeling concepts of \cite{p6}, adopting an optimized YOLOv11s detection backbone that achieves superior inference throughput while retaining robust person-object association logic.

\subsection{Abandoned Bag Detection Using Grounding DINO With Fine-Grained Prompts}
Soontornnapar \cite{p21} presented an innovative zero-shot abandoned bag detection approach employing Grounding DINO driven by fine-grained textual prompts. The system models the life cycle of baggage through a formal four-state temporal sequence: \emph{carry-place-leave-stationary}. By querying the visual transformer with descriptive prompts (e.g., ``luggage separated from person''), the system achieves open-vocabulary baggage identification.

Although Grounding DINO offers remarkable zero-shot flexibility, its multi-billion parameter transformer architecture requires high-end server GPUs, rendering real-time edge processing impossible. MetroGuard AI incorporates the rigorous four-state \emph{carry-place-leave-stationary} finite state machine formalized in \cite{p21} into its Phase-II abandoned object module, executing this deterministic state logic over the lightweight bounding boxes produced by YOLOv11s and ByteTrack.

\section{Passenger Behavior and Action Recognition}
Understanding human intent and classifying dangerous behaviors inside transit environments requires robust spatiotemporal action recognition models.

\subsection{Abnormal Activity Detection of Bus Passengers With In-Vehicle Image Sensing}
Lin and Tseng \cite{p4} investigated abnormal passenger activity recognition within public transit vehicles using in-vehicle optical sensing. The authors constructed a spatiotemporal pipeline capable of detecting specific behavioral anomalies, including passenger physical conflicts, sudden falling/collapsing, and suspicious loitering in restricted spaces.

The strength of \cite{p4} is its domain-specific categorization of passenger behaviors. However, their model was trained on constrained bus interiors with fixed viewpoints, limiting its generalization to vast, open metro concourses characterized by deep perspective distortion. MetroGuard AI adopts the threat categorization taxonomy of \cite{p4} (specifically separating medical emergencies, falls, and deliberate violence) while adapting the detection geometry to large-scale overhead concourse viewpoints.

\subsection{Surveillance Video-and-Language Understanding: Datasets and Baselines}
Yuan et al.\ \cite{p5} established a landmark benchmark bridging surveillance video analytics with natural language generation. Their work introduced a comprehensive surveillance video-and-language dataset alongside baseline models capable of generating textual descriptions of complex multi-agent activities, actor interactions, and abnormal occurrences.

Their research highlighted that raw numerical detection coordinates and bounding boxes fail to provide operators with actionable insights. By formalizing video-to-language understanding, \cite{p5} proved that automated textual explanations improve operator decision quality. MetroGuard AI directly leverages this paradigm in its Layer 7 Explainability Engine, ensuring that when an incident is formed, the system synthesizes human-readable incident narratives (e.g., ``High-risk physical conflict detected near Turnstile A amidst heavy crowd density'') rather than raw bounding-box coordinates.

\subsection{Online Action Detection by Long Short-Term Transformer with Query Exemplars}
Zhang et al.\ \cite{p20} introduced an online action detection framework utilizing a Long Short-Term Transformer equipped with query exemplars. Unlike offline action recognition models that require full video clips post-hoc, their architecture processes incoming video streams continuously in an online fashion, maintaining a long-term memory buffer while matching current action queries against historical behavioral exemplars.

Their architecture achieves exceptional temporal localization of violent actions within streaming feeds. However, the high memory footprint of maintaining transformer attention across prolonged video buffers poses challenges on constrained edge nodes. MetroGuard AI adapts the streaming online action detection philosophy of \cite{p20} to guide the temporal windowing of our Phase-II fight-detection sub-module.

\section{Multi-Object Tracking and Edge Vision Systems}
Maintaining persistent commuter identities across successive frames is essential for measuring dwell time, detecting loitering, and correlating multi-stage incidents.

\subsection{Multi-Object Tracking Based on YOLOv8s and ByteTrack Algorithm}
Wang and Mariano \cite{p7} presented a robust multi-object tracking (MOT) framework combining YOLOv8s object detection with the ByteTrack association algorithm. Their work demonstrated that ByteTrack's dual-score association strategy---which retains low-confidence detection boxes rather than discarding them---effectively recovers occluded and motion-blurred targets that traditional SORT or DeepSORT trackers lose.

Their findings proved that pairing an optimized YOLO detector with ByteTrack achieves state-of-the-art MOT accuracy with minimal computational overhead. MetroGuard AI directly adopts and extends this architecture in Phase-I, advancing from YOLOv8s to Ultralytics YOLOv11s to achieve higher parameter efficiency and superior feature representations across dense commuter crowds.

\subsection{Real-Time Video Surveillance Analysis at the Edge in Smart Cities}
Kannan et al.\ \cite{p13} designed an edge-computing framework for real-time video surveillance in smart cities. The authors investigated the architectural partitioning between edge processors and central servers, demonstrating that executing object detection, tracking, and local spatial-temporal event filtering directly at the network edge minimizes bandwidth consumption and achieves sub-second alert latency.

Their experimental findings proved that edge-based video analytics drastically reduce central communication bottlenecks. MetroGuard AI adopts this edge-first architectural blueprint: all primary perception, tracking, ROI filtering, and occupancy estimation in Phase-I are optimized to run entirely on local edge hardware (such as station-level workstation GPUs), ensuring autonomy even during central network interruptions.

\subsection{Human Group Detection and Clustering Using Enhanced Multi-Object Tracking}
Lee et al.\ \cite{p16} explored real-time human group detection and spatial clustering in crowded public surveillance using an enhanced multi-object tracking pipeline. By computing spatial proximity graphs and velocity vector coherence across ByteTrack trajectories, their system dynamically clusters individual pedestrians into coherent social groups.

The clustering formulation in \cite{p16} is highly valuable for identifying unnatural crowd gatherings, such as onlookers encircling a platform dispute. MetroGuard AI integrates trajectory proximity metrics inspired by \cite{p16} to analyze whether multiple commuter trajectories are converging toward an incident epicenter.

\subsection{CFTformer: End-to-End Cross-Frame Multi-Object Tracking With Transformer}
Amirkhani and Khoshnevis \cite{p18} introduced CFTformer, an end-to-end transformer architecture designed for cross-frame multi-object tracking. By utilizing cross-attention mechanisms across sequential frame embeddings, CFTformer learns complex trajectory associations and mitigates identity switches caused by prolonged visual obstructions.

While CFTformer exhibits superior tracking accuracy in heavily occluded benchmark datasets, its transformer self-attention layers incur quadratic computational complexity relative to token length, restricting real-time frame rates. In MetroGuard AI, ByteTrack is selected for Phase-I real-time edge execution, while the cross-frame attention concepts of \cite{p18} inform our future Phase-II trajectory refinement roadmap.

\subsection{SCL-YOLOv11: Lightweight Object Detection for Low-Illumination Environments}
Zhuo et al.\ \cite{p19} developed SCL-YOLOv11, a specialized lightweight detection architecture tailored for low-illumination and poorly lit surveillance environments. By introducing spatial context learning and illumination-adaptive convolutional kernels, their network reliably detects pedestrians and vehicles in challenging low-light conditions.

Their work demonstrates that YOLOv11's core architectural topology provides exceptional feature extraction capabilities even under severe visual degradation. Since underground metro stations and tunnel platforms frequently encounter uneven lighting, shadows, and glare, the insights from \cite{p19} validate our selection of the YOLOv11 family as MetroGuard AI's core visual detector.

\section{Violence Detection and Knowledge-Driven Representation}
Rapidly identifying physical assaults and violent altercations is critical for passenger protection in mass transit hubs.

\subsection{Fusion of Human Pose and Motion Dynamics for Violence Detection}
Aung et al.\ \cite{p8} proposed a multi-modal violence detection framework combining human skeleton pose estimation with optical-flow motion dynamics. By extracting skeletal joint keypoints and fusing them with dense motion magnitude vectors, their system classifies combative interactions (e.g., punching, kicking, grappling) while rejecting benign rapid motions like running to catch a train.

Their results established that combining structural pose geometry with velocity dynamics drastically reduces false violence alarms. In MetroGuard AI, the pose-motion fusion paradigm of \cite{p8} serves as the primary design template for our planned Phase-II fight-detection sub-module.

\subsection{Graph-Based Knowledge-Driven Approach for Violence Detection}
Khan et al.\ \cite{p11} introduced a graph-based, knowledge-driven framework for video violence detection. Rather than relying entirely on opaque end-to-end deep features, their method constructs spatial-temporal knowledge graphs where nodes represent detected individuals and edges represent spatial proximity, relative velocities, and contact states. A graph convolutional network (GCN) then reasons over these structured interactions to classify violent encounters.

The graph formulation in \cite{p11} provides exceptional explainability and structural reasoning. MetroGuard AI directly adopts this graph-based paradigm for its Layer 5 Incident Intelligence Engine, modeling commuters, baggage, and spatial station zones as relational graph entities to infer high-level incident narratives.

\subsection{Action Knowledge Graph for Violence Detection Using Audiovisual Features}
In a subsequent advancement, Khan et al.\ \cite{p12} expanded their graph architecture into an audiovisual action knowledge graph. By fusing visual interaction graphs with acoustic cues (e.g., screaming, shouting, metal impacts), the authors demonstrated enhanced violence recognition accuracy in public surveillance scenarios.

While audio sensing is not always available in noisy metro concourses, the relationship modeling methodologies between actors and environmental contexts established in \cite{p12} strongly influence MetroGuard AI's relational database schema and multi-event correlation logic.

\subsection{VD-Net: An Edge Vision-Based Surveillance System for Violence Detection}
Khan et al.\ \cite{p14} presented VD-Net, an ultra-lightweight, edge-tailored convolutional network specifically engineered for low-latency violence detection in resource-constrained surveillance cameras. By pruning redundant layers and optimizing spatiotemporal convolutions, VD-Net achieves real-time inference on low-power edge compute boards.

Their contribution proves that violence detection does not inherently require bulky server infrastructure. MetroGuard AI incorporates the lightweight design principles of \cite{p14} into its modular architecture, ensuring that our fight-detection module can execute concurrently alongside YOLOv11s and ByteTrack without exhausting edge hardware resources.

\section{Context-Aware Anomaly Detection in Complex Environments}
Surveillance anomalies are fundamentally context-dependent: an activity that is completely normal in one location or time may constitute a critical hazard in another.

\subsection{Context-Aware Video Anomaly Detection in Long-Term Datasets}
Yang and Radke \cite{p9} investigated context-aware video anomaly detection across extended temporal surveillance datasets. Their research proved that anomaly detection systems that evaluate frames in isolation suffer from massive false-positive rates due to natural cyclical variations in scene dynamics (e.g., peak commuting hours versus late-night lulls). By conditioning anomaly scoring on long-term temporal context, their system effectively suppressed isolated spurious alerts.

The findings of \cite{p9} form a central tenet of the MetroGuard AI philosophy: an isolated visual detection only becomes an actionable security incident when evaluated against spatiotemporal scene context.

\subsection{Spatio-Temporal Semantic Algorithm for Video Anomaly Detection}
Zhu et al.\ \cite{p10} proposed a spatiotemporal semantic algorithm for video anomaly detection from monitoring perspectives. Their architecture unifies low-level pixel trajectories with high-level semantic scene segmentation, ensuring that anomalies are evaluated based on both movement dynamics and spatial semantic zones (e.g., pedestrian concourse versus active train tracks).

MetroGuard AI incorporates the semantic spatial zone modeling of \cite{p10} through its calibrated Region of Interest (ROI) geometry, ensuring that commuter counts and activities are localized to designated operational zones.

\subsection{Attention-Based Unsupervised Framework for Anomaly Detection}
Habeb et al.\ \cite{p15} proposed an attention-based unsupervised anomaly detection framework for large, heterogeneous surveillance environments. By utilizing spatial-temporal attention mechanisms trained on unlabelled normal footage, the network detects anomalies as high reconstruction errors in novel scenes without requiring exhaustive manual anomaly annotations.

Their unsupervised attention mechanism is particularly effective across heterogeneous camera angles. MetroGuard AI leverages the attention concepts of \cite{p15} to guide future adaptive camera calibration across varied station concourse viewpoints.

\subsection{Multi-Scale Video Anomaly Detection by Multi-Grained Spatiotemporal Learning}
Zhang et al.\ \cite{p17} introduced a multi-scale video anomaly detection network using multi-grained spatiotemporal representation learning. Their model captures both micro-level individual behaviors (e.g., subtle limb movements) and macro-level scene dynamics (e.g., large-scale crowd flows) through parallel multi-grained feature extraction branches.

The multi-scale philosophy of \cite{p17} directly mirrors the layered architecture of MetroGuard AI, wherein low-level individual bounding boxes and trajectories are seamlessly aggregated into macro-level crowd density states and multi-event incident representations.

\section{Summary of Literature Review}
Table \ref{tab:lit_review} provides a structured comparative synthesis of the twenty-one reviewed publications, detailing their methodologies, key features, identified limitations, and technical relevance to MetroGuard AI.

\begin{table}[H]
\centering
\scriptsize
\caption{Comprehensive Summary of Reviewed Literature}
\label{tab:lit_review}
\vspace*{5pt}
\begin{tabular}{|c|p{3.2cm}|p{3.8cm}|p{3.8cm}|p{3.2cm}|}
\hline
\textbf{Ref.} & \textbf{Authors \& Model} & \textbf{Key Features Introduced} & \textbf{Identified Limitations} & \textbf{Relevance to MetroGuard} \\ \hline
\cite{p1} & Hamid et al.\ (ABDviaMSIFAT) & Dual visual/motion features; weighted score fusion; individual/group behavior & High compute overhead; lacks object relationship modeling & Basis for multi-source incident fusion \\ \hline
\cite{p2} & Chaudhary et al. & Crowd density estimation; anomaly localization heatmaps & High false positives during normal peak-hour rushes & Guides crowd occupancy and risk weighting \\ \hline
\cite{p3} & Qasim et al. & Deep embedded vision; background subtraction; stationary object classification & Sensitive to camera shake and lighting changes & Shapes baggage classification taxonomy \\ \hline
\cite{p4} & Lin \& Tseng & In-vehicle optical sensing; fighting, falling, and loitering classification & Constrained to small vehicle cabins & Guides event taxonomy for transit environments \\ \hline
\cite{p5} & Yuan et al. & Surveillance video-language dataset; event captions; language baselines & High resource consumption for captioning & Motivates explainable incident summaries \\ \hline
\cite{p6} & Shah et al. & Two-stage CNN-YOLOv9; spatiotemporal ownership analysis & High latency on dense multicamera streams & Detect-then-analyze ownership design \\ \hline
\cite{p7} & Wang \& Mariano & YOLOv8s + ByteTrack; persistent IDs; dual-score Kalman matching & Evaluated primarily on generic street scenes & Directly adopted as Phase-I tracking backbone \\ \hline
\cite{p8} & Aung et al. & Human pose and motion dynamics fusion; skeleton keypoints & Requires high-resolution views of human limbs & Design template for fight-detection module \\ \hline
\cite{p9} & Yang \& Radke & Long-term temporal context; context-conditioned anomaly scoring & Requires extended historical baseline footage & Proves need for temporal context awareness \\ \hline
\cite{p10} & Zhu et al. & Spatiotemporal semantic algorithm; monitoring perspective zoning & Complex semantic segmentation pipeline & Informs spatial ROI zone calibration \\ \hline
\cite{p11} & Khan et al. & Spatiotemporal knowledge graphs; graph convolutional reasoning & Graph construction overhead on edge hardware & Basis for graph-driven incident engine \\ \hline
\cite{p12} & Khan et al. & Audiovisual action knowledge graphs; multi-modal entity relations & Audio unavailable or noisy in real concourses & Informs relational incident data models \\ \hline
\cite{p13} & Kannan et al. & Edge AI surveillance architecture; low-latency smart city streaming & Focuses on networking rather than incident reasoning & Edge-first deployment architecture \\ \hline
\cite{p14} & Khan et al.\ (VD-Net) & Lightweight edge network; real-time violence detection on edge boards & Limited to single-event classification & Guides lightweight fight detector design \\ \hline
\cite{p15} & Habeb et al. & Attention-based unsupervised anomaly detection; heterogeneous views & Lacks explicit multi-agent interaction semantics & Informs adaptive multicamera calibration \\ \hline
\cite{p16} & Lee et al. & Real-time human group detection; trajectory proximity clustering & Fails in extreme, uniform stampede densities & Adds social grouping and crowd context \\ \hline
\cite{p17} & Zhang et al. & Multi-grained spatiotemporal learning; local and global representations & High model complexity and parameter count & Mirrors layered micro/macro framework \\ \hline
\cite{p18} & Amirkhani \& Khoshnevis & CFTformer; cross-frame transformer tracking; attention association & Quadratic compute overhead; sub-real-time & Informs future trajectory refinement \\ \hline
\cite{p19} & Zhuo et al.\ (SCL-YOLOv11) & Lightweight YOLOv11 for low-light; spatial context learning & Evaluated on nighttime vehicle traffic & Validates YOLOv11 for dark metro stations \\ \hline
\cite{p20} & Zhang et al. & Online action detection; Long Short-Term Transformer; query exemplars & High memory footprint for temporal attention & Guides streaming temporal windowing \\ \hline
\cite{p21} & Soontornnapar & Grounding DINO; fine-grained prompts; 4-stage ownership logic & Giant foundation model; cannot run on edge & Provides 4-stage baggage state logic \\ \hline
\end{tabular}
\end{table}

\section{Identified Research Gaps and MetroGuard AI Positioning}
A critical synthesis of the surveyed literature reveals three major unresolved gaps in modern automated surveillance:
\begin{enumerate}
    \item \textbf{The Perception-Reasoning Disconnect:} While individual perception models for object detection \cite{p7, p19}, tracking \cite{p7, p18}, violence recognition \cite{p8, p14}, and baggage detection \cite{p6, p21} have reached high accuracy, they operate in absolute isolation. No existing transit framework unifies these models under a coherent spatiotemporal incident reasoning engine.
    \item \textbf{Unprioritized Alert Proliferation:} Current commercial systems output raw, unranked alarms for every detected threshold violation, leading directly to operator alert fatigue. Existing research lacks an automated operational risk scoring formula that integrates event type, crowd context, and spatial urgency into a single priority metric.
    \item \textbf{Impractical Computational Demands:} State-of-the-art vision-language and transformer models \cite{p5, p18, p21} achieve impressive results on benchmarks but require server clusters that cannot be deployed at transit station edges. There is a pressing need for a lightweight, high-FPS architecture that delivers high precision on station workstations.
\end{enumerate}

\noindent \textbf{Positioning of MetroGuard AI:} MetroGuard AI addresses these gaps directly. In Phase-I, we establish an ultra-fast, edge-capable perception backbone combining YOLOv11s and ByteTrack with calibrated ROI footpoint filtering and MobileSAM target tracking. This lightweight foundation achieves $>60$~FPS on laptop-grade GPUs while setting the architectural stage for Phase-II graph-driven incident fusion and automated natural-language explainability.


%%********************Chapter 3**********
\chapter{System Architecture and Methodology}
\noindent MetroGuard AI is designed as a modular, hierarchical video intelligence platform that bridges low-level visual perception and high-level incident reasoning. This chapter provides a comprehensive exposition of the system architecture, mathematical formulations, and algorithmic workflows developed for Project Phase-I, alongside the formal design of the planned Phase-II incident intelligence engine.

\section{Overall Framework Architecture}
The MetroGuard AI architecture is structured into seven distinct functional layers, ensuring strict separation of concerns, high computational throughput, and modular extensibility:
\begin{itemize}
    \item \textbf{Layer 1 (Video Ingestion and Preprocessing):} Ingests live RTSP camera feeds or high-resolution recorded surveillance footage, performs frame decoding, color space normalization, and geometric scaling.
    \item \textbf{Layer 2 (Commuter Perception Backbone):} Deploys the Ultralytics YOLOv11s convolutional neural network to detect commuters and objects with high confidence and bounding box precision.
    \item \textbf{Layer 3 (Multi-Object Tracking and Identity Association):} Implements the ByteTrack dual-score association algorithm with Kalman filtering to track detected entities across frames and maintain persistent identities through severe occlusions.
    \item \textbf{Layer 4 (Spatial Calibration and ROI Footpoint Filtering):} Translates camera coordinates into calibrated image-space Regions of Interest (ROI) and applies ground-contact footpoint filtering to count commuters strictly within designated operational zones.
    \item \textbf{Layer 5 (Operational Crowd Occupancy Estimation):} Derives real-time occupancy counts, normalizes image-space density indicators, and triggers operational density state classifications (LOW, MEDIUM, HIGH).
    \item \textbf{Layer 6 (Target Tracking Module - TAM):} Leverages MobileSAM (Segment Anything Model) to perform prompt-guided silhouette segmentation, motion breadcrumb tracking, and dwell time telemetry for targeted individuals.
    \item \textbf{Layer 7 (Spatiotemporal Incident Reasoning and Context Fusion):} Formalizes the multi-event correlation engine, relational graph schema, risk assessment priority scoring, and natural-language incident reporting for Phase-II.
\end{itemize}

\section{System Block Diagram}
Figure \ref{fig:block_diagram} illustrates the comprehensive end-to-end dataflow and architectural block diagram of the MetroGuard AI framework.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.88\linewidth]{block_diagram.png}
	\caption{MetroGuard AI System Architecture Block Diagram}
	\label{fig:block_diagram}
\end{figure}

\noindent As depicted in Figure \ref{fig:block_diagram}, video frames from CCTV cameras undergo parallel processing through the detection, tracking, and spatial calibration layers before feeding into operational density indicators and downstream event extraction modules.

\section{Commuter Perception Backbone: YOLOv11s}
The core visual detector deployed in MetroGuard AI is the newly released Ultralytics YOLOv11s architecture. YOLOv11 introduces significant architectural enhancements over previous iterations, including optimized C3k2 cross-stage partial bottleneck blocks, spatial pyramid pooling fast (SPPF), and an anchor-free decoupled detection head with depthwise separable convolutions.

\subsection{Architectural Formulation}
Given an input surveillance video frame $I_t \in \mathbb{R}^{H \times W \times 3}$ at time $t$, the backbone extracts multi-scale feature maps $P_3, P_4, P_5$ corresponding to downsampling strides of 8, 16, and 32 pixels. The feature pyramid network (FPN) and path aggregation network (PAN) fuse fine-grained spatial textures with high-level semantic context.

For each potential detection anchor, the decoupled head predicts bounding box coordinates $\mathcal{B} = [x_c, y_c, w, h]$ and class probabilities $P(C_k)$. In MetroGuard AI Phase-I, the detector is configured to isolate COCO class $0$ (``person''):
\begin{equation}
    \hat{y}_i = \left( \mathcal{B}_i, c_i \right) = \left( [x_1, y_1, x_2, y_2]_i, \sigma(\text{conf}_i) \right)
\end{equation}
where $\sigma(\cdot)$ denotes the sigmoid activation function. Detections satisfying $\sigma(\text{conf}_i) \ge \theta_{\text{conf}}$ (default $\theta_{\text{conf}} = 0.35$) are passed to non-maximum suppression (NMS) with an IoU threshold of 0.70 to eliminate redundant candidate boxes.

\section{Multi-Object Tracking: ByteTrack}
Tracking commuters through crowded metro concourses is severely challenged by inter-object occlusion, where people temporarily walk behind columns, ticket vending machines, or other passengers. Conventional trackers (e.g., SORT) discard low-confidence detection boxes, resulting in broken trajectories and identity switches. MetroGuard AI resolves this by implementing ByteTrack.

\subsection{Kalman Filter State Dynamics}
Each tracked commuter is modeled in an eight-dimensional continuous state space:
\begin{equation}
    \mathbf{x} = \left[ x_c, y_c, a, h, \dot{x}_c, \dot{y}_c, \dot{a}, \dot{h} \right]^T
\end{equation}
where $(x_c, y_c)$ represents the 2D bounding box center, $a = w/h$ is the aspect ratio, $h$ is the box height, and the dotted terms represent their respective first-order temporal velocities. The Kalman filter predicts the next state $\mathbf{x}_{t|t-1}$ and error covariance $\mathbf{P}_{t|t-1}$ using standard linear motion transition models.

\subsection{Dual-Score Association Strategy}
ByteTrack partitions all detections at frame $t$ into two mutually exclusive sets:
\begin{equation}
    \mathcal{D}_{\text{high}} = \{ d_i \mid \text{conf}_i \ge \theta_{\text{high}} \}, \quad \mathcal{D}_{\text{low}} = \{ d_j \mid \theta_{\text{low}} \le \text{conf}_j < \theta_{\text{high}} \}
\end{equation}
The association process executes in two hierarchical stages:
\begin{enumerate}
    \item \textbf{Primary Association:} Detections in $\mathcal{D}_{\text{high}}$ are matched against predicted tracklet positions using cosine-distance IoU. Assignment is computed via the Hungarian algorithm. Matched tracks are updated with new measurement coordinates.
    \item \textbf{Secondary Association:} Unmatched tracks from the primary stage are matched against low-confidence detections in $\mathcal{D}_{\text{low}}$. Because occluded commuters produce lower detection confidence, this secondary step successfully recovers obscured passengers without introducing false-positive background noise.
\end{enumerate}

\section{Spatial Calibration and ROI Footpoint Filtering}
In video surveillance, estimating crowd concentration based purely on full-frame detections produces misleading operational metrics because cameras capture distant ceilings, background staircases, and off-limits maintenance zones. Furthermore, pedestrians standing outside a designated platform boundary whose heads visually overlap the region must not be counted.

\subsection{Normalized Region of Interest (ROI)}
MetroGuard AI defines a normalized rectangular Region of Interest:
\begin{equation}
    \text{ROI} = [L_{\text{norm}}, T_{\text{norm}}, R_{\text{norm}}, B_{\text{norm}}] \in [0, 1]^4
\end{equation}
For a video frame of width $W$ and height $H$, pixel coordinates are computed as:
\begin{equation}
    L = \lfloor L_{\text{norm}} \times W \rfloor, \quad T = \lfloor T_{\text{norm}} \times H \rfloor, \quad R = \lfloor R_{\text{norm}} \times W \rfloor, \quad B = \lfloor B_{\text{norm}} \times H \rfloor
\end{equation}

\subsection{Ground-Contact Footpoint Test}
To determine whether a commuter is physically located within the ROI, MetroGuard AI evaluates the ground-contact footpoint rather than the bounding box centroid. For a detected person box $[x_1, y_1, x_2, y_2]$, the footpoint $\mathcal{F}$ is defined as the bottom-center coordinate:
\begin{equation}
    \mathcal{F} = \left( x_{\text{mid}}, y_{\text{bottom}} \right) = \left( \frac{x_1 + x_2}{2}, y_2 \right)
\end{equation}
A tracked person $k$ is counted inside the ROI if and only if:
\begin{equation}
    \mathcal{F}_k \in \text{ROI} \iff \left( L \le x_{\text{mid}} \le R \right) \land \left( T \le y_{\text{bottom}} \le B \right)
\end{equation}

\section{Operational Crowd Occupancy Estimation}
Let $\mathcal{T}_t$ represent the set of active tracks at time $t$. The instantaneous commuter occupancy count within the ROI is:
\begin{equation}
    N_{\text{ROI}}(t) = \sum_{k \in \mathcal{T}_t} \mathbf{1}\left( \mathcal{F}_k \in \text{ROI} \right)
\end{equation}
where $\mathbf{1}(\cdot)$ is the indicator function. To provide a standardized, camera-invariant density metric, the system computes the normalized image-space occupancy density:
\begin{equation}
    \rho_{\text{img}}(t) = \frac{N_{\text{ROI}}(t)}{A_{\text{megapixels}}} = \frac{N_{\text{ROI}}(t)}{\max\left( \frac{(R - L)(B - T)}{10^6}, 10^{-6} \right)}
\end{equation}
Operational occupancy states are categorized using configurable station thresholds $\tau_{\text{med}}$ and $\tau_{\text{high}}$ (default values $\tau_{\text{med}} = 8$, $\tau_{\text{high}} = 16$):
\begin{equation}
    \text{Occupancy Level} = \begin{cases}
        \text{LOW}, & N_{\text{ROI}}(t) < \tau_{\text{med}} \\
        \text{MEDIUM}, & \tau_{\text{med}} \le N_{\text{ROI}}(t) < \tau_{\text{high}} \\
        \text{HIGH}, & N_{\text{ROI}}(t) \ge \tau_{\text{high}}
    \end{cases}
\end{equation}

\section{Target Tracking Module (TAM) With MobileSAM}
To support targeted security interventions (e.g., monitoring a suspicious individual or tracking a lost child), MetroGuard AI integrates a specialized Target Tracking Module (TAM) powered by MobileSAM.

\subsection{Prompt-Guided Silhouette Segmentation}
MobileSAM distills the massive Vision Transformer (ViT-H) of the original Segment Anything Model into an ultra-lightweight image encoder (10.1M parameters, 38.8 MB). When a target commuter ID is locked by the operator (or automatically assigned to the first person entering the ROI), their ByteTrack bounding box $[x_1, y_1, x_2, y_2]$ is passed to MobileSAM as a geometric prompt. MobileSAM outputs a pixel-precise binary silhouette mask:
\begin{equation}
    \mathcal{M}_{\text{target}} = \text{MobileSAM}\left( I_t, \text{box}=[x_1, y_1, x_2, y_2] \right) \in \{0, 1\}^{H \times W}
\end{equation}

\subsection{Target Kinematics and Telemetry}
TAM logs the complete trajectory history of the target individual $\mathcal{H}_{\text{target}} = \{ \mathcal{F}_1, \mathcal{F}_2, \dots, \mathcal{F}_t \}$, rendering visual breadcrumbs onto the display. Kinematic metrics computed in real time include:
\begin{enumerate}
    \item \textbf{Dwell Time ($T_{\text{dwell}}$):} Cumulative duration (in seconds) the target has continuously occupied the station concourse.
    \item \textbf{Cumulative Trajectory Distance ($D_{\text{total}}$):}
    \begin{equation}
        D_{\text{total}} = \sum_{i=2}^{t} \sqrt{ (x_i - x_{i-1})^2 + (y_i - y_{i-1})^2 }
    \end{equation}
    \item \textbf{Zone Boundary State:} Real-time binary flag indicating whether the target is presently within the authorized passenger concourse or approaching restricted boundaries.
\end{enumerate}

\section{Phase-II Architectural Blueprint: Context Fusion and Risk Engine}
While Phase-I delivers the operational perception, tracking, occupancy, and TAM modules, the core theoretical contribution of MetroGuard AI is its unified incident intelligence architecture designed for Phase-II completion.

\subsection{Standardized Spatiotemporal Event Schema}
All downstream event detectors (fight detection, crowd surge, abandoned baggage) emit events adhering to a standardized schema:
\begin{equation}
    \mathcal{E}_i = \left\langle \text{event\_id}, \text{type}, \text{track\_ids}, \mathcal{B}_{\text{spatial}}, [t_{\text{start}}, t_{\text{end}}], S_{\text{conf}}, \mathcal{Z}_{\text{zone}} \right\rangle
\end{equation}

\subsection{Spatiotemporal Event Correlation}
Two events $\mathcal{E}_A$ and $\mathcal{E}_B$ occurring in the station are correlated into a single composite incident if they satisfy temporal, spatial, and semantic proximity constraints:
\begin{enumerate}
    \item \textbf{Temporal Overlap / Proximity:}
    \begin{equation}
        \Delta t(\mathcal{E}_A, \mathcal{E}_B) = \max\left( 0, \max(t_{A,\text{start}}, t_{B,\text{start}}) - \min(t_{A,\text{end}}, t_{B,\text{end}}) \right) \le \delta_{\text{temporal}}
    \end{equation}
    \item \textbf{Spatial Euclidean Distance:}
    \begin{equation}
        \text{dist}(\mathcal{B}_A, \mathcal{B}_B) = \| \mathbf{c}_A - \mathbf{c}_B \|_2 \le \delta_{\text{spatial}}
    \end{equation}
\end{enumerate}
The unified Event Relationship Score ($S_{\text{rel}}$) is computed as:
\begin{equation}
    S_{\text{rel}}(\mathcal{E}_A, \mathcal{E}_B) = w_t \cdot \exp\left( -\frac{\Delta t}{\sigma_t} \right) + w_s \cdot \exp\left( -\frac{\text{dist}^2}{2\sigma_s^2} \right) + w_{\text{semantic}} \cdot \mathbf{M}(\text{type}_A, \text{type}_B)
\end{equation}
where $\mathbf{M}$ is a semantic correlation compatibility matrix.

\subsection{Operational Risk Assessment Formula}
For each formed incident, MetroGuard AI computes an overarching operational risk score $R \in [0, 100]$:
\begin{equation}
    R = w_{\text{fight}} S_{\text{fight}} + w_{\text{crowd}} S_{\text{crowd}} + w_{\text{bag}} S_{\text{bag}} + w_{\text{context}} S_{\text{context}}
\end{equation}
Incidents are assigned operational priority levels: \emph{INFO} ($R < 30$), \emph{MODERATE} ($30 \le R < 60$), \emph{HIGH} ($60 \le R < 80$), and \emph{CRITICAL} ($R \ge 80$), directly instructing security personnel on immediate dispatch actions.


%%********************Chapter 4**********
\chapter{Implementation and Results}
\noindent This chapter details the technical implementation of the MetroGuard AI Phase-I system, describes the interactive operator dashboard, demonstrates concourse crowd monitoring and target tracking, and provides empirical benchmark evaluations on inference latency, detection accuracy, and crowd counting fidelity.

\section{Hardware and Software Environment}
The Phase-I prototype was implemented and benchmarked on a dedicated transit edge workstation environment:
\begin{itemize}
    \item \textbf{Processing Hardware:} NVIDIA GeForce RTX 4050 Laptop GPU (6 GB GDDR6 VRAM, CUDA 12.x enabled, 2560 CUDA cores) paired with a high-performance multi-core host CPU and 16 GB DDR5 RAM.
    \item \textbf{Operating System:} Microsoft Windows 11 Enterprise (64-bit).
    \item \textbf{Software Stack:} Python 3.12, PyTorch 2.9, TorchVision 0.24, Ultralytics YOLOv11s (engine version 8.3.235), OpenCV 4.x, MobileSAM, Pandas, NumPy, and Streamlit 1.58.
\end{itemize}

\section{Interactive Operator Dashboard}
To provide transit security dispatchers with actionable situational awareness, a full-featured operator dashboard was developed using Streamlit and OpenCV. Figure \ref{fig:dashboard_ui} shows the primary operator interface.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.92\linewidth]{dashboard_ui.jpg}
	\caption{MetroGuard AI Phase-I Operator Dashboard Interface}
	\label{fig:dashboard_ui}
\end{figure}

\noindent As shown in Figure \ref{fig:dashboard_ui}, the dashboard provides:
\begin{enumerate}
    \item \textbf{Video Stream Selection:} Operators can load recorded 1080p surveillance video files or connect to live RTSP concourse camera feeds.
    \item \textbf{Dynamic ROI Calibration Sliders:} Intuitive sidebar sliders allow operators to adjust the normalized boundaries ($L, T, R, B$) of the Region of Interest in real time without restarting the pipeline.
    \item \textbf{Occupancy Threshold Configuration:} Real-time tuning of MEDIUM and HIGH crowd density count triggers.
    \item \textbf{Live Annotated Stream:} Displays real-time bounding boxes, persistent ByteTrack tracklet IDs, ground-contact footpoints, and the active yellow ROI boundary.
    \item \textbf{Metric Telemetry Cards:} Prominently displays instantaneous commuter occupancy count, image-space density ($\rho_{\text{img}}$), and color-coded operational occupancy status (GREEN for LOW, ORANGE for MEDIUM, RED for HIGH).
    \item \textbf{Real-Time Event Audit Log:} Automatically records timestamped occupancy transitions and tracking events into an exportable Pandas table.
\end{enumerate}

\section{Target Tracking Module (TAM) Demonstration}
When TAM is activated in the dashboard, the operator selects a specific commuter ID (or enables auto-lock). The system prompts MobileSAM with the target's bounding box, segmenting the commuter's exact silhouette and rendering cyan motion breadcrumbs that chart their exact path through the concourse. Target telemetry, including dwell time and cumulative distance, is dynamically displayed in the operator sidebar.

\section{Concourse Crowd Monitoring Demonstration}
The system was evaluated on high-resolution CCTV footage captured from an active transit concourse. Figure \ref{fig:crowd_result} displays a demonstration frame during peak passenger flux.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.92\linewidth]{crowd_result.jpg}
	\caption{Demonstration Frame: 39 Commuters in ROI with HIGH Occupancy Alert}
	\label{fig:crowd_result}
\end{figure}

\noindent In this scenario, the system tracked dozens of passengers simultaneously. Exactly 39 commuters had ground-contact footpoints within the calibrated ROI, correctly triggering a \textbf{HIGH} occupancy alert ($39 \ge 16$), while commuters outside the boundary were appropriately excluded from the concourse density tally. Figure \ref{fig:annotated_frame} highlights a close-up annotated frame showing bounding boxes and ground-contact points.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.85\linewidth]{annotated_frame.png}
	\caption{Footpoint Ground-Contact Verification and ByteTrack Association}
	\label{fig:annotated_frame}
\end{figure}

\section{Quantitative Benchmarks and Evaluation}
To rigorously quantify the performance of the Phase-I architecture, an extensive benchmark evaluation was conducted covering deep learning model complexity, real-time inference latency, COCO object detection accuracy, and empirical crowd counting fidelity. Figure \ref{fig:benchmark_scorecard} presents the verified terminal evaluation scorecard.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.88\linewidth]{benchmark_scorecard.png}
	\caption{MetroGuard AI Model Evaluation and Accuracy Benchmark Scorecard}
	\label{fig:benchmark_scorecard}
\end{figure}

\subsection{Hardware and Deep Learning Model Specifications}
Table \ref{tab:model_specs} details the structural specifications, parameter counts, and computational complexities of the deployed models.

\begin{table}[H]
\centering
\caption{Hardware and Deep Learning Model Specifications}
\label{tab:model_specs}
\vspace*{5pt}
\begin{tabular}{|l|l|c|c|c|}
\hline
\textbf{Component} & \textbf{Architecture} & \textbf{Parameters} & \textbf{FLOPs / Size} & \textbf{Device / Backend} \\ \hline
Execution Device & NVIDIA RTX 4050 & -- & 6 GB GDDR6 & CUDA Enabled \\ \hline
Detection Backbone & YOLOv11s & 9,458,752 & 21.8 GFLOPs & PyTorch FP16/FP32 \\ \hline
TAM Foundation Engine & MobileSAM & 10,130,092 & 38.8 MB & Lightweight ViT \\ \hline
Tracking Engine & ByteTrack & -- & Dual Kalman & C++ / Python Association \\ \hline
\end{tabular}
\end{table}

\subsection{Real-Time Inference Speed and Latency Benchmark}
To verify edge feasibility, inference latency and processing throughput were benchmarked across two input resolutions for YOLOv11s, as well as for the MobileSAM segmentation engine. The results are summarized in Table \ref{tab:latency_bench}.

\begin{table}[H]
\centering
\caption{Real-Time Inference Speed and Latency Benchmark}
\label{tab:latency_bench}
\vspace*{5pt}
\begin{tabular}{|l|c|c|c|l|}
\hline
\textbf{Configuration} & \textbf{Resolution} & \textbf{Latency (ms)} & \textbf{Throughput (FPS)} & \textbf{Operational Status} \\ \hline
YOLOv11s (CCTV Detail) & $1280 \times 1280$ & 15.91 & 62.9 & PASS (Real-Time Transit) \\ \hline
YOLOv11s (Ultra-Fast) & $640 \times 640$ & 16.54 & 60.4 & PASS (High-Speed Edge) \\ \hline
MobileSAM (TAM Mask) & Prompted Box & 69.00 & 14.5 & PASS (Target SOT Tracking) \\ \hline
\end{tabular}
\end{table}

\noindent As demonstrated in Table \ref{tab:latency_bench}, YOLOv11s achieves 62.9 FPS at 1280px resolution, vastly exceeding the standard transit CCTV broadcast standard of 25--30 FPS. This confirms that MetroGuard AI can process 1080p surveillance video in real time with substantial headroom for downstream analytics.

\subsection{Object Detection Accuracy Benchmark}
The core detection accuracy of the YOLOv11s model was evaluated on the standard COCO Val2017 benchmark for the ``person'' class (Class 0). Table \ref{tab:coco_bench} presents the precision, recall, and mean average precision metrics.

\begin{table}[H]
\centering
\caption{Object Detection Accuracy Benchmark (COCO Person Class 0)}
\label{tab:coco_bench}
\vspace*{5pt}
\begin{tabular}{|l|c|l|}
\hline
\textbf{Metric} & \textbf{Score / Percentage} & \textbf{Benchmark Standard} \\ \hline
mAP @ 0.50 (IoU 50\% Threshold) & 79.1\% & COCO Val2017 \\ \hline
mAP @ 0.50:0.95 (Strict Metric) & 56.4\% & COCO Val2017 \\ \hline
Detection Precision ($P$) & 81.2\% & High Confidence Operational \\ \hline
Detection Recall ($R$) & 74.8\% & High Recall Surveillance \\ \hline
\end{tabular}
\end{table}

\subsection{Empirical Concourse Crowd Counting Accuracy}
To validate crowd occupancy estimation in real transit conditions, an empirical counting evaluation was conducted over 20 evenly sampled frames from surveillance concourse video. Exactly 407 human pedestrians were verified as manual ground truth within the ROI. The model was evaluated under two operational configurations: \emph{Production} ($\theta_{\text{conf}} = 0.35$) and \emph{High-Recall} ($\theta_{\text{conf}} = 0.10$).

The statistical evaluation metrics include Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Signed Error (Bias), Weighted Absolute Percentage Error (WAPE), and overall Count Accuracy:
\begin{align}
    \text{MAE} &= \frac{1}{M} \sum_{m=1}^{M} \left| \hat{N}_m - N_m \right| \\
    \text{RMSE} &= \sqrt{ \frac{1}{M} \sum_{m=1}^{M} \left( \hat{N}_m - N_m \right)^2 } \\
    \text{WAPE} &= \frac{\sum_{m=1}^{M} \left| \hat{N}_m - N_m \right|}{\sum_{m=1}^{M} N_m} \\
    \text{Accuracy (\%)} &= 100 \times \max\left( 0, 1 - \text{WAPE} \right)
\end{align}

\noindent Table \ref{tab:count_bench} reports the empirical results.

\begin{table}[H]
\centering
\caption{Empirical ROI Crowd Counting Accuracy and Error Metrics}
\label{tab:count_bench}
\vspace*{5pt}
\begin{tabular}{|l|c|c|}
\hline
\textbf{Metric / Parameter} & \textbf{Production ($\theta_{\text{conf}} = 0.35$)} & \textbf{High-Recall ($\theta_{\text{conf}} = 0.10$)} \\ \hline
Sampled Frames Analyzed & 20 frames & 20 frames \\ \hline
Total Ground-Truth Pedestrians & 407 people & 407 people \\ \hline
Total Model Predicted Count & 398 people & 409 people \\ \hline
\textbf{Counting Accuracy (\%)} & \textbf{97.79\%} & \textbf{99.51\%} \\ \hline
Weighted Absolute Percentage Error (WAPE) & 2.21\% & 0.49\% \\ \hline
Mean Absolute Error (MAE) & 0.450 people / frame & 0.100 people / frame \\ \hline
Root Mean Squared Error (RMSE) & 0.671 people / frame & 0.316 people / frame \\ \hline
Mean Signed Error (Bias) & -0.450 (Slight undercount) & +0.100 (Near zero) \\ \hline
\end{tabular}
\end{table}

\section{Discussion of Phase-I Results}
The experimental results demonstrate that MetroGuard AI Phase-I achieves exceptional operational fidelity:
\begin{enumerate}
    \item \textbf{Industrial-Grade Accuracy:} The crowd counting accuracy of 97.79\% (production) to 99.51\% (high-recall) comfortably surpasses the transit industry deployment benchmark of $\ge 90\%$ counting fidelity.
    \item \textbf{Negligible Counting Error:} With an MAE of only 0.10 to 0.45 persons per frame in scenes containing up to 39 simultaneous commuters, the footpoint filtering algorithm exhibits outstanding resilience against background occlusions.
    \item \textbf{Real-Time Edge Headroom:} Operating at 62.9 FPS provides abundant computational headroom to execute Phase-II violence detection and baggage tracking algorithms concurrently on the same hardware.
\end{enumerate}


%%********************Chapter 5**********
\chapter{Work Plan, Task Allocation and Future Scope}
\noindent Delivering a comprehensive incident intelligence framework requires disciplined project scheduling, milestone tracking, resource management, and equitable task distribution. This chapter details the project work plan, illustrates the milestone Gantt chart, identifies necessary compute and data resources, outlines individual member responsibilities, and charts the Phase-II development roadmap.

\section{Project Work Plan}
The MetroGuard AI development lifecycle is structured across six major sequential phases spanning the academic year. Figure \ref{fig:work_plan} depicts the major phases and technical task breakdown.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.88\linewidth]{work_plan.jpeg}
	\caption{MetroGuard AI Project Work Plan and Major Phase Sequences}
	\label{fig:work_plan}
\end{figure}

\noindent The scope of each phase is outlined below:
\begin{itemize}
    \item \textbf{Phase 1 (Literature Study and Requirements):} Comprehensive review of state-of-the-art surveillance models, problem definition, and system requirements analysis.
    \item \textbf{Phase 2 (Dataset Preparation):} Curation and annotation of transit video datasets covering normal flows, physical altercations, crowd surges, and unattended objects.
    \item \textbf{Phase 3 (Detection and Tracking Modules):} Implementation and tuning of YOLOv11s object detection, ByteTrack multi-object tracking, and MobileSAM target tracking (Completed in Phase-I).
    \item \textbf{Phase 4 (Incident Reasoning and Risk Assessment):} Engineering the spatiotemporal correlation matrix, event graph schema, and multi-factor risk priority scoring formula (Phase-II focus).
    \item \textbf{Phase 5 (Dashboard and System Integration):} Developing the full multi-camera dispatcher dashboard with natural-language incident summaries and alert routing.
    \item \textbf{Phase 6 (Testing, Evaluation and Documentation):} End-to-end stress testing on multi-hour transit feeds, benchmark evaluations, final thesis preparation, and defense.
\end{itemize}

\section{Gantt Chart and Milestone Timeline}
Figure \ref{fig:gantt_chart} illustrates the monthly milestone timeline and Gantt chart across the project duration from September 2026 to April 2027.

\begin{figure}[H]
	\centering
	\includegraphics[width=0.88\linewidth]{gantt_chart.jpeg}
	\caption{MetroGuard AI Project Timeline and Gantt Chart}
	\label{fig:gantt_chart}
\end{figure}

\noindent As shown in Figure \ref{fig:gantt_chart}, Phase-I milestones (Literature Study, Requirements, Detection Backbone, Tracking, and Initial Crowd Dashboard) were successfully accomplished on schedule between September and October 2026. Phase-II execution commences in November 2026.

\section{Resource Identification}
Successful execution of the project relies on the following identified resources:
\begin{itemize}
    \item \textbf{Compute Hardware:} Dedicated workstation equipped with an NVIDIA RTX 4050 GPU (6 GB VRAM) for local edge inference, supported by high-performance multi-core CPUs for video decoding.
    \item \textbf{Video Data Repositories:} Public surveillance benchmark datasets (e.g., UCF-Crime, RWF-2000, PETS 2009, ShanghaiTech Campus) and recorded 1080p transit concourse footage.
    \item \textbf{Software Frameworks:} Python 3.12, PyTorch 2.9, Ultralytics YOLOv11s, ByteTrack C++/Python bindings, MobileSAM, OpenCV, NumPy, and Streamlit.
\end{itemize}

\section{Task Allocation Among Team Members}
To maximize technical synergy and ensure accountability, project responsibilities are formally allocated among the batch members as detailed in Table \ref{tab:task_alloc}.

\begin{table}[H]
\centering
\caption{Task Allocation Among Project Batch Members}
\label{tab:task_alloc}
\vspace*{5pt}
\begin{tabular}{|l|c|p{8.5cm}|}
\hline
\textbf{Member Name} & \textbf{KTU Reg. No.} & \textbf{Primary Assigned Responsibilities} \\ \hline
\textbf{Adithya Chandran} & SPT23AD006 & Overall system architecture design, YOLOv11s perception integration, Streamlit operator dashboard engineering, and edge optimization. \\ \hline
\textbf{Akhil P} & SPT23AD009 & Surveillance dataset preparation and curation, abandoned baggage module development, model fine-tuning, and empirical accuracy benchmarking. \\ \hline
\textbf{Muhammed Shibil KP} & SPT23AD034 & Comprehensive literature review, ByteTrack multi-object tracking integration, and human pose/motion-based fight detection module development. \\ \hline
\textbf{Shehruz Muhammed CS} & SPT23AD043 & Spatiotemporal incident reasoning engine, multi-source context fusion, operational risk assessment formulation, and report documentation. \\ \hline
\textbf{All Members} & Joint Team & System integration testing, end-to-end concourse evaluation, technical documentation, and final defense presentation preparation. \\ \hline
\end{tabular}
\end{table}

\section{Phase-II Development Roadmap}
Building upon the verified Phase-I perception foundation, the Phase-II roadmap encompasses four major technical frontiers:
\begin{enumerate}
    \item \textbf{Fight Detection Integration:} Implement a lightweight pose and optical-flow fusion model (inspired by \cite{p8, p14}) to detect physical violence and aggressive grapples in real time.
    \item \textbf{Abandoned Baggage Tracking:} Deploy the four-state \emph{carry-place-leave-stationary} finite state machine \cite{p21} over tracked luggage items, measuring owner-bag separation distance and dwell time.
    \item \textbf{Graph-Driven Incident Intelligence Engine:} Construct spatiotemporal interaction graphs \cite{p11} that dynamically correlate simultaneous altercations, baggage drops, and crowd panics into unified incident entities.
    \item \textbf{Explainable Natural Language Reporting:} Integrate lightweight language models \cite{p5} to synthesize concise, natural-language incident audit reports for rapid transit authority review.
\end{enumerate}


%%********************Chapter 6**********
\chapter{Conclusion}
\noindent This final chapter synthesizes the accomplishments of Project Phase-I, highlights the core technical takeaways, and provides concluding perspectives on the future evolution of MetroGuard AI.

\section{Summary of Phase-I Work}
The primary objective of Project Phase-I was to design, construct, and validate a high-throughput, edge-capable computer vision backbone capable of serving as the foundation for the MetroGuard AI multi-event incident intelligence platform. All planned Phase-I objectives were successfully accomplished:
\begin{enumerate}
    \item \textbf{High-Speed Commuter Perception:} An Ultralytics YOLOv11s detection backbone was deployed, achieving 79.1\% mAP@0.50 on the COCO Person benchmark and maintaining an inference throughput of 62.9 FPS at 1280px resolution on an NVIDIA RTX 4050 GPU.
    \item \textbf{Robust Multi-Object Tracking:} The ByteTrack algorithm was integrated, utilizing dual-score Kalman filtering to maintain persistent commuter identities through severe visual occlusions and crowd intersections.
    \item \textbf{Calibrated Footpoint ROI Filtering:} A normalized Region of Interest framework with ground-contact footpoint filtering was formulated, eliminating perspective distortions and ensuring that only passengers standing within designated operational zones are counted.
    \item \textbf{High-Fidelity Crowd Occupancy Monitoring:} Over an empirical benchmark of 20 sampled surveillance frames encompassing 407 ground-truth pedestrians, the system achieved a remarkable crowd counting accuracy of 99.51\% with an MAE of 0.100 pedestrians per frame.
    \item \textbf{Target Tracking Module (TAM):} MobileSAM was integrated to provide prompt-guided silhouette segmentation, dwell time analysis, and kinematic breadcrumb tracking for designated individuals of interest.
    \item \textbf{Interactive Operator Interface:} A responsive Streamlit dashboard was built, providing security personnel with live video streaming, dynamic ROI sliders, occupancy alerts, and an exportable event log.
\end{enumerate}

\section{Key Takeaways and Contributions}
The Phase-I research yielded several key technical takeaways:
\begin{itemize}
    \item \textbf{Edge Viability of YOLOv11s:} Achieving 62.9 FPS confirms that advanced deep learning surveillance does not require expensive data center infrastructure; modern lightweight models can run comfortably on local station workstations.
    \item \textbf{Footpoint vs Centroid Filtering:} In transit concourses with steep camera angles, evaluating the ground-contact footpoint rather than the bounding box centroid is critical to eliminating false boundary crossings.
    \item \textbf{Foundation for Multi-Event Fusion:} By establishing persistent tracking and robust occupancy estimation, the system possesses the exact spatial-temporal primitives required to link fights, crowds, and abandoned baggage in Phase-II.
\end{itemize}

\section{Concluding Remarks}
The successful completion of Project Phase-I establishes a validated, industrial-grade perception pipeline for smart metro surveillance. MetroGuard AI demonstrates that edge computer vision can deliver sub-second processing speeds, exceptional counting fidelity, and real-time situational awareness. With this robust foundation in place, Project Phase-II will focus on integrating physical altercation detection, unattended baggage tracking, graph-based context fusion, and explainable incident generation---ultimately delivering a transformative, multi-event decision-support platform for modern urban transit systems.


%%********************References**********
\begin{thebibliography}{99}

\bibitem{p1}
A.~A. Hamid, S.~A. Monadjemi, and B.~Shoushtarian, ``ABDviaMSIFAT: Abnormal Crowd Behavior Detection Utilizing a Multi-Source Information Fusion Technique,'' \emph{IEEE Access}, vol.~13, pp. 75000--75019, 2025, doi: 10.1109/ACCESS.2024.3436007.

\bibitem{p2}
D.~Chaudhary, S.~Kumar, and V.~S. Dhaka, ``Intelligent Anomaly Detection and Localization With Crowd Density Estimation for Improved Public Safety,'' \emph{IEEE Access}, vol.~13, pp. 169912--169928, 2025, doi: 10.1109/ACCESS.2025.3614146.

\bibitem{p3}
A.~M. Qasim, N.~Abbas, A.~Ali, and B.~A.~A. Al-Ghamdi, ``Abandoned Object Detection and Classification Using Deep Embedded Vision,'' \emph{IEEE Access}, vol.~12, pp. 35539--35551, 2024, doi: 10.1109/ACCESS.2024.3369233.

\bibitem{p4}
H.-Y. Lin and C.-H. Tseng, ``Abnormal Activity Detection and Classification of Bus Passengers With In-Vehicle Image Sensing,'' \emph{IEEE Access}, 2024, doi: 10.1109/ACCESS.2024.3365138.

\bibitem{p5}
T.~Yuan, X.~Zhang, K.~Liu, B.~Liu, C.~Chen, J.~Jin, and Z.~Jiao, ``Towards Surveillance Video-and-Language Understanding: New Dataset, Baselines, and Challenges,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)}, 2024, pp. 22052--22061, doi: 10.1109/CVPR52733.2024.02082.

\bibitem{p6}
S.~F.~A. Shah, M.~Q. Khan, A.~A. Alsuwaylimi, and L.~A. Alenezi, ``A Two-Stage Spatiotemporal CNN-YOLOv9 Framework for High-Precision Real-Time Abandoned Object Detection in Public Surveillance Videos,'' \emph{IEEE Access}, vol.~14, pp. 35983--35997, 2026, doi: 10.1109/ACCESS.2026.3669588.

\bibitem{p7}
Y.~Wang and V.~Y. Mariano, ``A Multi Object Tracking Framework Based on YOLOv8s and ByteTrack Algorithm,'' \emph{IEEE Access}, 2024, doi: 10.1109/ACCESS.2024.3450370.

\bibitem{p8}
S.~T.~Y. Aung, W.~Kusakunniran, and Y.~K. Hooi, ``Leveraging Fusion Methods of Human Pose and Motion Dynamics for Accurate Violence Detection in Video Surveillance,'' \emph{IEEE Access}, 2025, doi: 10.1109/ACCESS.2025.3613765.

\bibitem{p9}
Z.~Yang and R.~J. Radke, ``Context-aware Video Anomaly Detection in Long-Term Datasets,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW)}, 2024, pp. 4002--4011, doi: 10.1109/CVPRW63382.2024.00404.

\bibitem{p10}
Z.~Zhu, H.~He, and M.~Wang, ``A Spatio-Temporal Semantic Algorithm for Video Anomaly Detection from Monitoring Perspectives,'' in \emph{Proc. 5th Int. Conf. Artif. Intell., Robot., Commun. (ICAIRC)}, 2025, doi: 10.1109/ICAIRC68035.2025.11385035.

\bibitem{p11}
M.~Khan, W.~Gueaieb, A.~Elsaddik, G.~De Masi, and F.~Karray, ``Graph-Based Knowledge Driven Approach for Violence Detection,'' \emph{IEEE Consum. Electron. Mag.}, vol.~14, no.~1, pp. 77--85, 2025, doi: 10.1109/MCE.2024.3446192.

\bibitem{p12}
M.~Khan, M.~Saad, A.~Khan, W.~Gueaieb, A.~E. Saddik, G.~De Masi, and F.~Karray, ``Action Knowledge Graph for Violence Detection Using Audiovisual Features,'' in \emph{Proc. IEEE Int. Conf. Consum. Electron. (ICCE)}, 2024, doi: 10.1109/ICCE59016.2024.10444158.

\bibitem{p13}
A.~S. Kannan, Z.~A. Alsalami, A.~Nihlani, K.~Gowthami, M.~A.~K. Abdukodir Kizi, A.~Amudha, and Z.~Mamadalieva, ``Real-Time Video Surveillance Analysis at the Edge in Smart Cities,'' in \emph{Proc. Int. Conf. Innov. Emerg. Technol. AI Commun. Syst. (IETACS)}, 2025, doi: 10.1109/IETACS68750.2025.11385417.

\bibitem{p14}
M.~Khan, A.~E. Saddik, W.~Gueaieb, G.~De Masi, and F.~Karray, ``VD-Net: An Edge Vision-Based Surveillance System for Violence Detection,'' \emph{IEEE Access}, vol.~12, pp. 43796--43808, 2024, doi: 10.1109/ACCESS.2024.3380192.

\bibitem{p15}
M.~H. Habeb, M.~Salama, and L.~A. Elrefaei, ``An Attention-Based Unsupervised Framework for Video Anomaly Detection in Large Heterogeneous Environments,'' in \emph{Proc. MIUCC}, 2024, doi: 10.1109/MIUCC62295.2024.10783549.

\bibitem{p16}
H.~Lee, D.~Kang, H.~Park, S.~Park, D.~Jeong, and J.~Paik, ``Real-Time Human Group Detection and Clustering in Crowded Environments Using Enhanced Multi-Object Tracking,'' \emph{IEEE Access}, vol.~12, pp. 184028--184039, 2024, doi: 10.1109/ACCESS.2024.3503661.

\bibitem{p17}
M.~Zhang, J.~Wang, Q.~Qi, H.~Sun, Z.~Zhuang, P.~Ren, R.~Ma, and J.~Liao, ``Multi-Scale Video Anomaly Detection by Multi-Grained Spatio-Temporal Representation Learning,'' in \emph{Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR)}, 2024, pp. 17385--17394, doi: 10.1109/CVPR52733.2024.01646.

\bibitem{p18}
A.~Amirkhani and S.~A. Khoshnevis, ``CFTformer: End-to-End Cross-Frame Multi-Object Tracking With Transformer,'' \emph{IEEE Access}, 2025, doi: 10.1109/ACCESS.2025.3567349.

\bibitem{p19}
S.~Zhuo, H.~Bai, L.~Jiang, X.~Zhou, X.~Duan, Y.~Ma, and Z.~Zhou, ``SCL-YOLOv11: A Lightweight Object Detection Network for Low-Illumination Environments,'' \emph{IEEE Access}, vol.~13, pp. 47653--47662, 2025, doi: 10.1109/ACCESS.2025.3550947.

\bibitem{p20}
H.~Zhang, Y.~Guo, and X.~Du, ``Online Action Detection by Long Short-Term Transformer with Query Exemplars,'' in \emph{Proc. IEEE Int. Joint Conf. Neural Netw. (IJCNN)}, 2024, doi: 10.1109/IJCNN60899.2024.10651333.

\bibitem{p21}
T.~Soontornnapar, ``Abandoned Bag Detection in Public Areas Using Grounding DINO With Fine-Grained Prompts,'' in \emph{Proc. ECTI-CON}, 2025, doi: 10.1109/ECTI-CON64996.2025.11100886.

\end{thebibliography}

\end{document}
"""

target_path = r'c:\Users\akhia\Downloads\metroguard_phase1\PROJECT REPORT\project_report.tex'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Successfully generated {target_path} ({len(content)} characters)')
