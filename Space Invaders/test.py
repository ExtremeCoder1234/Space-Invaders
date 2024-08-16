import pygame

pygame.init()

WIDTH, HEIGHT = 700, 700

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
posX = WIDTH * 1 / 8
posY = HEIGHT * 1 / 8
position = posX, posY
text = "INFO"
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    font = pygame.font.SysFont("comicsans", 40)
    if text == "INFO":
        text = [
            "If you are learning to play, it is recommended",
            "you chose your own starting area.",
        ]
        label = []
        for line in text:
            label.append(font.render(line, True, (255, 255, 255)))
        for line in range(len(label)):
            WIN.blit(
                label[line],
                (position[0], position[1] + (line * 40) + (15 * line)),
            )
            pygame.display.update()
