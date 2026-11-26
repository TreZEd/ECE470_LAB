#!/usr/bin/env python

'''

lab7pkg_pick_place/lab7_img.py

@brief: image processing for lab6, including template matching, image filtering, edge detection, contour detection, etc.
@author: Songjie Xiao
@date: Monday 2023/3/20

'''

#########################################################################
#
#  Lab 6-Image Processing
#  Main task is to pick and place all the blocks to your destination.
#  Camera is used to detect blocks. With image processing methods, 
#  robot is able to know the position, shape and orientation of the blocks.
#  Since block's position is based on image coordinate, what we should do
#  is to transform it into robot coordinate.
# 
#  In this lab, you only need to complete the image processing part.
#
#########################################################################

import cv2
import numpy as np
import json
from pathlib import Path

class ImageProcess():
    def __init__(self):

        self.contours_elip = []
        self.contours_rect = []

    def template_process(self, img_path):

        # read image from img_path
        img_temp = cv2.imread(img_path)

        if img_temp is None:
            print('Template Image is None, Please check image path!')
            return
        
        img_copy = img_temp.copy()

        # Bilateral Filter smooths images while preserving edges,
        # by means of a nonlinear combination of nearby image values.
        # cv2.bilateralFilter(src, d, sigmaColor, sigmaSpace)
        # d - Diameter of each pixel neighborhood that is used during filtering.
        img_blur = cv2.bilateralFilter(img_copy, 19, 130, 30)

        # cv2.medianBlur() is used to reduce noise in the image
        img_blur = cv2.medianBlur(img_blur, 9)

        # cv2.cvtColor() is used to convert the image to grayscale
        img_gray = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)

        # cv2.Sobel() is used to find the gradient of the image
        x_grid = cv2.Sobel(img_gray, cv2.CV_16SC1, 1, 0)
        y_grid = cv2.Sobel(img_gray, cv2.CV_16SC1, 0, 1)
        # cv2.Canny() is used to find the edges of the image
        img_canny = cv2.Canny(x_grid, y_grid, 30, 220)

        # split image into two parts, rectangle and ellipse
        weight, height = img_canny.shape
        img_rect = img_canny[:, :weight]
        img_elip = img_canny[:, weight:]

        # cv2.findContours to find contour
        # variable contours_1 stores all contours, each of which is composed of a series of pixel point 
        # For example: len(contours) contours[0] 
        # rectangle
        self.contours_rect, hierarchy = cv2.findContours(img_rect, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # elipse
        self.contours_elip, hierarchy = cv2.findContours(img_elip, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Test code
        # cv2.imshow('canny image', img_canny)
        # cv2.waitKey()
        # cv2.destroyAllWindows()
        # print('contours_rect: ', self.contours_rect)
        # print('length of rectangle: ', len(self.contours_rect))
        # print('example of rectangle: ', self.contours_rect[0])
        # print('contours_elip: ', self.contours_elip)
        # print('length of ellipse: ', len(self.contours_elip))
        # print('example of ellipse: ', self.contours_elip[0])

    def image_process(self, img_path):

        # read image from img_path
        img_src = cv2.imread(img_path)

        if img_src is None:
            print('Source Image is None, Please check image path!')
            return
        
        img_copy = img_src.copy()

        ############## Your Code Start Here ##############
        # TODO: image process including filtering, edge detection, contour detection and so on.
        
        # Important: check contours and make sure the contour is available.
        # For one block, there will be 4 contours, 2 for rectangle or ellipse outside and 2 for arrow inside.
        # For one rectangle edge, there will be 2 contours in image resolution.
        # Tips: use cv2.contourArea(contour) as threshold to filter out the contour.

        pass

        ############### Your Code End Here ###############

        # length of contours equals to 4 times the number of blocks
        print("length of contours: ", len(contours))

        ############## Your Code Start Here ##############
        # TODO: compute the center of contour and the angle of arrow,
        # as well as match shapes of your block
        center_value = []
        shape = [] # 0 represents rectangle while 1 represents ellipse
        theta = []
        for i in range(len(contours) // 2):
            if i % 2 == 0:
                ############## Your Code Start Here ##############
                # TODO: compute the center of external contour (rectangle/ellipse) and match shapes of your block
                # Tips: ret = cv2.matchShapes(contour1, contour2, 1, 0.0) 

                # cv2.circle(draw_img, (int(center_x), int(center_y)), 7, [0,0,255], -1)

                pass

                ############### Your Code End Here ###############

            else:
                # compute the center of internal contour (arrow) and compute the angle of arrow
                N = cv2.moments(contours[i * 2])
                _center_x = int(N["m10"] / N["m00"])
                _center_y = int(N["m01"] / N["m00"])
                # draw a circle on the center point
                cv2.circle(img_copy, (int(_center_x), int(_center_y)), 7, [0,255,0], -1)

                ############## Your Code Start Here ##############
                # TODO: compute the angle of arrow
                # Tips: compute the distance between center point of external contour and every point of internal contour,
                # find the furthest point, then you can compute the angle.

                # cv2.line(draw_img, (_center_x, _center_y), (x, y), (128, 0, 0), 2)

                pass

                ############### Your Code End Here ###############

        cv2.imshow('image with center and orientation', img_copy)
        cv2.waitKey()
        cv2.destroyAllWindows()

        return center_value, shape, theta

def load_calibration(calibration_path=None):
    """Read private paired points from a local file; keep this file out of Git."""
    if calibration_path is None:
        calibration_path = Path(__file__).with_name("camera_world_calibration.json")
    with open(calibration_path, "r", encoding="utf-8") as calibration_file:
        calibration = json.load(calibration_file)
    return calibration["camera_points"], calibration["world_points"]

def coordinate_transform(center_cam, center_robot, center_snap):
    """Convert camera pixels to world coordinates using paired calibration data.

    center_cam: N paired [xc, yc] pixel coordinates.
    center_robot: N paired [xt, yt] or [xt, yt, zt] world coordinates.
    center_snap: M [xc, yc] pixel coordinates to transform.
    Returns M world-coordinate lists in the calibration data's units.

    With at least three non-collinear pairs, fit an affine map by least
    squares using every pair. For XYZ output, zt is an estimate on the
    calibration plane, not a measurement of an object's arbitrary depth.
    Two XY pairs retain the manual's swapped-axis transformation.
    """
    cam = np.asarray(center_cam, dtype=float)
    world = np.asarray(center_robot, dtype=float)
    snap = np.asarray(center_snap, dtype=float)

    if cam.ndim != 2 or cam.shape[1] != 2 or len(cam) < 2:
        raise ValueError("center_cam must contain at least two [xc, yc] pairs.")
    if (world.ndim != 2 or world.shape[0] != len(cam)
            or world.shape[1] not in (2, 3)):
        raise ValueError("center_robot must contain one XY or XYZ row per camera point.")
    if snap.ndim == 1 and snap.size == 0:
        snap = snap.reshape(0, 2)
    if snap.ndim != 2 or snap.shape[1] != 2:
        raise ValueError("center_snap must have shape (M, 2).")
    if not all(np.isfinite(points).all() for points in (cam, world, snap)):
        raise ValueError("Coordinates must contain only finite numbers.")

    if len(cam) == 2:
        if world.shape[1] != 2:
            raise ValueError("XYZ calibration needs at least three non-collinear pairs.")
        delta = cam[1] - cam[0]
        if np.any(np.isclose(delta, 0.0)):
            raise ValueError("Two-point calibration needs different xc and yc values.")
        ratios = (world[1] - world[0]) / delta[::-1]
        return (world[0] + (snap - cam[0])[:, ::-1] * ratios).tolist()

    # [xc, yc, 1] @ coefficients = [xt, yt] or [xt, yt, zt].
    design = np.column_stack((cam, np.ones(len(cam))))
    coefficients, _, rank, _ = np.linalg.lstsq(design, world, rcond=None)
    if rank < 3:
        raise ValueError("Calibration camera points must not all lie on one line.")

    targets = np.column_stack((snap, np.ones(len(snap))))
    return (targets @ coefficients).tolist()

def lab_imgproc(center_robot1=None, center_robot2=None):
    """Use the local calibration pairs by default, or two supplied XY pairs."""

    # init image path
    # template image for template matching of rectangle and ellipse
    path_template = "../img/template.jpg"
    # two calibration images to calculate the image coordinate
    # with corresponding image coordinate and robot coordinate, 
    # a linear transformation between image coordinate and robot coordinate can be computed
    path_img_cali1 = '../img/img_cali_1.bmp'
    path_img_cali2 = '../img/img_cali_2.bmp'
    # snapshot image saved by your camera
    path_img_snap = '../img/img_snap.bmp'

    # init ImageProcess class
    img_process = ImageProcess()

    # template process to get the contour of rectangle and ellipse
    img_process.template_process(path_template)

    if center_robot1 is None and center_robot2 is None:
        # Keep measured pixel/world positions in the private local JSON file.
        center_cam, center_robot = load_calibration()
    elif center_robot1 is None or center_robot2 is None:
        raise ValueError("Provide both two-point XY coordinates, or neither.")
    else:
        # Preserve the original manual-based two-point XY workflow.
        center_cali1, _, _ = img_process.image_process(path_img_cali1)
        center_cali2, _, _ = img_process.image_process(path_img_cali2)
        center_cam = [center_cali1[0], center_cali2[0]]
        center_robot = [center_robot1, center_robot2]

    # Locate the blocks in the current scene and transform their pixel centers.
    center_snap, shape_snap, theta_snap = img_process.image_process(path_img_snap)

    center_snap_robot = coordinate_transform(center_cam, center_robot, center_snap)

    return center_snap_robot, shape_snap, theta_snap
