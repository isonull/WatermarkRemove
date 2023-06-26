import os
import json
import cv2
import numpy as np

sift = cv2.SIFT_create()


def wrap_affine(image, matrix):
    shape = [image.shape[1], image.shape[0]]
    return cv2.warpAffine(image, matrix, shape)


def mask_from_channel(image, channel, true_condition):
    return np.uint8(np.where(true_condition(image[:, :, channel]), 1, 0))


def image_and_mask_from_png(path):
    bgra = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # bgra
    mask = mask_from_channel(bgra, 3, lambda x: x != 0)
    bgr = cv2.cvtColor(bgra, cv2.COLOR_BGRA2BGR)
    return bgr, mask


def sift_image_and_mask_from_png(path):
    bgra = cv2.imread(path, cv2.IMREAD_UNCHANGED)  # bgra
    mask = mask_from_channel(bgra, 3, lambda x: x != 0)
    bgr = cv2.cvtColor(bgra, cv2.COLOR_BGRA2BGR)
    sift_image = SiftImage(bgr)
    return sift_image, mask


def sift_image_from_png(path):
    bgr = cv2.imread(path)  # bgr
    return SiftImage(bgr)


class SiftImage:
    def __init__(self, image):  # bgr
        self.image = image
        self.keypoints, self.descriptors = sift.detectAndCompute(image, None)

    def filter_features(self, mask):  # keep feature points in mask == 0
        valid = [mask[int(keypoint.pt[1]), int(keypoint.pt[0])] == 0
                 for keypoint in self.keypoints]
        self.keypoints = [
            self.keypoints[i] for i, v in enumerate(valid) if v]
        self.descriptors = np.float32(
            [self.descriptors[i] for i, v in enumerate(valid) if v])
        return

    def estimate_affine(self, other, matches):
        query_points = np.float32(
            [self.keypoints[match.queryIdx].pt for match in matches])
        target_points = np.float32(
            [other.keypoints[match.trainIdx].pt for match in matches])
        affine_matrix, _ = cv2.estimateAffinePartial2D(
            query_points, target_points)
        return affine_matrix

    def wrap_affine(self, matrix):
        return wrap_affine(self.image, matrix)

    def inspect_image(self):
        return cv2.drawKeypoints(self.image, self.keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
