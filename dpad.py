import pygame

pygame.init()
pygame.joystick.init()

# 确保有连接的控制器
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
else:
    print("No joystick connected!")
    pygame.quit()
    quit()

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # 处理轴事件
        elif event.type == pygame.JOYAXISMOTION:
            # 根据实际情况调整轴值的范围
            if event.axis == 0:  # 左右方向键
                if event.value < -0.5:
                    print("D-Pad Left")
                elif event.value > 0.5:
                    print("D-Pad Right")
            elif event.axis == 1:  # 上下方向键
                if event.value < -0.5:
                    print("D-Pad Up")
                elif event.value > 0.5:
                    print("D-Pad Down")

# 退出
pygame.quit()
