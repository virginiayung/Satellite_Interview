import os
import numpy as np
import matplotlib;matplotlib.use("TkAgg");
import matplotlib.pyplot as plt
import pywt
import otbApplication
import sklearn.decomposition

def Wavelet(rgb, pan, level = 1):

    rgb_coeffs = pywt.wavedec2(rgb, 'db1', level)
    rgb_cA2, (rgbcH2, rgbcV2, rgbcD2), (rgbcH1, rgbcV1, rgbcD1) = rbg_coeffs
    pan_coeffs = pywt.wavedec2(pan, 'db1', level)
    pan_cA2, (pan_cH2, pan_cV2, pan_cD2), (pan_cH1, pan_cV1, pan_cD1) = pan_coeffs
    fused_coeffs = pan_cA2, (pan_cH2, pan_cV2, pan_cD2), (pan_cH1, pan_cV1, pan_cD1)

    print "levels:", len(fused_coeffs)-1
    return pywt.waverec2(fused_coeffs, 'db1')




def PXS(rbg, pan):

    # The following line creates an instance of the Pansharpening application
    pxs = otbApplication.Registry.CreateApplication("Pansharpening")

    # The following lines set all the application parameters:
    pxs.SetParameterString("inp", "QB_Toulouse_Ortho_PAN.tif")

    pxs.SetParameterString("inxs", "QB_Toulouse_Ortho_XS.tif")

    pxs.SetParameterString("out", "Pansharpening.tif")
    pxs.SetParameterOutputImagePixelType("out", 3)

    # The following line execute the application
    pxs.ExecuteAndWriteOutput()

    return pxs

def PCA(rbg, pan):

    n_col = pan.shape[1]
    pca = PCA(n_components=n_col)
    pan_components = pca.fit_transform(train_feat)


    pca_range = np.arange(n_col) + 1
    xbar_names = ['PCA_%s' % xtick for xtick in pca_range]
    plt.bar(pca_range, pca.explained_variance_ratio_, align='center')
    xticks = plt.xticks(pca_range, xbar_names, rotation=90)
    plt.ylabel('Variance Explained')

