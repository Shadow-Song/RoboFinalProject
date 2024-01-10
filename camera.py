import cv2

class Camera:

    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取视频的宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取视频的高度

    def is_open(self):
        return self.cap.isOpened()
    
    def get_frame(self):
        return self.cap.read()
    
    def get_size(self):
        return self.width, self.height

