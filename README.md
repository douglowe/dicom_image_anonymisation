# Image Anonymisation Tool

This tool will load an image from a DICOM binary file, apply a mask, and write out a lossless PNG file.

## Requirements and Installation

This tool is written in python. Dependencies are managed by the [uv](https://docs.astral.sh/uv/) package manager.

To install uv follow the [official installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

## Running the Tool

To get the help page use:

```bash
uv run image-tooling --help
```



The options needed to run the tool are:

* `--inputfile <path to input file>`
* `--outputpath <path to output directory>` (note this directory will be created if it does not already exist)
* `--mask <path to mask file>` 



The input file must be a DICOM image file. The output files will always be lossless PNGs. The mask file is a YAML file with the format:

```yaml
mask:
  type: bounding-box
  units: pixels
  left-edge: 5
  right-edge: 40
  lower-edge: 80
  upper-edge: 100
```

Masks will be bounding boxes, defined by the pixel count from the origin of the image (usually the lower-left corner). 