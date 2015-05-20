# Introduction

Extreme scale scientific simulations are leading a charge to exascale
computation, and data analytics runs the risk of being a bottleneck to
scientific discovery. Due to power and I/O constraints, we expect _in situ_
visualization and analysis will be a critical component of these workflows.
Options for extreme scale data analysis are often presented as a stark contrast:
write large files to disk for interactive, exploratory analysis, or perform in
situ analysis to save detailed data about phenomena that a scientists knows
about in advance. We present a novel framework for a third option – a highly
interactive, image-based approach that promotes exploration of simulation
results, and is easily accessed through extensions to widely used open source
tools. This _in situ_ approach supports interactive exploration of a wide range of
results, while still significantly reducing data movement and storage.

More information about the overall design of Cinema is available in the paper,
An Image-based Approach to Extreme Scale In Situ Visualization and Analysis,
which is available at the following link:
[https://datascience.lanl.gov/data/papers/SC14.pdf](https://datascience.lanl.gov/data/papers/SC14.pdf).

This repository contains a Qt based viewer written in Python. This viewer
uses the [cinema_python](https://gitlab.kitware.com/cinema/cinema_python) module
and supports various Cinema specs and formats. Our goal is to continue to grow
this functionality as new features are added to Cinema.

# Requirements

* Python 2.x
* PySide
* cinema_store
* PIL
* numpy

# Basic Usage

```shell
python qt-viewer/Cinema.py PATH/info.json
```
