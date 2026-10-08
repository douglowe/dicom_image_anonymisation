from pathlib import Path

import click
import numpy as np
import pydicom
import yaml
from PIL import Image


def open_dicom_file(filename):
    """Open a DICOM file and return the dataset or False on failure."""
    try:
        return pydicom.dcmread(filename)
    except Exception:
        return False


def load_image_from_dicom(dicom) -> np.ndarray | bool:
    """Return the pixel data for an opened DICOM image."""
    try:
        return dicom.pixel_array
    except Exception:
        return False


def load_mask(mask_file: str | Path) -> dict:
    """Load and validate a YAML bounding-box mask."""
    try:
        with Path(mask_file).open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise click.ClickException(f"Mask file not found: {mask_file}") from exc
    except yaml.YAMLError as exc:
        raise click.ClickException(f"Unable to parse mask YAML: {mask_file}") from exc

    mask_info = payload.get("mask")
    if not isinstance(mask_info, dict):
        raise click.ClickException("Mask file must contain a top-level 'mask' dictionary.")

    required_fields = ["left-edge", "right-edge", "lower-edge", "upper-edge"]
    missing = [field for field in required_fields if field not in mask_info]
    if missing:
        fields = ", ".join(missing)
        raise click.ClickException(f"Mask file is missing required field(s): {fields}")

    return {
        "left": int(mask_info["left-edge"]),
        "right": int(mask_info["right-edge"]),
        "lower": int(mask_info["lower-edge"]),
        "upper": int(mask_info["upper-edge"]),
    }


def mask_image(image: np.ndarray, mask_data: dict) -> np.ndarray:
    """Apply a bounding-box mask to the image by setting the masked pixels to zero."""
    masked = np.array(image, copy=True)
    left = min(mask_data["left"], mask_data["right"])
    right = max(mask_data["left"], mask_data["right"])
    lower = min(mask_data["lower"], mask_data["upper"])
    upper = max(mask_data["lower"], mask_data["upper"])

    height, width = masked.shape[:2]
    left = max(0, min(width, left))
    right = max(0, min(width, right))
    lower = max(0, min(height, lower))
    upper = max(0, min(height, upper))

    if masked.ndim == 2:
        masked[lower:upper, left:right] = 0
    elif masked.ndim == 3:
        masked[lower:upper, left:right, :] = 0
    else:
        raise click.ClickException("Unsupported image dimensionality for masking.")

    return masked


def write_image(image: np.ndarray, output_path: Path, input_name: str) -> Path:
    """Write the masked image to a lossless PNG file in the output directory."""
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / f"{Path(input_name).stem}.png"

    image_array = np.asarray(image)
    if image_array.ndim == 2:
        pillow_image = Image.fromarray(image_array.astype(np.uint8), mode="L")
    else:
        pillow_image = Image.fromarray(image_array.astype(np.uint8))

    pillow_image.save(output_file, format="PNG")
    return output_file


@click.command(name="image-tooling")
@click.option(
    "--inputfile",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to the input DICOM image file.",
)
@click.option(
    "--outputpath",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory where the anonymised PNG output will be written.",
)
@click.option(
    "--mask",
    "mask_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="YAML file describing the bounding-box mask to apply.",
)
def main(inputfile: Path, outputpath: Path, mask_file: Path) -> None:
    """Apply a bounding-box mask to a DICOM image and export a PNG."""
    dicom = open_dicom_file(str(inputfile))
    if not dicom:
        raise click.ClickException(f"Unable to open DICOM file: {inputfile}")

    image = load_image_from_dicom(dicom)
    if image is False:
        raise click.ClickException(f"Failed to read image data from: {inputfile}")

    mask_data = load_mask(mask_file)
    masked_image = mask_image(image, mask_data)
    output_file = write_image(masked_image, outputpath, inputfile.name)

    click.echo(f"Image written to {output_file}")


if __name__ == "__main__":
    main()