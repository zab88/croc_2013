import cv2
import numpy as np
import pcduino_pin
import math

SEARCH_COLOR = 255 #255 - white cross, 0 - black cross
DEBUG_DRAW = False
ADD_BORDER = 30

def findDistances(cnt):
    dst = []
    cnt_ll = len(cnt)-1

    # print cnt
    cntt = np.append(cnt, [cnt[0]], axis=0)
    # cnt[cnt_ll+1] = cnt[0]
    # print cnt
    # exit()

    for index, point in enumerate(cntt):
        if index <= cnt_ll:
            point = point[0]
            dd = (point[0]- cntt[index+1][0][0])*(point[0]- cntt[index+1][0][0])
            dd += (point[1]- cntt[index+1][0][1])*(point[1]- cntt[index+1][0][1])
            dst.append( dd )
    return dst

def get4corners(cnt, dst):
    cnt_ll = len(cnt)-1
    cnt = np.append(cnt, [cnt[0]], axis=0)
    dst.sort()
    dst.reverse()
    indexes = []
    merge_indexes = []
    mmm_tmp = []
    new_points = []

    for index, point in enumerate(cnt):
        if index <= cnt_ll:
            point = point[0]
            dd = (point[0]- cnt[index+1][0][0])*(point[0]- cnt[index+1][0][0])
            dd += (point[1]- cnt[index+1][0][1])*(point[1]- cnt[index+1][0][1])
            #print dd
            if dd == dst[0] or dd == dst[1] or dd == dst[2] or dd == dst[3]:
                indexes.append(index)
                if index+1>cnt_ll:
                    indexes.append(0)
                else:
                    indexes.append(index+1)
                # indexes.append(point)
                # indexes.append(cnt[index+1][0])
                if mmm_tmp.count(index) < 1:
                    new_points.append([point[0], point[1]])
            else:
                new_x = int( np.float32(cnt[index][0][0]+cnt[index+1][0][0])/2.0 )
                new_y = int( np.float32(cnt[index][0][1]+cnt[index+1][0][1])/2.0 )
                new_points.append([new_x, new_y])
                mmm_tmp.append(index)
                mmm_tmp.append(index+1)
                if index+1>cnt_ll:
                    merge_indexes.append([index, 0])
                else:
                    merge_indexes.append([index, index+1])


    return new_points

def checkCross(img_bin, cnt, points):
    x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(cnt)
    #initial percentage
    blob = img_bin[y_cnt:(y_cnt+h_cnt), x_cnt:(x_cnt+w_cnt)]

    area = w_cnt*h_cnt
    colored = cv2.countNonZero(blob)
    if SEARCH_COLOR > 0:
        percentage = (np.float32(area)-np.float32(colored))/np.float32(area)
    else:
        percentage = (np.float32(colored))/np.float32(area)
    if percentage > 0.35:
        return False

    line_width = int(np.float32(w_cnt+h_cnt)/40.0)+1
    cv2.line(img_bin, (points[0][0], points[0][1]), (points[2][0], points[2][1]), SEARCH_COLOR, line_width)
    cv2.line(img_bin, (points[1][0], points[1][1]), (points[3][0], points[3][1]), SEARCH_COLOR, line_width)
    blob = img_bin[y_cnt:(y_cnt+h_cnt), x_cnt:(x_cnt+w_cnt)]
    coloredNew = cv2.countNonZero(blob)
    if SEARCH_COLOR > 0:
        percentageNew = (np.float32(area)-np.float32(coloredNew))/np.float32(area)
    else:
        percentageNew = (np.float32(coloredNew))/np.float32(area)
    if percentageNew > 0.2:
        return False
    else:
        return True


def perp( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return
def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    return (num / denom)*db + b1

def lineIntersection(points):
    p1 = np.array( [points[0][0], points[0][1]] )
    p2 = np.array( [points[2][0], points[2][1]] )

    p3 = np.array( [points[1][0], points[1][1]] )
    p4 = np.array( [points[3][0], points[3][1]] )

    res = seg_intersect( p1,p2, p3,p4)
    return res

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


vc = cv2.VideoCapture(0)
if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    #frame = cv2.imread('test06.png')
    #frame = cv2.imread('bug/2013-07-17-124756_800x600_scrot.png')
    obj_detected = False
    img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.blur(img_gray, (3, 3))
    img_bin = cv2.threshold(img_blur, 127, 255, cv2.THRESH_OTSU)[1]

    #Adding border
    img_bin = cv2.copyMakeBorder(img_bin, ADD_BORDER, ADD_BORDER, ADD_BORDER, ADD_BORDER, cv2.BORDER_CONSTANT, img_bin, SEARCH_COLOR)
    if DEBUG_DRAW:
        frame = cv2.copyMakeBorder(frame, ADD_BORDER, ADD_BORDER, ADD_BORDER, ADD_BORDER, cv2.BORDER_CONSTANT, frame, (127, 127, 127))


    contours, hierarchy = cv2.findContours(img_bin.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02*cv2.arcLength(cnt,True),True)
        approx_area = cv2.contourArea(approx)
        x_cnt, y_cnt, w_cnt, h_cnt = cv2.boundingRect(approx)

        ##can check for convex
        ##cv2.isContourConvex(cnt)

        #do not consider bad contours
        if w_cnt > img_bin.shape[1]-ADD_BORDER:
            continue
        if approx_area > 2048 and np.float32(w_cnt)/np.float32(h_cnt)>0.6 and np.float32(w_cnt)/np.float32(h_cnt)<1.8:
            hull = cv2.convexHull(approx)
            cv2.drawContours( frame, [cnt], -1, (0,0,255), 1)
            cv2.drawContours( frame, [hull], -1, (255,0,0), 1)
            hull_len = len(hull)
            if hull_len < 4 or hull_len > 8:
                continue
            distances = findDistances(hull)
            distances.sort()
            distances.reverse()
            #print(distances)
            rr = get4corners(hull, distances)
            #print(rr)
            #exit()
            cv2.line(frame, (rr[0][0], rr[0][1]), (rr[2][0], rr[2][1]), (50, 255, 50), 3)
            cv2.line(frame, (rr[1][0], rr[1][1]), (rr[3][0], rr[3][1]), (50, 255, 50), 3)
            obj_detected = checkCross(img_bin.copy(), approx, rr)

            if obj_detected:
                #point_center = lineIntersection(rr)
                #print point_center
                p_x = int(np.float32(rr[0][0]+rr[1][0]+rr[2][0]+rr[3][0])/4.0)
                p_y = int(np.float32(rr[0][1]+rr[1][1]+rr[2][1]+rr[3][1])/4.0)

                #cv2.circle(frame, (point_center[0], point_center[1]), 5, (0, 0, 255), 10)
                if DEBUG_DRAW:
                    cv2.circle(frame, (p_x, p_y), 5, (0, 0, 255), 10)
                makeControl([p_x, p_y], img_bin.shape[1], img_bin.shape[0])
                break




    if obj_detected is False:
        pcduino_pin.moveCommand('none')
        print('none')

    if DEBUG_DRAW:
        cv2.imshow("preview1", img_bin)
        cv2.imshow("preview", frame)

    rval, frame = vc.read()
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        if DEBUG_DRAW:
            cv2.destroyAllWindows()
        break