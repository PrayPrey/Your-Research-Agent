# Related Work

Our work builds on three lines of research: documentation framework design, empirical documentation studies, and community engagement in open-source software.

## Documentation Framework Design

Gebru et al. [@gebru2018datasheets] introduced *Datasheets for Datasets*, proposing structured templates documenting dataset motivation, composition, collection processes, preprocessing, and intended uses. The framework drew on electronics industry datasheets to improve transparency and accountability in ML datasets. Mitchell et al. [@mitchell2019model] extended this approach to *Model Cards for Model Reporting*, providing analogous documentation for trained models. Pushkarna et al. [@pushkarna2022data] further refined these ideas with *Data Cards*, emphasizing licensing clarity and preprocessing transparency.

These frameworks address dataset documentation at the *design* level—providing templates and guidelines for what to document. Boyd et al. [@boyd2021datasheets] validated datasheet effectiveness in controlled settings (N=23 participants), demonstrating improved communication in collaborative ML projects. However, these studies measure framework *utility* when used, not *adoption rates* in voluntary practice. Our work complements this literature by measuring how often these frameworks are actually applied in real-world repositories.

## Empirical Documentation Studies

Recent work has documented severe gaps in current practice. Rondina et al. [@rondina2025documentation] manually assessed 100 ML datasets and found widespread deficiencies in data collection context (lacking in 25% of datasets) and preprocessing transparency (lacking in 40%). Oreamuno et al. [@oreamuno2024ethics] analyzed HuggingFace datasets and identified ethics documentation as the weakest component, with few repositories addressing potential misuse or bias concerns. Gim et al. [@gim2025fair] evaluated FAIR compliance on OpenML, reporting that 0% of datasets achieve "Reusable" status and only 5% meet "Findable" criteria.

These studies establish that documentation gaps exist but share a critical limitation: all use *cross-sectional* measurements capturing current repository state, not initial release documentation. Without temporal precedence validation, we cannot distinguish whether gaps arise from (1) initial non-compliance or (2) documentation degradation over time. Our temporal measurement at T0+90 days addresses this gap, establishing that repositories are non-compliant from initial release.

## Community Engagement and Software Quality

Software engineering research has long studied how community engagement affects project quality. Mockus and Votta [@mockus2000process] demonstrated that commit frequency correlates with code quality in large open-source projects, suggesting sustained development activity reflects cultural rigor. Raymond [@raymond1999cathedral] argued that "many eyeballs make bugs shallow," positing that larger contributor bases improve software outcomes.

Recent work has applied these insights to ML repository practices. Koch et al. [@koch2021community] analyzed GitHub ML repositories and found that star counts and contributor diversity correlate with documentation completeness. However, these studies test *generic community engagement* (stars, forks, contributors) without isolating specific activity dimensions. Our mechanism specificity tests—separately measuring commits, contributors, and issue responsiveness—reveal that only sustained commit activity correlates with documentation (ρ = 0.951), while team diversity shows no relationship (ρ = 0.028). This specificity challenges the "many eyeballs" framing, suggesting documentation is a byproduct of active development workflows, not team size.

## Positioning Our Contribution

Our work differs from prior literature in three ways. First, we provide temporal precedence validation through T0+90 measurement, establishing that documentation gaps exist from initial release rather than emerging through degradation. Second, we test mechanism specificity by isolating commit velocity from contributor count and issue responsiveness, revealing workflow integration as the dominant driver. Third, we characterize component-level heterogeneity (licensing 27%, preprocessing 52%, data context 77%), identifying licensing as a critical barrier despite being mechanically simpler than other components.

These contributions enable targeted interventions: rather than generic "raise awareness" campaigns, our findings suggest commit-triggered documentation prompts and automated licensing templates would address the 93% non-compliance rate observed at initial release.
