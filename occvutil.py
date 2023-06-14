import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

def changedSV(bgr_img, alpha, beta, color_idx):
    hsvimage = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV_FULL) # BGR->HSV
    hsvf = hsvimage.astype(np.float32)
    hsvf[:,:,color_idx] = np.clip(hsvf[:,:,1] * alpha+beta, 0, 255)
    hsv8 = hsvf.astype(np.uint8)
    return cv2.cvtColor(hsv8,cv2.COLOR_HSV2BGR_FULL)

def changedH(bgr_img, shift):
    hsvimage = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV_FULL) # BGR->HSV
    hi = hsvimage[:,:,0].astype(np.int32)
    shift = shift * 255 / 360
    if shift < 0:
        nhi = hi.flatten()
        for px in nhi:
            if px < 0:
                px = 255 - px
        nhi = nhi.reshape(hsvimage.shape[:2])
        hi = nhi.astype(np.uint8)
    chimg = (hi + shift) % 255
    hsvimage[:,:,0] = chimg
    hsv8 = hsvimage.astype(np.uint8)
    return cv2.cvtColor(hsv8,cv2.COLOR_HSV2BGR_FULL) # HSV->BGR

def changedS(bgr_img, alpha, beta):
    return changedSV(bgr_img, alpha, beta, 1)

def changedV(bgr_img, alpha, beta):
    return changedSV(bgr_img, alpha, beta, 2)

def pil2cv(imgPIL):
    imgCV_RGB = np.array(imgPIL, dtype = np.uint8)
    imgCV_BGR = np.array(imgPIL)[:, :, ::-1]
    return imgCV_BGR

def cv2pil(imgCV):
    imgCV_RGB = imgCV[:, :, ::-1]
    imgPIL = Image.fromarray(imgCV_RGB)
    return imgPIL

def cvtextdraw(img, text, org, fontFace, fontScale, color):
    x, y = org
    b, g, r = color
    colorRGB = (r, g, b)
    imgPIL = cv2pil(img)
    draw = ImageDraw.Draw(imgPIL)
    fontPIL = ImageFont.truetype(font = fontFace, size = fontScale)
    draw.text(xy = (x,y), text = text, fill = colorRGB, font = fontPIL)
    """
    後でここに追加する
    """
    imgCV = pil2cv(imgPIL)
    return imgCV