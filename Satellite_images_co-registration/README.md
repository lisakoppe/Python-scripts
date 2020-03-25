# Automatic co-registration of satellite images

### Objective
Automatically detect and correct the slight offset/shift between two or more high resolution satellite images.

### Data

The script has here been tested on two images of the port of the city of Tanabe in Japan in 2016 and 2020:
![Tanabe, Japan](https://github.com/lisakoppe/Python-scripts/blob/master/Satellite_images_co-registration/images/Tanabe_JP.jpeg)

I modified the transparency of the layers in order to create an overlay of images to visually evaluate the gap between the two pictures. The following photo focuses on a set of points of interest located along the edge of the dock which highlights the misalignment between the two images:
![Offset](https://github.com/lisakoppe/Python-scripts/blob/master/Satellite_images_co-registration/images/visual_offset.jpeg)

### Data and tools exploration

Before any data manipulation, the goal of the mission must be clearly specified in order to stick to the client's needs and provide relevant results. In the case of multi-temporal images of the same area, here a part of the port of Tanabe, I am assuming that the mission is relative to changes detection in time-series satellite images. It is then extremely important to ensure that the source images are precisely co-registered and orthorectified. In order to provide relevant site surveillance products, the quality of the data and its preparation are major topics to be addressed at the very beginning of the project.

Automatic co-registration of satellite images focuses on one of the first pre‐processing steps of the image analysis process: ensuring dataset quality and coherence.

These images are covering the same area, but a slight imagery offset remains between the two images. This phenomenon can be partly due to camera distortions, atmospheric conditions or even slight orbit modifications of the satellite (e.g. collision avoidance manoeuvres).

Images which do not line up perfectly with each other are frequently encountered in satellite imagery and many algorithms have been developed to enable manual, semi or fully automatic displacement correction in the literature.

The state of the art gathers two groups of co-registration techniques:

**Intensity-based techniques:** these techniques rely on the recognition of similar grey value patterns between different shots of the same area. This approach does not depend on the presence of significant image features. It is relevant for non-excessive image distortions, but it might consume a big amount of computational power.

**Feature-based techniques:** these techniques detect the image positions of ground objects based on distinct recognition features, such as the sharp edges of docks or dikes which are not subject to change in time and space. Unlike intensity-based techniques, the feature-based techniques are less computationally expensive and have the potential to precisely quantify misalignment vectors. This technique has a strong dependency on Earth's surface appearance which limits the generalization usage of the algorithm.

Here it seems that the images are not georeferenced thus the corners coordinates are not properly defined. For now, I consider these key characteristics missing and I will then direct my research towards methods which don't need these data.

### Offset detection and correction method

The limitations encountered in this mission were clearly revealed. To summarize, I suggest providing the list of the constraints faced here:

- Need for fully automated image preprocessing (offset detection and correction).
- Use regardless of spatial characteristics (non-georeferenced data).
- Work despite the point of interest changes (temporal land cover dynamics).
- Need for fast and efficient computation (considering growing remote sensing data volume).
- But also ensure robustness against high degree of cloud coverage for example.
- The previous test made me think of three scenarii for algorithm design depending on the data available:

**1. Availability of georeferenced data:** use AROSICS algorithm and automatically align images (not possible here).

**2. Georeferences not available:**
        2.1. Artificially recreate spatial coordinates based on other images of the same area and other sources or use ground control points and then use AROSICS (may be quite hard and time-consuming to implement).
        2.2. Use intensity-based techniques together with feature-based techniques in order to align the two (or more) images based on stable keypoints (e.g. the yet unmodified docks and dike sides).

Here, the approach 2.2. seems to be quite accurate. A feature-based approach can be used to detect interesting stable points in an image (called keypoints or feature points) and then match them with the feature points in the other image. A transformation matrix is then calculated based on the matching features and the target image can then be aligned with the reference image.

Here are the steps that could be implemented in order to re-create interest points, identify and apply coordinate transformation and then remove the offset:

**1. Automatically detect and select interest points/keypoints** (extract features) using interest point corner detectors algorithm which calculates each pixel’s gradient, for example. The pixel will be judged as being a corner if the absolute gradient values are not close to 0 in two directions.

**2. Extraction of feature descriptor of the local image structure** for an efficient matching of features across images to be registered. Given an interest point (x, y) the descriptor is formed by a patch centered at (x, y). Descriptors basically are histograms of the image gradients to characterize the appearance of an interest point. Descriptors add a kind of "context" to the pixels.

**3. Matching of local features:** once descriptors are extracted, it is necessary to find the matches between the two images. The nearest neighbors are then recorded and the Euclidian distances between them are recorded to get a more precise idea of the "neighborhood" of interest points. These distances can then be sorted and filtered to keep only the smallest ones in order to reduce computation load and improve accuracy.

**4. Estimate Homography:** compare the interest points selected of the two images and estimate the offset with a simple 3×3 matrix called Homography. Homography basically maps the keypoints in the reference image to the corresponding keypoints in the target one. An iterative algorithm (usually RANSAC) can be used to estimate the parameters of the transformation type needed to align the images. Another frequently used method applies the phase correlation approach (using fast Fourier transform) to a pair of images to create a third one showing a peak corresponding to the relative translation between the images.

**5. Image warping:** apply the set of transformations obtained with the homography matrix to re-align one image to the other and save the data.

**6. Method evaluation:** as in every model, the accuracy must be measured together with other metrics to evaluate its efficiency and make relevant adjustments.

In order to test this approach with Python, I am using the OpenCV library because several keypoint detectors are already implemented in the package (e.g. SIFT, SURF, and ORB). Here, I chose to use the ORB detector because the literature advertises it as having the best matching performance and because it saves computation cost. Moreover, SIFT and SURF detectors are patented so ORB seems to be a good choice for now. According to the previously detailed methodology, I designed the following code to try to align the port of Tanabe's photos: [script available here](https://github.com/lisakoppe/Python-scripts/blob/master/Satellite_images_co-registration/Images_co-registration.py)

### Results

The outputted features matching image:
![Features matches](https://github.com/lisakoppe/Python-scripts/blob/master/Satellite_images_co-registration/images/feature_matches.jpeg)

The newly aligned target image compared to the reference image:
![Alignment](https://github.com/lisakoppe/Python-scripts/blob/master/Satellite_images_co-registration/images/alignment.gif)

### Conclusion, next steps, and improvements

After running the algorithm, it visually seems that the images got quite properly co-registered (when having a look at the docks edges). It even managed to align the images despite the land modifications and the boats navigating. However, some buildings (3D shapes) remain not properly aligned, which could lead to potential errors while running CNN in later use cases.

In order to get a fully operational product, improve efficiency and accuracy and potentially ensure generally usable co-registration here are the steps I would go through:

**Step 1:** Current model adjustment:
- Test the current model by adjusting the maximum number of features to be retained (max_features) and the percentage of matches to be kept (match_rate) to find the optimal set of parameters.
- Try to change the matcher method and the estimation technique while calling the ".findHomography" method.

**Step 2:** Other models testing and scale-up:
- Dig deeper into the different techniques mentioned earlier.
- Evaluate their characteristics, the results of the tests already implemented in the literature, the error rates and check the limitations encountered.
- Select at least two techniques for further exploration.
- Check the relevance of the chosen techniques according to the business needs (mission purpose).
- Test the selected techniques on the port of Tanabe images and collect more images of the same area if possible.
- Test on georeferenced and non-georeferenced images of the same area and evaluate the methods.
- According to the results, apply slight functions and rates adjustment to reach a better accuracy score.
- Try to generalize the algorithm to other scenes to make it generally usable if possible. If generalization is not relevant, then focus on a specified algorithm to address port surveillance specificities for example.
- Implement the chosen model into a robust architecture to be able to do the transformation on an "unlimited" number of images and not only two images as demonstrated earlier.
- Keep improving and regularly test the model on different images from different sources.
