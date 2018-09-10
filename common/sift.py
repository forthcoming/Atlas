#!--coding=utf8--
import cv2
import matplotlib.pyplot as plt
from numpy import *
from scipy.ndimage import filters

# 检测关键点
def detector(gray):
    # 创建sift对象
    sift = cv2.xfeatures2d.SIFT_create()
    # 计算关键点和描述子
    kp, des = sift.detectAndCompute(gray, None)
    # img_sample_kp = cv2.drawKeypoints(gray, kp, gray, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # plt.imshow(img_sample_kp)
    # plt.show()
    return kp, des

# 匹配描述子
def match(des1, des2):
    # BFMatcher with default params
    bf = cv2.BFMatcher(crossCheck=False)
    if len(des1) > len(des2):
        matches = bf.knnMatch(des2, des1, k=2)
    else:
        matches = bf.knnMatch(des1, des2, k=2)
    # 将匹配结果按特征点之间的距离进行降序排列
    # print matches
    # goods = []
    # for mat in matches:
    #     if mat:
    #         # if mat[0].distance < 600:
    #         goods.append(mat)
    # goods = sorted(goods, key=lambda x: x[0].distance)
    # Apply ratio test
    goods = []
    for m, n in matches:
        if m.distance < 0.9 * n.distance:
            goods.append([m])
    # cv.drawMatchesKnn expects list of lists as matches.
    # img3 = cv.drawMatchesKnn(img1, kp1, img2, kp2, good, flags=2)
    return goods

def histeq(im, nbr_bins=256):
    imhist, bins = histogram(im.flatten(), nbr_bins, density=True)
    cdf = imhist.cumsum()
    cdf = 255 * cdf / cdf[-1]
    im2 = interp(im.flatten(), bins[:-1], cdf)
    return im2.reshape(im.shape), cdf

# 图像预处理函数
def pre_process(gray):
    """

    :param gray: gray picture ndarray
    :return:
    """
    ret, thresh = cv2.threshold(gray, 165, 255, cv2.THRESH_BINARY)
    image_gf = filters.gaussian_filter(thresh, 0.25)
    image_gf_eq = cv2.equalizeHist(image_gf)
    # image_gf = np.array(image_gf, dtype='uint8')
    # w, h = image_gf.shape
    # count1 = 0
    # count2 = 0
    # for i in range(w):
    #     for j in range(h):
    #         # print(gray[i, j])
    #         if image_gf[i, j] > 205:
    #             count1 += 1
    #             image_gf[i, j] = 255
    #         else:
    #             image_gf[i, j] = 0
    #             count2 += 1
    # plt.imshow(image_gf_eq, cmap='gray')
    # plt.show()
    return image_gf_eq

def compute(image_path1, image_path2):
    """
    :param image_path1: the abspath of picture1
    :param image_path2: the abspath of picture2
    :return: matching rate of picture1 and picture2
    """
    # 图一的kp和des
    img_target = cv2.imread(image_path1)
    if isinstance(img_target, type(None)):
        img_target = plt.imread(image_path1)
    gray_target = cv2.cvtColor(img_target, cv2.COLOR_BGR2GRAY)
    result_target = pre_process(gray_target)
    kp_target, des_target = detector(result_target)
    # 图二的kp和des
    img_train = cv2.imread(image_path2)
    if isinstance(img_train, type(None)):
        img_train = plt.imread(image_path2)
    gray_train = cv2.cvtColor(img_train, cv2.COLOR_BGR2GRAY)
    result_train = pre_process(gray_train)
    kp_train, des_train = detector(result_train)

    # 调用match方法
    matches_list = match(des_target, des_train)
    # 计算匹配率
    des_amount = min(len(des_target), len(des_train))
    des_matches_amount = len(matches_list)
    rate = des_matches_amount / des_amount
    return rate, des_amount, des_matches_amount
