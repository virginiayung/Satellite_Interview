import os
import rasterio as rio
import numpy as np
from rasterio.warp import reproject, RESAMPLING
import pywt
from sklearn.decomposition import PCA
from sys import argv
from PIL import Image
import time
from Pipeline_CommonFunctions import clean_file_lst
from Brovey_Methods import Brovey, Brovey_ACRGB
# from Other_Methods import Wavelet, PXS

blocksize=2048
     
matht = np.float32
np.seterr(invalid='ignore', divide='ignore')


def calculateRunTime(function, *args):

    """
    run a function and return the run time and the 
    result of the function if the function requires arguments, 
    those can be passed in too
    """

    startTime = time.time()

    return time.time() - startTime


def half_window(window):
    """
    Computes the half-window size, used for scaling RGB 
    ban images
    """

    ((fr, tr), (fc, tc)) = window
    return ((int(fr/2), int(tr/2)), (int(fc/2), int(tc/2)))
 
def make_windows(w, h):
    """
    makes windows of size equivalent to 
    pan ban image

    """
    for x in range(int(w/blocksize+1)):
        for y in range(int(h/blocksize+1)):
            yield (
                (y*blocksize, min(h-1, (y*blocksize)+blocksize+2)), # hint: this is prolly where the off-by-one is!
                (x*blocksize, min(w-1, (x*blocksize)+blocksize+2))
            )

def brovey_rmse(weight,red,green, blue, downsized_pan, out):
    """
    RMSE is the root mean squared error between the 
    average of the 3 bans: RGB and the downsized pan ban image. 
    """

    w = float(weight)
    r, g, b =  (rio.open(f).read(1).astype(np.float32) for f in [red, green, blue])
    p = ((r + g + b*w) / (2+w)).astype(np.uint16)
    
    with rio.open(out, 'w', **rio.open(blue).meta) as dest:
        dest.write_band(1, p)

    A = np.asarray(Image.open(out)).astype(np.float32)
    B = np.asarray(Image.open(downsized_pan)).astype(np.float32)
    error = np.absolute(A - B)
    rmse = np.mean((error**2).flatten())**0.5
    
    return rmse




class Pan_Sharpening(object):

    def __init__(
            self,
            directory_path,
            subdir_path,
            weights,
            pan_sharp_method,
            out,
            half_window = half_window,
            make_windows = make_windows,
            Brovey = Brovey,
            Wavelet = Wavelet,
            PXS = PXS,
            brovey_rmse = brovey_rmse):
        """
        inputs:
                1) directory_path = main directory containing subdirectory and all functions.
                2) subdirectory_path = the subdirectory containing all an images 
                   (b2, b3, b4, b8, and downsized b8) 
                3) pan_sharp_method
                4) weights: range of weights to search on
                5) output image path

        output: pan-sharpened img, rmse
        """
        self.dir_path = directory_path
        self.subdir_path = subdir_path
        self.pan_sharp_method = pan_sharp_method
        self.weights = weights
        self.out = out
        self.make_windows = make_windows
        self.half_window = half_window
        self.brovey = Brovey
        self.brovey_ACRGB= Brovey_ACRGB
        self.pxs = PXS
        self.wavelet = Wavelet
        self.brovey_rmse = brovey_rmse

    def find_weight(self, red, green, blue, downsized_pan):
        dir_rmse = {}
        zoomed_weights = []
        print 'First search within larger range between %f and %f...'\
                       %(float(min(self.weights))/100, float(max(self.weights))/100)

        for big_weight in self.weights:
            rmse_output = self.dir_path + '/rmse_w' + str(big_weight*100) + '.tif'
            big_weight = float(big_weight)/100
            img_rmse =  self.brovey_rmse(big_weight, red, green,blue, downsized_pan, rmse_output)
            dir_rmse[big_weight] = img_rmse

        big_opt_weight = sorted(dir_rmse, key=dir_rmse.get)[0]
        big_opt_weight = int(big_opt_weight * 1000)
        lower = big_opt_weight
        upper = (big_opt_weight) + 21

        print 'Searching within smaller range between %f and %f...'\
                      %(float(lower)/1000, float(upper)/1000)

        for i in range(lower, upper, 1):
            zoom_weight = float(i)/1000
            rmse_output = self.dir_path + '/rmse_w' + str(big_weight*100) + '.tif'
            img_rmse =  self.brovey_rmse(zoom_weight, red, green,blue, downsized_pan, rmse_output)
            dir_rmse[zoom_weight] = img_rmse

        opt_weight = sorted(dir_rmse, key=dir_rmse.get)[0]

        return opt_weight, dir_rmse


    def _check_img_size(self, pan_img, output_size):
        # test function
        # assert size: output image is the same size as the pan ban image
        if pan_img != output_size:
            raise Exception('Image is not the right size!')


    def main(self):
        """
        main function 
        """
        
        
        img_lst = os.listdir(self.subdir_path)

        print 'Running tests with images from this directory...', self.subdir_path
        print 'subdirectory contains these files...', img_lst
        print ''

        for i, img_file in enumerate(img_lst):
            if 'down' in img_file.lower():
                downsized_pan = os.path.join(self.subdir_path,img_file)
            elif 'b2' in img_file.lower():
                blue = os.path.join(self.subdir_path,img_file)
            elif 'b3' in img_file.lower():
                green = os.path.join(self.subdir_path,img_file)
            elif 'b4' in img_file.lower():
                red = os.path.join(self.subdir_path,img_file)
            elif 'b8' in img_file.lower() and 'down' not in img_file.lower():
                pan = os.path.join(self.subdir_path,img_file)
            elif 'l8sr' in img_file.lower():
                l8sr = os.path.join(self.subdir_path,img_file)
                with rio.open(l8sr, 'r') as src:
                    rl8, gl8, bl8 = src.read((1, 2, 3))

        # if 'l8sr' in img_file.lower():
        #     r, g, b= rl8, gl8, bl8
        #     p = rio.open(pan)
        #     color_meta = src.meta
        else:
            r, g, b, p = (rio.open(f) for f in [red, green, blue, pan])
            color_meta = b.meta
        rgb_o = (r, g, b)

        
        pan_meta = p.meta
        w, h = pan_meta['width'], pan_meta['height']
        print "pan image width: %f, pan image height: %f" %(w, h)
        pan_meta.update(photometric='rgb', count=3)

        print '===================== Finding optimal weight for blue band ====================='
        # Find Optimal Weight For Blue Band
        opt_weight, dir_rmse = self.find_weight(red, green, blue, downsized_pan)


        print '===================== Building Image With Weight %s ===================== ' %opt_weight
        print 'img_rmse = ', dir_rmse[opt_weight]
        output_file = self.out + str(opt_weight) + '.tif'

        # Start constructing pan-sharpened image
        with rio.open(output_file, 'w', **pan_meta) as dest:
            startTime = time.time()
            window_count = 1
            for wind in self.make_windows(w, h):
                print 'window number: ', window_count
                print(wind, self.half_window(wind))
                pan = p.read(1, window=wind).astype(matht)
                rgb = list(band.read(1, window=self.half_window(wind)).astype(matht) for band in rgb_o)
                # apply method to compose output image and calculate rmse
                if self.pan_sharp_method == 'Brovey':
                    output_img, ratio= self.brovey(opt_weight,rgb, pan, color_meta, pan_meta, dest, wind)
                
                elif self.pan_sharp_method == 'Brovey_ACRGB':
                    print '=============== Constructing adjusted pan ==============='
                    adjusted_pan= self.brovey_ACRGB(opt_weight,rgb, pan, color_meta, pan_meta, dest, wind)
                    print '=============== Brovey on corrected RGB and adjusted pan ==============='
                    output_img, ratio=self.brovey(opt_weight, rgb, adjusted_pan, color_meta, pan_meta, dest, wind)

                elif self.pan_sharp_method == 'PXS':
                    output_img= self.pxs(rgb, pan)

                elif self.pan_sharp_method == 'Wavelet':
                    output_img= self.wavelet(rgb, pan)
                window_count += 1
   
            # check if output image size matches the pan image size is correct
            # self._check_img_size(pan, output_img)

        run_time = time.time() - startTime
      
        print '====================='
        print ' '     
        print 'run_time: ', run_time


        return sorted(dir_rmse, key=dir_rmse.get)



if __name__ == '__main__':
    # make changes to input so it takes in more than one image
    dir_path = '/Users/heymanhn/ENV/mapbox/pan_sharpening_img2/'
    sub_dir_path = os.path.join(dir_path, 'I2')
    output_img = dir_path + 'output_img'
    fm = Pan_Sharpening(dir_path, sub_dir_path, range(20,70,1), 'Brovey_ACRGB', output_img)
        
    directory_rmse = fm.main()
    print 'sorted weights by ascending rmse: ',directory_rmse
