# Related Work

Our work draws on three research threads: software ecosystem lifecycle analysis, time series clustering methodology, and changepoint detection for temporal segmentation. We review each area and identify the gap our approach addresses.

## Software Ecosystem Lifecycle Analysis

The study of software package adoption dynamics has established foundational methods for understanding ecosystem evolution. Wittern et al. [2016] provided the first comprehensive analysis of the npm ecosystem, characterizing package dependencies and usage patterns through descriptive statistics. This work demonstrated that package ecosystems exhibit structured behavior amenable to quantitative analysis, though it did not attempt trajectory clustering.

Mujahid et al. [2021] advanced this line by identifying trajectory patterns in npm packages, showing that download dynamics follow recognizable archetypes. Their work established that software adoption is not purely idiosyncratic but reflects underlying mechanisms that generate recurring temporal signatures. However, their single-level clustering approach conflates lifecycle phase (where a package currently sits in its adoption curve) with trajectory type (what shape its full adoption curve takes). A young package in its growth phase clusters with mature packages showing similar current download rates, obscuring the underlying trajectory structure.

Studies of PyPI and other package ecosystems [Decan et al., 2019] have similarly focused on aggregate statistics or dependency analysis rather than trajectory characterization. The transfer of these methods to ML dataset ecosystems—where benchmark effects, paper publication cycles, and domain-specific trends create distinct dynamics—has not been attempted.

## Time Series Clustering

Time series clustering provides the methodological foundation for grouping trajectories by shape similarity. Aghabozorgi et al. [2015] provide a comprehensive review of approaches, distinguishing shape-based methods (which preserve temporal structure) from feature-based methods (which reduce series to summary statistics). For adoption trajectory analysis, shape-based methods are essential: two datasets may have identical mean and variance but entirely different adoption dynamics (sustained growth vs. peak-and-decline).

Dynamic Time Warping (DTW) has emerged as the standard distance metric for shape-based clustering [Berndt and Clifford, 1994]. DTW handles temporal warping—allowing similar shapes that occur at different speeds to be recognized as similar—which is crucial for adoption analysis where some datasets reach maturity faster than others. The tslearn library [Tavenard et al., 2020] provides efficient implementations of DTW-based TimeSeriesKMeans that we employ.

However, existing time series clustering work has focused on domains like sensor data, electricity consumption, and financial time series. Application to software or dataset ecosystems has been limited, and no prior work has combined clustering with changepoint detection to separate phase from trajectory.

## Changepoint Detection

Changepoint detection identifies points where statistical properties of a time series shift, enabling segmentation into distinct regimes. The PELT algorithm [Killick et al., 2012] provides optimal changepoint detection with linear computational cost, making it practical for large-scale analysis. PELT with BIC penalty selection has been validated across diverse domains including climate data, financial time series, and genomic applications.

Applying changepoint detection to adoption trajectories enables identification of discrete phases—launch, growth, maturity, decline—that characterize lifecycle progression. This addresses a limitation of direct clustering: without phase detection, a dataset's current position in its lifecycle confounds its trajectory type.

## Our Position

We combine validated time series methods (DTW clustering, PELT changepoint detection) with insights from software ecosystem studies to create the first systematic ML dataset lifecycle analysis. Our two-level hierarchical approach—using PELT for phase identification (Level 1) and DTW clustering for trajectory classification (Level 2)—addresses the phase-trajectory conflation that limits single-level methods. This enables discovery of stable trajectory archetypes that generalize across datasets regardless of their current lifecycle phase.
