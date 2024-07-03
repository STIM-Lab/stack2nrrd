# -*- coding: utf-8 -*-
"""
@author: helioum
"""
import numpy as np
import cv2 as cv
import shutil
import nrrd
import sys
import os

def stack2nrrd(image_path, save_path, coords, dims, N, grayscale=True):
    """
    Converts a stack of 2D images into smaller 3D NRRD blocks and saves.

    Parameters
    ----------
    image_path : str
        Input directory of the large-scale images
    save_path : str
        Output directory for the .nrrd blocks
    coords : tuple
        (x, y, z) coordinates of the starting point for cropping
    dims : tuple
        (sx, sy, sz) dimension to crop along each axis, should be a multiplies of N
    N : int
        Size of each block (final block size is NxNxN)
    grayscale : bool, optional
        Loads images in grayscale mode if True, else in color mode (default is True)

    Returns
    -------
    None

    Description
    -----------
    This function loads a stack of images from the inputed directory, crops them according 
    to the given coordinates and dimensions, and then divides the cropped volume into 
    smaller NxNxN blocks. Each block is saved as an NRRD file in the output directory to be
    later used (segment) in Slicer3D software.

    Examples
    --------
    from stack2nrrd import stack2nrrd
    stack2nrrd("/Data/images", "/blocks_nrrd", (100, 100, 100), (256, 256, 256), 128, True)
    
    or
    
    (terminal) > python stack2nrrd.py /Data/images /blocks_nrrd 100 100 100 256 256 256 128 1
    """
    
    x, y, z = coords
    sx, sy, sz = dims
    
    # check if input dimensions are divisible by N
    if (sx % N != 0) or (sy % N != 0) or (sz % N != 0):
        print('Dimensions must be divisible by N.')
        return

    # load the image list
    images_list = [f for f in os.listdir(image_path) if f.endswith('.bmp') or f.endswith('.jpg') or f.endswith('.tif') or f.endswith('.png')]
    images = []

	# crop each image based on length and width
    for i in range(z, z+sz, 1):
        # load and crop the image, default type: grayscale
        img = cv.imread(os.path.join(image_path, images_list[i]), (cv.IMREAD_GRAYSCALE if grayscale else cv.IMREAD_COLOR))
        img = img[x:x+sx, y:y+sy]
        images.append(img)

    # stack the images to create the whole volume
    volume =  np.stack(images, axis=0)

    # create saving directory and delete previous files
    if os.path.exists(save_path):
        shutil.rmtree(save_path)
    os.makedirs(save_path)

    # crop the volume into NxNxN smaller cubes and save as nrrd file
    nx, ny, nz = [dim // N for dim in (sx, sy, sz)]				# find the number of cubes that fit along each axis
    for x in range(nx):
        for y in range(ny):
            for z in range(nz):
                cube = volume[z*N : (z+1)*N, y*N : (y+1)*N, x*N : (x+1)*N]
                nrrd.write(os.path.join(save_path, f'cubic{N}_{z}_{y}_{x}.nrrd'), cube)



# call the function with parsed arguments (for terminal)
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 9:
        print('Provide the valid inputs.')
    elif len(args) == 9 and args[8] == 'True' or args[8] == 'False':
        print('Please enter (1/0) as (True/False) for grayscale input.')
    coords = tuple(map(int, args[2:5]))
    dims = tuple(map(int, args[5:8]))
    grayscale = True if len(args) < 10 else int(args[9])
    stack2nrrd(args[0], args[1], coords, dims, int(args[8]), grayscale)

