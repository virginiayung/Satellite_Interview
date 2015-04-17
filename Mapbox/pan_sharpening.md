# What is Pan-Sharpening?
To keep satellite weight, cost, bandwidth and complexity down, many satellite data providers bundle satellite sensors to include two types of imagery: 
* A multispectral image is a four-band (R, G, B, NIR)  image which has low spatial resolution but accurate color data (NIR or near-infrared is optional).
* A panchromatic image is a grayscale image which has higher spatial resolution.

Pan-sharpening is a process of using the  spatial information in the high-resolution grayscale band (panchromatic, or pan-band) and color information in the multispectral bands to create a single high-resolution color image.

  ```
  P pan-pixel cluster + M single multispectral pixel = M pan-sharpened pixel
  ```


This is a multispectral image of San Francisco (the three bands R, G, B stacked)
![mergergb](https://cloud.githubusercontent.com/assets/4450007/7174193/593027cc-e3b8-11e4-8f2c-629a220437ec.png)

This is the corresponding panchromatic image of the same image as above.
![b8](https://cloud.githubusercontent.com/assets/4450007/7174125/48cb1a78-e3b7-11e4-8f48-a692611d3d6c.png)

This is the resulting pan-sharpened image after applying the Weight Brovey Method:
![results 546](https://cloud.githubusercontent.com/assets/4450007/7174473/daa1bf32-e3bd-11e4-85e9-1699c1433949.png)


The Landsat 8 panchromatic band that we work with is not sensitive to blue light. As a result, the spectral characteristics of the raw pansharpened color image may not exactly match those of the corresponding low-resolution RGB image, resulting in altered color tones. This has resulted in the development of many algorithms that attempt to reduce this spectral distortion and to produce visually pleasing images. For more information on pan-sharpening Landsat 8 data and Virginia's sprint, please feel free to skip the next section.

### Comparison of Different Pan-Sharpening Methods

#### Brovey
The Brovey transformation is a sharpening method  that uses a mathematical combination of the color image and high resolution data. Each resampled, multispectral pixel is multiplied by the ratio of the corresponding panchromatic pixel intensity to the sum of all the multispectral intensities. It assumes that the spectral range spanned by the panchromatic image is the same as that covered by the multispectral channels. This is done essentially by increasing the resolution of the color information in the data set to match that of the panchromatic band. Therefore, the output RGB images will have the pixel size of the input high-resolution panchromatic data. Various resampling methods include bilinear, lanczos, cubic, average, mode, min, and max. 

#### Weighted Brovey
Particularly for Landsat 8 imagery data, we know that the pan-band does not include the full blue band, so we take a fraction of blue (optimal weight computed in this sprint) in the pan-band and use this weight to compute the sudo_pan_band, which is a weighted average of the three bands. We then compute the ratio between the pan-band and the sudo-band and adjust each of the three bands by this ratio.

```
sudo_pan = (R + B + B*weight)/(2+weight)
ratio = pan / sudo_pan
R_out = R * ratio
G_out = G * ratio
B_out = B * ratio
```

![screen shot 2015-04-13 at 10 14 29 pm](https://cloud.githubusercontent.com/assets/4450007/7141761/7a277a88-e288-11e4-9dd7-39e3f970603f.png)

#### Weighted Brovey With Atmospherically Corrected RGB Pixel
This method can be used when atmospherically corrected RGB images are available.
For every corrected multispectral pixel, we can combine it with the corresponding 2*2 neighboring uncorrected pan pixels. Since the multispectral pixels are atmospherically correct, we can then use the corrected RGB to modify the overall brightness of pan-band, and use the pan pixels *P* to find out how brightness is distributed inside that 2*2 neighborhood. In this case, we average the RGB to get the expected pan value for that area of 4 pan pixels. We then compute the ratio between the expected and actual (averaging 4 pan pixels) and scale each pan pixel *P* by this ratio to obtained the adjusted pan-pixels. The last step is to use the vanilla Brovey method (listed above) on the atmospherically corrected RGB and the adjusted pan-ban image to obtain the final pan-sharped image.

#### IHS
The IHS transformation first converts the color image to IHS color space. It then replaces the intensity band by the a weighted version of the panchromatic image. Finally, the fused image is converted back to RGB space. IHS fused images generally experience spectral distortion from the original multispectral image. 

#### PCA:
The Principle Component Analysis (PCA) is a common statistical procedure that is used to reduce the dimensionality of multi-dimensional space. It is used for numerous applications in fields like statistics, machine learning, and signal processing.It is an orthogonal transformation that converts a set of correlated observations into a set of linearly uncorrelated values called principal components. This transformation leads to an interesting result - the first principal component accounts for the greatest proportion of variability in the data. 
In this case, it can be used to convert intercorrelated multispectral bands into a set of uncorrelated components.  The first band, which has the highest variance, is then replaced by the Panchromatic image.  We can then obtain the high-resolution pansharpened image by applying an inverse PCA on the PCA.


#### P+XS:
The P+XS is a variational method, which calculates the pansharpened image by minimizing an energy functional. It obtains the edge information of the panchromatic image by using the gradient. The spectral information is obtained by approximating the panchromatic image as a linear combination of the multispectral bands (Ballester, 2007). 

#### Wavelet:
The Wavelet method uses Discrete Wavelet Transforms (DWT) to decompose the original multispectral and panchromatic image into components. For each of the images, there is one component that contains low-resolution information, while the others contain more detailed local spatial information. The low-resolution component of the panchromatic image is replaced by the low-resolution multispectral component. The final image is created by performing an inverse wavelet transformation. 
Runtime in Theory: O(n)

![dwt1](https://cloud.githubusercontent.com/assets/4450007/7141344/da8b2cec-e285-11e4-9253-a3040b076bd2.jpg)

where cJk are the scaling coefficients and djk are the wavelet coefficients. The first term in Eq. (8) gives the low-resolution approximation of the signal while the second term gives the detailed information at resolutions from the original down to the current resolution J. The process of applying the DWT can be represented as a bandk of filters, as in the figure below.

![dwt_components](https://cloud.githubusercontent.com/assets/4450007/7141354/e990abcc-e285-11e4-984b-b35c22e18f6f.jpg)


In case of a 2D image, a single level decomposition can be performed resulting in four different frequency bands namely LL, LH, HL and HH sub band and an N level decomposition can be performed resulting in 3N+1 different frequency bands and it is shown in figure 3. At each level of decomposition, the image is split into high frequency and low frequency components; the low frequency components can be further decomposed until the desired resolution is reached.

#### VWP: 
VWP combines the Wavelet method with P+XS. It uses the geometry matching term from P+XS and spectral information from wavelet decomposition. This method outperforms others by preserving the highest spectral quality (Moeller, 2008).

#### Wavelet + Canny Edge Detector:
<p>Combining DWT with Canny Edge Detectors. More details <a href="http://link.springer.com/chapter/10.1007%2F978-3-642-21783-8_6" title="Title">
here.</a></p>


# Pan-Sharpening Landsat 8 Imagery:

## Summary
For this sprint, my goal is to build out a pipeline that would support any exploratory analysis needed in finding the optimal method for pan-sharpening. 

1. Baseline model with the Brovey methods because they are least computationally intense. 
  * The first step is to search through a range of values and find the optimal weight for the blue band by minimizing RMSE. The current script searches for this weight with a precision of two decimal places.
  * Once we compute the optimal weight we can compute the sudo_pan and the ratio between pan_band and sudo_pan. 
  * Last step is to adjust each band with that ratio.

  ```
  sudo_pan = (R + B + B*optimal_weight)/(2+optimal_weight)
  ratio = pan / sudo_pan
  R_out = R * ratio
  G_out = G * ratio
  B_out = B * ratio
  ```
2. The pipeline also supports any additional pan-sharpening methods (list above). In this sprint, I included three other more computational intense methods-Wavelet, P-XS, and PCA.

#### Python Libraries Required:
##### For all methods: 
- rasterio
- numpy
- PIL
- time (to calculate runtime)

##### For specific methods:
- Wavelet: **pywt**
- P-XS: **otbApplication**
- PCA: **sklearn.decomposition**

### How Are Results Evaluated In This Sprint:

* RMSE - Root Mean Squared Error
We look to minimize RMSE

### Future Evaluation Methods To Consider:
* SID- Spectral Information Divergence
* RASE- Relative Average Spectral Error



## Progress:
### What We Know So Far...
* There is a tradeoff in every method between the spatial and spectral resolution. 
* The choice of method depends on how the fused image will be used.
* From literature, VWP performs the best spectrally. the results derived using P-XS and Wavelet transform typically do not look as sharp as other methods in terms of spatial quality, but therefore preserve the spectral quality from the original multispectral image better.
* prevent overfitting: some methods good for certain imagery
* Landsat 8 does not cover infrared range
* l8sr dataset does not contained atmospherically corrected pan-band image.

### Update 2...
1. Different Resampling Methods Give Different Results: 
  - bilinear
  - lanczos
  - cubic

Below is a comparison of two images constructed using the "bilinear" resampling method (first image) versus the "lanczos" method (second image). Notice the second image is sharper and brighter at higher zoom levels. However, the "lanczos" is more computationally intense than the "bilinear" resampling method.

![results1 0l](https://cloud.githubusercontent.com/assets/4450007/7192784/95b78fec-e44d-11e4-8dfb-81e704c77c74.png)

![results1 0b2](https://cloud.githubusercontent.com/assets/4450007/7192771/84428bc2-e44d-11e4-9a1d-1aca6b9e9988.png)





2. We found the optimal weight! What does that mean?

Below is a comparison of using full 100% of the blue ban (first image) and the optimal weight 56.4% (second image). Notice that the image on the second appears sharper and brighter, this is because the blue ban percentage has been adjusted to remove haze.

![results1 0l](https://cloud.githubusercontent.com/assets/4450007/7192860/9233ae54-e44e-11e4-85d1-563111b46033.png)

![results 546l](https://cloud.githubusercontent.com/assets/4450007/7192865/a5bff9b4-e44e-11e4-805d-c86ca7496207.png)

