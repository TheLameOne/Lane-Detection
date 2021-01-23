import cv2
import numpy as np
from PIL import ImageGrab
import time
import math
from direct_key_inputs import PressKey, ReleaseKey, W, A, S, D

tl_width = 0    # top left width, i.e top left x coordinate
tl_height = 40  # top left height, i.e top left y coordinate
br_width = 640  # bottom right width, i.e bottom right x coordinate
br_height = 510  # bottom right height, i.e bottom right y coordinate


def process_img(image):
    # convert to gray
    processed_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.blur(processed_img, (3, 3))
    # edge detection
    processed_img = cv2.Canny(processed_img, 30, 90)
    # vertices which define the ROI
    vertices = np.array([[tl_width, 0.66*(br_height - tl_height)], [tl_width, br_height],
                         [br_width, br_height], [br_width, 0.66*(br_height-tl_height)],
                         [0.75*(br_width-tl_width), 0.5*(br_height-tl_height)],
                         [0.25*(br_width-tl_width), 0.5*(br_height-tl_height)]], np.int32)
    processed_img = roi(processed_img, [vertices])
    # Find and draw lines on the edge detected image
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 100, np.array([]),
                            10, 10)
    draw_lines(image, lines)
    
    return image


def roi(img, vertices):
    # blank mask
    mask = np.zeros_like(img)
    # fill the mask
    cv2.fillPoly(mask, vertices, 255)
    # now only show the area that is the mask
    masked = cv2.bitwise_and(img, mask)
    return masked
    

def draw_lines(img, lines):
    # To handle situations when no lines are detected
    if lines is not None:
        left_line_x = []
        left_line_y = []
        right_line_x = []
        right_line_y = []
        for line in lines:
            for x1, y1, x2, y2 in line:
                slope = (y2 - y1) / (x2 - x1 + 0.001)  # Calculating the slope.
                if math.fabs(slope) < 0.5:  # Only consider extreme slope
                    continue
                if slope <= 0:  # If the slope is negative, left group.
                    left_line_x.extend([x1, x2])
                    left_line_y.extend([y1, y2])
                else:  # Otherwise, right group.
                    right_line_x.extend([x1, x2])
                    right_line_y.extend([y1, y2])
        
        # Sort X values and accordingly y values
        left_line_y = [y for _, y in sorted(zip(left_line_x, left_line_y))]
        left_line_x = sorted(left_line_x)

        right_line_y = [y for _, y in sorted(zip(right_line_x, right_line_y))]
        right_line_x = sorted(right_line_x)

        # # Remove duplicate elements from X and accordingly from Y
        # # sorting makes the removal of duplicate elements easy
        # _, l_unq_idx = np.unique(left_line_x, return_index=True)
        # left_line_x = [left_line_x[i] for i in l_unq_idx]
        # left_line_y = [left_line_y[i] for i in l_unq_idx]
        #
        # _, r_unq_idx = np.unique(right_line_x, return_index=True)
        # right_line_x = [right_line_x[i] for i in r_unq_idx]
        # right_line_y = [right_line_y[i] for i in r_unq_idx]

        # Try Except used to handle cases when no lanes are detected
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
