from pathlib import Path

import numpy as np
import pytest
from click.testing import CliRunner
from PIL import Image
from pydicom.dataset import Dataset, FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from image_tooling import main


def write_dicom(path: Path, image: np.ndarray) -> None:
    meta = FileMetaDataset()
    meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.TransferSyntaxUID = ExplicitVRLittleEndian
    meta.ImplementationClassUID = "1.2.3.4.5.6.7.8"

    ds = FileDataset(str(path), {}, file_meta=meta, preamble=b"\0" * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = False
    ds.SOPClassUID = meta.MediaStorageSOPClassUID
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID
    ds.PatientName = "Test^Patient"
    ds.Rows = image.shape[0]
    ds.Columns = image.shape[1]
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = image.astype(np.uint8).tobytes()
    ds.save_as(path, write_like_original=False)


def test_cli_writes_masked_png(tmp_path):
    image = np.full((20, 50), 255, dtype=np.uint8)
    image[8:12, 5:40] = 100
    dicom_path = tmp_path / "sample.dcm"
    write_dicom(dicom_path, image)

    mask_path = tmp_path / "mask.yaml"
    mask_path.write_text(
        """
mask:
  type: bounding-box
  units: pixels
  left-edge: 5
  right-edge: 40
  lower-edge: 8
  upper-edge: 12
""".strip()
    )

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--inputfile",
            str(dicom_path),
            "--outputpath",
            str(output_dir),
            "--mask",
            str(mask_path),
        ],
    )

    assert result.exit_code == 0, result.output
    png_path = output_dir / "sample.png"
    assert png_path.exists()

    with Image.open(png_path) as img:
        pixels = np.array(img)

    assert pixels.shape == (20, 50)
    assert np.all(pixels[8:12, 5:40] == 0)
    assert np.all(pixels[0:8, :] == 255)
