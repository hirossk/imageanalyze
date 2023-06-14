import cv2
import time
import os
import numpy as np

def main():
    capture = cv2.VideoCapture(0)

    oldcircles = None
    x = None

    counter = 0
    while(True):
        ret, frame = capture.read()
        window = (1000, 800)
        cimg = cv2.resize(frame,window)
        cimg = cv2.medianBlur(cimg,5)
        gray = cv2.cvtColor(cimg, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT, 
            dp=1.0, minDist=150, param1=50, param2=65)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0,:]:
                if oldcircles is not None:
                    for j in oldcircles[0,:]:
                        #近しい円のみ描画する（誤判定防止）
                        if np.abs(i[0] - j [0]) < 50 and np.abs(i[1] - j [1]) < 50:
                            x,y,r = i[0],i[1],i[2]
                            counter = 0

            oldcircles = circles

        if counter > 5:
            x = None
            counter = 5

        if x is not None:
            cv2.circle(cimg,(x, y), r,(0,255,0),2)

        cv2.imshow('detected circles',cimg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        counter = counter + 1

    capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()