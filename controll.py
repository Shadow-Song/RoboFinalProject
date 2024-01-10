import pygame

def init_joystick():
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No joystick/gamepad found!")
        return None
    else:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"Initialized joystick: {joystick.get_name()}")
        return joystick

def main():
    joystick = init_joystick()
    if joystick is None:
        return

    running = True
    while running:
        for event in pygame.event.get():
            print(event)
            '''
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.JOYBUTTONDOWN:
                print(f"Button {event.button} pressed")

            if event.type == pygame.JOYBUTTONUP:
                print(f"Button {event.button} released")

            #if event.type == pygame.JOYAXISMOTION:
                #print(f"Axis {event.axis} moved to {event.value}")
            '''

    pygame.quit()

if __name__ == "__main__":
    main()
