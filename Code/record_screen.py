from cv2 import cv2
import numpy as np
from PIL import ImageGrab
import time
import math
from direct_key_inputs import PressKey, ReleaseKey, W, A, S, D

tl_width = 0    # top left width # 100
tl_height = 40  # top left height # 240
br_width = 640  # bottom right width # 1280
br_height = 510  # bottom right height #800


def process_img(image):
    # convert to gray
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.blur(processed_img, (3, 3))
    # edge detection
    processed_img = cv2.Canny(processed_img, 30, 90)

    vertices = np.array([[tl_width, 0.66*(br_height - tl_height)], [tl_width, br_height],
                         [br_width, br_height], [br_width, 0.66*(br_height-tl_height)],
                         [0.75*(br_width-tl_width), 0.5*(br_height-tl_height)],
                         [0.25*(br_width-tl_width), 0.5*(br_height-tl_height)]], np.int32)
    processed_img = roi(processed_img, [vertices])

    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 100, np.array([]),
                            10, 10)
    draw_lines(image, lines)

    return image


def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    #masked areas
    masked = cv2.bitwise_and(img, mask)
    return masked
    

def draw_lines(img, lines):
    #when no lines are detected
    if lines is not None:
        left_line_x = []
        left_line_y = []
        right_line_x = []
        right_line_y = []
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = (y2 - y1) / (x2 - x1 + 0.001)  
                if math.fabs(slope) < 0.5:  
                    continue
                if slope <= 0: 
                    left_line_x.extend([x1, x2])
                    left_line_y.extend([y1, y2])
                else:  
                    right_line_x.extend([x1, x2])
                    right_line_y.extend([y1, y2])
        
        # Sort X and Y values
        left_line_y = [y for _, y in sorted(zip(left_line_x, left_line_y))]
        left_line_x = sorted(left_line_x)

        right_line_y = [y for _, y in sorted(zip(right_line_x, right_line_y))]
        right_line_x = sorted(right_line_x)

        # when no lanes are detected
        try:
            cv2.line(img, (left_line_x[0], left_line_y[0]), (left_line_x[-1], left_line_y[-1]),
                     [255, 0, 0], 3)
        except Exception:
            pass
        try:
            cv2.line(img, (right_line_x[0], right_line_y[0]), (right_line_x[-1], right_line_y[-1]),
                     [255, 0, 0], 3)
        except Exception:
            pass


def main():
    # This gives us time to set things up
    for i in list(range(4))[::-1]:
        print(i+1)
        time.sleep(1)
    
    last_time = time.time()
    while True:
        # Grab image from screen
        screen = np.array(ImageGrab.grab(bbox=(tl_width, tl_height,
                                               br_width, br_height)))
        print("Loop time : {}".format(time.time() - last_time))
        last_time = time.time()
        new_screen = process_img(screen)
        new_screen = cv2.cvtColor(new_screen, cv2.COLOR_RGB2BGR)
        cv2.imshow('Window', new_screen)

        # Exit if pressed 'q'
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    main()
