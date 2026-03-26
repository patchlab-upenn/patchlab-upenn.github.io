---
layout: page
title: MTL Postmortem Imaging
description: High-Resolution Postmortem Imaging of the Human Medial Temporal Lobe
img: assets/img/exvivo_mtl/sadhana_atlas.png
importance: 1
category: primary
related_publications: true
---

The PATCH lab has done extensive work in the field of ex vivo human brain imaging, including developing algorithms for postmortem MRI segmentation, reconstruction and registration of serial histology to MRI, pathology quantification, building probabilistic atlases from multiple MRI scans, and in vivo to ex vivo MRI registration. The hippocampus and the medial temporal lobe (MTL) have been the main areas on which this work has focused. These structures are of crucial importance in neurodegenerative diseases, since **the earliest AD-related neurodegeneration occurs in the MTL**. This project is a close collaboration with the [Human Neuroanatomy Laboratory](https://www.uclm.es/albacete/farmacia/lnh#menu-personal) at the University of Castilla-La Mancha in Albacete, and renouned neuroanatomist Ricardo Insausti (1954-2024). 

Using postmortem MRI and histology from increasingly large datasets, we built **first-of-its-kind probabilistic atlases of the human hippocampus** {% cite adler18 %} and **human medial temporal lobe (MTL)** {% cite ravikumar24 %}. These atlases describe the average/characteristic shape of these structures, their composition into anatomical subregions, and provide a reference space for statistical analysis. More recently, we used serial immunohistochemistry (IHC) to **describe the 3D distribution of tau neurofibrillary tangle pathology in the MTL** and characterize the associations between tau load and MTL thinning, while accounting for co-pathologies such as TDP-43 {% cite yushkevich21 ravikumar24 %}. 

<div class="row">
    <div class="col-sm-4 mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/exvivo_mtl/sadhana_atlas_full.png" title="Postmortem atlas of the MTL" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm-8 mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/exvivo_mtl/sadhana_tau.png" title="Map of average tau burden in early and late Braak stages" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Left: Postmortem atlas of the medial temporal lobe. Right: Three-dimensional maps of average tau NFT burden density in the MTL for early and late Braak stages. From {% cite ravikumar24 %}.
</div>

This research direction remains active, funded by NIH grant R01AG056014. We are collecting a dataset of serial histology and 9.4T MRI in >100 brain donors on the Alzheimer's disease continuum, characterizing variability in patterns of spread of tau pathology in the MTL and how tau spread is impacted by beta-amyloid pathology and co-pathologies. We are also embarking on 3D mapping of other histologically-derived markers, including neuronal density, calcium-binding interneurons, and beta-amyloid plaques.  