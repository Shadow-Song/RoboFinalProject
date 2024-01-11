import cv2
import pyzbar.pyzbar as pyzbar
import log

class Camera:
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 获取视频的宽度
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 获取视频的高度
    image_index = 0

    frame = None
    capture_flag = False

    new_code = ''
    code_list = ['']
    width = 0
    height = 0
    result = None
    w1 = 300
    h1 = 300

    logger: log.Logger = None

    def __init__(self, logger):
        self.logger = logger

    def is_open(self):
        return self.cap.isOpened()
    
    def get_frame(self):
        _, self.frame = self.cap.read()
        return self.frame
    
    def get_size(self):
        return self.width, self.height
    
    def run(self):
        _, self.frame = self.cap.read()
        if self.capture_flag:
            cv2.imwrite(f'./img/photo{self.image_index}.jpg', self.frame)
            print(f'照片{self.image_index}已保存')
            self.logger.write(f'照片{self.image_index}已保存', 0)
            self.image_index += 1
        self.capture_flag = False
        
    def capture(self):
        self.capture_flag = True

    def capture_QR(self):
        i = 0
        width, height = self.get_size()
        self.x1 = int(width / 2 - self.w1 / 2)
        self.y1 = int(height / 2 - self.h1 / 2)
        if not self.is_open():
            print('Camera not detected.')
            return
        while True:
            ret, img = self.cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            self.show_code_string(gray=gray, image=img)

            if not self.append_code(new_code=self.new_code):
                self.driver.t_stop(2)

                cv2.imwrite(f'./QR_img/img{i}.jpg', img)
                print(f'Image {i} saved.')
                self.logger.write(f'Image {i} saved.', 0)
                self.code_list.append(self.new_code)
                i += 1

            key = cv2.waitKey(5)
            if key == 27:
                break

    def show_code_string(self, gray, image):
        code_strings = pyzbar.decode(gray)
        for code_string in code_strings:
            (x, y, w, h) = code_string.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            if x >= self.x1 and y >= self.y1 and x + w <= self.x1 + self.w1 and y + h <= self.y1 + self.h1:
                self.result = True
            else:
                self.result = False

            self.new_code = code_string.data.decode('utf-8')
            code_type = code_string.type
            print(f'[INFO] Found {code_type} barcode: {self.new_code}')
            self.logger.write(f'[INFO] Found {code_type} barcode: {self.new_code}', 0)

    def append_code(self, new_code):
        return new_code in self.code_list
