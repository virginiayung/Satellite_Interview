import os
import rasterio as rio
import numpy as np
from rasterio.warp import reproject, RESAMPLING


def Brovey(weight, rgb, pan, color_meta, pan_meta, dest, wind):
    """
    Brovey Method: Each resampled, multispectral pixel is 
    multiplied by the ratio of the corresponding 
    panchromatic pixel intensity to the sum of all the 
    multispectral intensities.
    """

    weight = float(weight)
    for i, c in enumerate(rgb):
        x = np.empty(pan.shape)
        reproject(
            c, x,
            src_transform=color_meta['transform'],
            src_crs=color_meta['crs'],
            dst_transform=pan_meta['transform'],
            dst_crs=pan_meta['crs'],
            resampling=RESAMPLING.bilinear)

        rgb[i] = x
    sudo_pan = (rgb[0] + rgb[1] + rgb[2]*weight)/(2+weight)
    ratio = pan / sudo_pan

    # for debugging: checking for numerical overflow
    # print 'pan min',np.nanmin(pan)
    # print 'pan max', np.nanmax(pan)
    # print 'pan mean', np.mean(pan) 
    # print 'sudo min',np.nanmin(sudo_pan)
    # print 'sudo max', np.nanmax(sudo_pan)
    # print 'sudo mean', np.mean(sudo_pan) 
    # print 'ratio min',np.nanmin(ratio)
    # print 'ratio max', np.nanmax(ratio)
    # print 'ratio mean', np.mean(ratio)  

    for i, data in enumerate(rgb):
        print i
        pan_sharpened_img = (data * ratio).astype(np.uint16)
        print 'weight:', weight
        print'amax:', (np.amax(pan_sharpened_img))  # typically 40% of data, roughly 30k
        dest.write_band(i+1, pan_sharpened_img, window=wind)

    return pan_sharpened_img,ratio

def Brovey_ACRGB(weight, rgb, pan, color_meta, pan_meta, dest, wind):
    """
    Alternative Brovey Method:
    For every multispectral pixel M, we find it's corresponding 
    2*2 panchromatic pixel P[0], P[1], P[2], P[3]. 
    we trust the *overall* brightness of M more, but we trust 
    P to tell us how that brightness is *distributed* inside the neighborhood.

    avg_rgb = avg(or weighted avg) of the atmospherically corrected 
            multispectral pixels M from 3 bands
    avg_pan = sum(P[0] + P[1] + P[2] + P[3])/ 4
    ratio = avg_rgb/avg_pan
    Scale each of P by ratio to get adjusted P
    Then apply Brovey on Adjusted RGB and Adjusted P
    """

    weight = float(weight)

    avg_rgb = (rgb[0] + rgb[1] + rgb[2]*weight)/(2+weight)
    # For each M  (X, Y pixel coords) , take X, X + 1, Y, Y + 1 of P 
    print avg_rgb.shape

    count = 0
    avg_pan = np.empty((pan.shape[0]/2, pan.shape[1]/2))

    for i in xrange(pan.shape[0]-1):
        for j in xrange(pan.shape[1]-1):
            avg = float(np.sum(pan[i][j] + pan[i+1][j] + pan[i][j+1] + pan[i+1][j+1]))/4
            if i%2 == 0 and j%2 == 0:
                x = i/2
                y = j/2
                count += 1
                avg_pan[x][y] = avg
    
    ratio = avg_rgb / avg_pan
    print 'ratio', ratio.shape

    adjusted_ratio = np.empty(pan.shape)

    for i in xrange(avg_pan.shape[0]):
        for j in xrange(avg_pan.shape[1]):
            x = i * 2
            y = j * 2
            if x%2 == 0 and y%2 == 0:
                adjusted_ratio[x][y] = ratio[i][j]
                adjusted_ratio[x+1][y] = ratio[i][j]
                adjusted_ratio[x][y+1] = ratio[i][j]
                adjusted_ratio[x+1][y+1] = ratio[i][j]
            
    print adjusted_ratio.shape

    adjusted_pan = (pan * adjusted_ratio).astype(np.uint16)

    print'amax:', (np.amax(adjusted_pan))
    print'output shape:',(adjusted_pan.shape)
    dest.write_band(1, adjusted_pan, window=wind)

    return adjusted_pan










