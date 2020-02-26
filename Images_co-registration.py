# Import Numpy and OpenCV packages
import numpy as np
import cv2

# Create a variable to store each filepath: two input images and two output images
# If you want to run the code on your machine, this is the only part you need to change beforehand
ref_path = 'path/to/your/image'
target_path = 'path/to/your/image'
aligned_image_path = 'path/to/your/image'
matches_path = 'path/to/your/image'

# Create a function to re-align a set of two images


def imagesCoreg(ref_file, target_file, max_features, match_rate):
    '''
    This function allows the co-registration of two images.
    It uses the ORB feature detector from the OpenCV library.
    It takes the following four inputs:
    - ref_file: the image to be considered as the reference for registration
    - target_file: the image to be aligned
    - max_features: the maximum number of features to be retained
    - match_rate: the percentage of matches to be kept
    It outputs three elements:
    - matches_path: a visual map of features' matching
    - aligned_file: the modified/re-aligned target image
    - h_matrix: the computed homography matrix
    '''
    # Read the reference image and the image to be aligned to it (in color)
    img_ref = cv2.imread(ref_file, cv2.IMREAD_COLOR)
    img_target = cv2.imread(target_file, cv2.IMREAD_COLOR)

    # Convert these images to grayscale
    img_ref_gray = cv2.cvtColor(img_ref, cv2.COLOR_BGR2GRAY)
    img_target_gray = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)

    # Detect the ORB features of the two images and compute the corresponding descriptors
    orb = cv2.ORB_create(max_features)
    keypoints_ref, descriptors_ref = orb.detectAndCompute(img_ref_gray, None)
    keypoints_target, descriptors_target = orb.detectAndCompute(img_target_gray, None)

    # Create a Brute-Force descriptors matcher with Hamming distance measurement
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    # Spot the matching descriptors in the two images using the created matcher
    matches = matcher.match(descriptors_ref, descriptors_target, None)

    # Sort descriptors by goodness of match (sorting distances)
    matches.sort(key=lambda x: x.distance, reverse=False)

    # From matches obtained, keep only a small percentage (match_rate) of relevant matches
    nb_correctMatches = int(len(matches) * match_rate)
    matches = matches[:nb_correctMatches]

    # Draw top matches
    img_matches = cv2.drawMatches(img_ref, keypoints_ref, img_target,
                                  keypoints_target, matches, None)
    # Save the image for visual inspection
    cv2.imwrite(matches_path, img_matches)

    # Create two empty arrays to store keypoints locations
    ref_points = np.zeros((len(matches), 2), dtype=np.float32)
    target_points = np.zeros((len(matches), 2), dtype=np.float32)

    # Extract relevant keypoints matches locations in both the images and store them into the arrays
    for i, match in enumerate(matches):
        ref_points[i, :] = keypoints_ref[match.queryIdx].pt
        target_points[i, :] = keypoints_target[match.trainIdx].pt

    # Solve a linear system of equations to find the homography using RANSAC robust estimation technique
    h_matrix, mask = cv2.findHomography(ref_points, target_points, cv2.RANSAC)

    # Store target image shape into corresponding variables
    height, width, channels = img_target.shape
    # Image warping: transform the target image to map it to the reference image
    imgReg = cv2.warpPerspective(img_ref, h_matrix, (width, height))

    # Save the new registered image
    aligned_file = aligned_image_path
    cv2.imwrite(aligned_file, imgReg)

    # Print the estimated homography matrix used to transform the target image
    print('Computed homography matrix: \n', h_matrix)

    # Print output files path
    print('\n Aligned image saved in:', aligned_image_path)
    print('\n Features matching image saved in:', matches_path)

    return imgReg, h_matrix


# Run the imagesCoreg function with the two given images
imgReg, h_matrix = imagesCoreg(ref_path,
                               target_path,
                               max_features=6000,
                               match_rate=0.15)
