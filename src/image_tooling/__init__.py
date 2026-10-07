import os
import PIL
import numpy as np
import pydicom
import json
import click


def open_dicom_file(filename):
    """Function for opening a DICOM file. Returns False if this fails.
    
    Args:
        filename (string): path to the file of interest

    Returns:
        dicom: pointer for the opened dicom file.
               If the file failed to open this will be 'False' instead. 
    """

    try:
        dicom = pydicom.dcmread(filename)
    except:
        print(f"Failed to open {filename}.")
        return False
    else:
        return dicom

def load_image_from_dicom(dicom) -> np.ndarray:
    """Function for extracting image from DICOM datafile
    
    Args:
        dicom: the opened dicom file

    Returns:
        image: numpy array containing image data
    """

    try:
        image = dicom.pixel_array
    except:
        print(f"Failed get image from DICOM file.")
        return False
    else:
        return image
    

def load_mask() -> dict:
    print("loading mask information as a dictionary")

def mask_image() -> np.ndarray:
    print("masking image")

def write_image() -> None:
    print("writing image")



def main() -> None:
    print("Hello from image-tooling!")


if __name__ == '__main__':
    main()