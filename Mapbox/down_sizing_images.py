                l8sr = os.path.join(self.subdir_path,img_file)
                with rio.open(l8sr, 'r') as src:
                    rl8, gl8, bl8 = src.read((1, 2, 3))

g_1 = g[:,:-1]

g_1 = g[:,:-1]

g_2 = g_1[:-1]

g_2.shape
(7830, 7680)


new_l8 = np.dstack((r_2, g_2, b_2))

new_src = src.meta
new_src.update(height=7830,width=7680)


    for i in np.arange(4):
        a = with_alpha[:,:,i]
        dst.write_band(i+1, a)
with rio.open('I4/new_l8sr.tif', 'w', **new_src) as dest:
	for i in np.arange(3):
		data = new_l8[:,:,i]
		dest.write_band(i+1, data)


with rio.open('I4/LC80360372015072LGN00_B8.TIF', 'r') as b8src:
	b8 = b8src.read(1)

b8_1 = b8[:,:-1]
b8_1 = b8[:,:-1]
b8_2 = b8_1[:-1]

newb8_src = b8src.meta
newb8_src.update(height=15660,width=15360)
with rio.open('I4/new_l8sr_b8.tif', 'w', **newb8_src) as destb8:
	destb8.write_band(1, b8_2)




				# for i, data in enumerate(rgb):
			# 	done = (data * ratio).astype(np.uint16)
			# 	print(np.amax(done)) # for debugging, whether overflow. typically 40%, 30k
			# 	# print(done.shape)
			# 	# print(wind, w, h)
			# 	# print done[0]
			# 	dest.write_band(i+1, done, window=wind)



with rio.open('pretty_resultACRGB0.2.tif', 'r') as src:
    r, g, b = src.read((1, 2, 3))

b2_meta = src.meta
b2_meta.update(count=1)
with rio.open('pretty_resultACRGB0_b2.tif','w', **b2_meta) as dest:
	dest.write_band(3, b)
with rio.open('pretty_resultACRGB0_b3.tif','w', **b2_meta) as dest:
	dest.write_band(1, g)
with rio.open('pretty_resultACRGB0_b4.tif','w', **b2_meta) as dest:
	dest.write_band(1, r)


# brighten image for visual inspection
convert -sigmoidal-contrast 35,15% resultACRGB0.2.tif pretty_resultACRGB0.2.tif

# extract each band from image
gdal_translate -b 1 pretty_resultBrovey0.24.tif pretty_resultBrovey0.24.b4.tif
gdal_translate -b 2 pretty_resultBrovey0.24.tif pretty_resultBrovey0.24.b3.tif
gdal_translate -b 3 pretty_resultBrovey0.24.tif pretty_resultBrovey0.24.b2.tif

# downsize each band
gdal_translate -outsize 75% 75% pretty_resultBrovey0.24.b4.tif down_pretty_resultBrovey0.24.b4.tif
gdal_translate -outsize 75% 75% pretty_resultBrovey0.24.b3.tif down_pretty_resultBrovey0.24.b3.tif
gdal_translate -outsize 75% 75% pretty_resultBrovey0.24.b2.tif down_pretty_resultBrovey0.24.b2.tif

# stack bands back into image
gdal_merge.py -co photometric=RGB -separate -o merge_brovey.tif down_pretty_resultBrovey0.24.b4.tif down_pretty_resultBrovey0.24.b3.tif down_pretty_resultBrovey0.24.b2.tif

# convert to png format
convert merge_brovey.tif merge_brovey.png

