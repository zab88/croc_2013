import time
import cv2
import numpy as np
import math
import pcduino_pin

SEARCH_COLOR = 255 #255- white, 0 - black.
DEBUG_DRAW = True
DEBUG_FPS = False
R_PART = 0.4
ERROR_4_SMALL_RECT = 0.1
ADD_BORDER = 31

def detectHoleColor(img_bin, point_center, rr_opt):
    #in order to avoid errors with going out of boundaries
    # if (point_center[0]-rr_opt)<0 or (point_center[1]-rr_opt)<0:
    #     return False, ''
    # if (point_center[0]+rr_opt)>img_bin.shape[1] or (point_center[1]+rr_opt)>img_bin.shape[0]:
    #     return False, ''
    #croping testing rectangle
    rect_01 = img_bin[(point_center[1]-rr_opt):(point_center[1]+rr_opt), (point_center[0]-rr_opt):(point_center[0]+rr_opt)]
    #draw for debug
    if DEBUG_DRAW:
        cv2.rectangle(frame, (point_center[0]-rr_opt, point_center[1]-rr_opt), (point_center[0]+rr_opt, point_center[1]+rr_opt), 255, 1)
    #error counting
    err = np.float32(cv2.countNonZero(rect_01))/np.float32(rect_01.shape[0]*rect_01.shape[1])
    #compare with threshold
    if err >= 1.0 - ERROR_4_SMALL_RECT:
        return True, 'WHITE'
    elif err <= ERROR_4_SMALL_RECT:
        return True, 'BLACK'
    else:
        return False, ''

def makeControl(point_cross, img_width, img_height):
    x_err = (2*point_cross[0] - img_width)
    y_err = (2*point_cross[1] - img_height)
    if 5*( math.fabs(x_err)+math.fabs(y_err)) < img_height+img_width:
        print 'centered'
        pcduino_pin.moveCommand('centered')
        return
    if math.fabs(x_err) >= math.fabs(y_err):
        if x_err>0:
            print 'right'
            pcduino_pin.moveCommand('right')
        else:
            print 'left'
            pcduino_pin.moveCommand('left')
    else:
        if y_err>0:
            print 'forward'
            pcduino_pin.moveCommand('forward')
        else:
            print 'back'
            pcduino_pin.moveCommand('back')


######################################
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

start_time = time.time()
counter = 0

while rval:
    img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.blur(img_gray, (3, 3))
    img_bin = cv2.threshold(img_blur, 127, 255, cv2.THRESH_OTSU)[1]
    #add border
    '''
    for x in range(img_bin.shape[1]):
        img_bin[0][x] = SEARCH_COLOR
        img_bin[1][x] = SEARCH_COLOR
        img_bin[img_bin.shape[0]-1][x] = SEARCH_COLOR
        img_bin[img_bin.shape[0]-2][x] = SEARCH_COLOR
    for y in range(img_bin.shape[0]):
        img_bin[y][0] = SEARCH_COLOR
        img_bin[y][1] = SEARCH_COLOR
        img_bin[y][img_bin.shape[1]-1] = SEARCH_COLOR
        img_bin[y][img_bin.shape[1]-2] = SEARCH_COLOR
    '''
    img_bin = cv2.copyMakeBorder(img_bin, ADD_BORDER, ADD_BORDER, ADD_BORDER, ADD_BORDER, cv2.BORDER_CONSTANT, img_bin, SEARCH_COLOR)
    if DEBUG_DRAW:
        frame = cv2.copyMakeBorder(frame, ADD_BORDER, ADD_BORDER, ADD_BORDER, ADD_BORDER, cv2.BORDER_CONSTANT, frame, (127, 127, 127))
    #     if img_bin[y][0] > 0:
    #     if img_bin[0][x] > 0:
    #         img_bin[0][x] = 0
    #     else:
    #         img_bin[0][x] = 255
    #     if img_bin[1][x] > 0:
    #         img_bin[1][x] = 0
    #     else:
    #         img_bin[1][x] = 255
    #
    #     if img_bin[img_bin.shape[0]-1][x] > 0:
    #         img_bin[img_bin.shape[0]-1][x] = 0
    #     else:
    #         img_bin[img_bin.shape[0]-1][x] = 255
    #
    # for y in range(img_bin.shape[0]):
    #     if img_bin[y][0] > 0:
    #         img_bin[y][0] = 0
    #     else:
    #         img_bin[y][0] = 255
    #
    #     if img_bin[y][img_bin.shape[1]-1] > 0:
    #         img_bin[y][img_bin.shape[1]-1] = 0
    #     else:
    #         img_bin[y][img_bin.shape[1]-1] = 255


    contours, hierarchy = cv2.findContours(img_bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.01*cv2.arcLength(cnt,True),True)
        approx_area = cv2.contourArea(approx)
        x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(approx)

        if approx_area > 2048 and np.float32(w_cnt)/np.float32(h_cnt)>0.7 and np.float32(w_cnt)/np.float32(h_cnt)<1.3:
            cv2.drawContours( frame, [cnt], -1, (0,0,255), 1)

            rect = cv2.minAreaRect(approx)
            #print(rect)
            if np.float32(rect[1][0])/np.float32(rect[1][1]) > 1.3 or np.float32(rect[1][0])/np.float32(rect[1][1])<0.7:
                continue

            #get color in center
            #m = cv2.moments(approx)
            #cnt_center_point = ( m['m10']/m['m00'], m['m01']/m['m00'] )
            #cnt_center = img_bin[(cnt_center_point[1]-10):(cnt_center_point[1]+10), (cnt_center_point[0]-10):(cnt_center_point[0]+10)]
            rrc = int( np.float32(rect[1][0]+rect[1][1])/np.float32(40) ) + 3
            #print(rrc)

            rect_center = img_bin[(rect[0][1]-rrc):(rect[0][1]+rrc), (rect[0][0]-rrc):(rect[0][0]+rrc)]
            if DEBUG_DRAW:
                cv2.rectangle(frame, (int(rect[0][0]-rrc), int(rect[0][1]-rrc)), (int(rect[0][0]+rrc), int(rect[0][1]+rrc)), (127, 255, 255), 2)
                #cv2.rectangle(frame, (int(cnt_center_point[0]-10), int(cnt_center_point[1]-10)), (int(cnt_center_point[0]+10), int(cnt_center_point[1]+10)), (255, 255, 127), 2)
            color_center = cv2.countNonZero(rect_center)
            #color_center = cv2.countNonZero(cnt_center)
            if color_center > int(np.float32(4*rrc*rrc)*np.float32(0.75)):
                color_not_center = 'WHITE'
            elif color_center < int(np.float32(4*rrc*rrc)*np.float32(0.25)):
                color_not_center = 'BLACK'
            else:
                color_not_center = ''
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

            #testing
            rr = np.float32(rect[1][0])*0.35
            rr_opt = int(rr*R_PART)
            rr_center_y = rr * math.cos(math.radians(90.0-rect[2]))
            rr_center_x = rr * math.sin(math.radians(90.0-rect[2]))

            point_center = ( int(rect[0][0]+rr_center_x), int(rect[0][1]+rr_center_y))
            is_hole, color_basic = detectHoleColor(img_bin, point_center, rr_opt)
            if is_hole is False or color_not_center == color_basic:
                #if is_hole is False:
                #print(color_not_center, color_basic)
                continue

            point_center = ( int(rect[0][0]-rr_center_x), int(rect[0][1]-rr_center_y))
            is_hole, color = detectHoleColor(img_bin, point_center, rr_opt)
            #if is_hole is False or color_basic != color or color_not_center == color:
            if is_hole is False or color_basic != color:
                continue

            point_center = ( int(rect[0][0]+rr_center_y), int(rect[0][1]-rr_center_x))
            is_hole, color = detectHoleColor(img_bin, point_center, rr_opt)
            #if is_hole is False or color_basic != color or color_not_center == color:
            if is_hole is False or color_basic != color:
                continue

            point_center = ( int(rect[0][0]-rr_center_y), int(rect[0][1]+rr_center_x))
            is_hole, color = detectHoleColor(img_bin, point_center, rr_opt)
            #if is_hole is False or color_basic != color or color_not_center == color:
            if is_hole is False or color_basic != color:
                continue


            if DEBUG_DRAW:
                cv2.circle(frame, (int(rect[0][0]), int(rect[0][1])), 5,(255,0,0), 10)
            makeControl((int(rect[0][0]), int(rect[0][1])), img_bin.shape[1], img_bin.shape[0])


    if DEBUG_DRAW:
        cv2.imshow("preview1", img_bin)
        cv2.imshow("preview", frame)

    if DEBUG_FPS:
        counter += 1
        print( np.float32(counter)/np.float32( time.time() - start_time ) )

    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        if DEBUG_DRAW:
            cv2.destroyAllWindows()
        break