import rasterio as rio
import numpy as np
from rasterio.warp import reproject, RESAMPLING
 
blocksize=2048 #2048
 
matht = np.float32
np.seterr(invalid='ignore', divide='ignore')
 
 
def half_window(window):
	((fr, tr), (fc, tc)) = window
	return ((int(fr/2), int(tr/2)), (int(fc/2), int(tc/2)))
 
def make_windows(w, h):
 for x in range(int(w/blocksize+1)):
 	for y in range(int(h/blocksize+1)):
 		yield (
 			(y*blocksize, min(h, (y*blocksize)+blocksize+2)), # hint: this is prolly where the off-by-one is!
			(x*blocksize, min(w, (x*blocksize)+blocksize+2))
		)
 
def main(red, green, blue, pan, weight,out):
	weight = float(weight)
	r, g, b, p = (rio.open(f) for f in [red, green, blue, pan])
	rgb_o = (r, g, b)
	
	color_meta, pan_meta = b.meta, p.meta
	w, h = pan_meta['width'], pan_meta['height']
	print(w, h)
	pan_meta.update(photometric='rgb', count=3)
	
	with rio.open(out, 'w', **pan_meta) as dest:
		for wind in make_windows(w, h):
			# print(wind, half_window(wind))
			pan = p.read_band(1, window=wind).astype(matht)
			print 'pan after', pan.shape
			rgb = list(x.read_band(1, window=half_window(wind)).astype(matht) for x in rgb_o)
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


			print weight
			print 'RESAMPLING.bilinear'

			# # print 'pan min',np.nanmin(pan)
			# # print 'pan max', np.nanmax(pan)
			# # print 'pan mean', np.mean(pan) 

			# # print 'sudo min',np.nanmin(sudo_pan)
			# # print 'sudo max', np.nanmax(sudo_pan)
			# # print 'sudo mean', np.mean(sudo_pan) 
			ratio = pan / sudo_pan
			print sudo_pan.shape
			print ratio.shape
			print pan.shape
			# # print 'ratio min',np.nanmin(ratio)
			# # print 'ratio max', np.nanmax(ratio)
			# # print 'ratio mean', np.mean(ratio)   # ratio .9 to 1.1
 
			# for i, data in enumerate(rgb):
			# 	done = (data * ratio).astype(np.uint16)
			# 	print(np.amax(done)) # for debugging, whether overflow. typically 40%, 30k
			# 	# print(done.shape)
			# 	# print(wind, w, h)
			# 	# print done[0]
			# 	dest.write_band(i+1, done, window=wind)
	print('that was cool and fun')
 
if __name__ == '__main__':
	import sys
	main(*sys.argv[1:])
	# convert -sigmoidal-contrast 25,13% /Users/heymanhn/ENV/mapbox/pan_sharpening_img/brovey1.tif pretty_brovey1.tif






# pan min 0.0
# pan max 47623.0  # a little high
# pan mean 7202.28 # reasonable
# sudo min 0.0
# sudo max 30301.9889706    # reasonable
# sudo mean 7290.84804641   # reasonable
# ratio min 0.0
# ratio max inf
# ratio mean nan




