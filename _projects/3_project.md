---
layout: page
title: Quantitative Neuropathology
description: Deep learning-based measures for quantification of human neuropathology
img: assets/img/neuropathology/brainPaper.png
importance: 3
category: primary
---

Postmortem neuropathology is the gold standard for analysis of neurodegenerative pathologies yet is limited by time-consuming semi-quantitative ratings by experts applied to sparsely sampled brain regions. To address these concerns, the PATCH lab has developed multiple computational tools to digitally quantify neuropathology across the three-dimensional space of the brain. Deep learning-based techniques allow for high throughput analysis of digitally scanned sections and can characterize a wider range of pathological burden than traditional semi-quantitative ratings of pathology. Many of these projects have been done in close collaboration with the Penn Digital Neuropathology Lab, led by Dr. David Irwin. Thus far, we have developed models for quantification of tau pathology in Alzheimer's Disease and TDP-43 pathology in limbic predominant age-related TDP4-3 encephalopathy {% cite yushkevich20213d athalye2025operationalizing denning2024association %}. Using both antemortem and postmortem imaging, we have found strong, regionally specific associations between tau pathology and MTL cortical thickness {% cite ravikumar2024postmortem %} and found that quantitative measurement of tau pathology significantly improved modeling of MTL structure compared to traditional semi-quantitative ratings {% cite denning2024association %}. Further work is underway for quantification of neuron and glial density, amyloid-beta plaques and cerebral amyloid angiopathy, and calcium-binding interneurons.

We are also extending quantitative neuropathology methods to white matter pathology, focusing on the heterogeneous substrates underlying white matter hyperintensities (WMH) on MRI. WMH are prevalent markers of aging and neurodegeneration, yet reflect a mixture of demyelination, vascular injury, inflammation, and axonal loss that volumetric measures cannot disentangle. We developed an automated pipeline for quantifying myelin integrity from LFB-CV stained whole-slide images using optical density normalized against automatically identified intact reference regions, establishing histological ground truth to train models that predict regional myelin loss from in vivo MRI. Ongoing work extends this approach to H&E and immunohistochemical staining modalities, with the goal of developing pathology-specific neuroimaging biomarkers for the distinct substrates of WMH.

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/neuropathology/Figure3D.png" title="3D reconstruction of tau IHC and burden maps" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/neuropathology/Patches.png" title="Example activation maps for tau and TDP-43 pathology" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/neuropathology/wmh.png" title="myelin loss heatmaps registered to MR images" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    Left:Example activation maps for tau and TDP-43 pathology, Middle: 3D reconstruction of tau IHC and burden maps, Right: Myelin loss heatmaps registered to MR images.
</div>

The PATCH Lab has also built a unique dataset of serial histopathology to analyze pathological burden across the 3D extent of the brain, compared to conventional histopathology which is done with sparse sampling in limited brain regions. We developed an automated framework for 3D reconstruction of serial histology co-registered to same-subject postmortem imaging of the medial temporal lobe using multimodality image registration. From this reconstruction we can develop 3D maps of pathological burden, used to characterize the 3D extent of tau pathology across the hippocampal long axis (Yushkevich et al., 2021) and to analyze tau pathological burden within individual MTL subregions (Ravikumar et al., 2024). Serial Nissl staining from this dataset with dense anatomical labeling from the Human Neuroanatomy Laboratory at the University of Castilla La Mancha, led by renounced neuroanatomist Ricardo Insausti, is publicly available at <a href="https://histo.itksnap.org/about">https://histo.itksnap.org/about</a>.