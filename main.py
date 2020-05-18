import pygame
import random
from os import path

# Estabelece a pasta que contem as figuras e sons.
img_dir = path.join(path.dirname(__file__), 'img')

# Dados gerais do jogo.
TITULO = 'Corona Run'
WIDTH = 1250 # Largura da tela
HEIGHT = 768 # Altura da tela
FPS = 60 # Frames por segundo
PLAYER_IMG = 'dino.png'
BLOCK_IMG = 'boss.png'
BACKGROUND_IMG = 'full_background.png'
CACTOS_IMG = 'cactos.png'

# Define algumas variáveis com as cores básicas
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Define a aceleração da gravidade
GRAVITY = 2
# Define a velocidade inicial no pulo
JUMP_SIZE = 30
# Define a altura do chão
GROUND = HEIGHT * 7/8

# Define estados possíveis do jogador
STILL = 0
JUMPING = 1
FALLING = 2
## CROWCH = 3
## DEATH = 4

# Define a velocidade inicial do mundo
world_speed = -10
# Define a quantidade inicial de cactos
INITIAL_CACTOS = 1

# Carrega todos os assets de uma vez.
def load_assets(img_dir):
    assets = {}
    assets[PLAYER_IMG] = pygame.image.load(path.join(img_dir, PLAYER_IMG)).convert_alpha()
    assets[BACKGROUND_IMG] = pygame.image.load(path.join(img_dir, BACKGROUND_IMG)).convert()
    assets[CACTOS_IMG] = pygame.image.load(path.join(img_dir, CACTOS_IMG)).convert()
    return assets

# Classe Jogador que representa o herói
class Player(pygame.sprite.Sprite):

    # Construtor da classe.
    def __init__(self, player_img):

        # Construtor da classe pai (Sprite).
        pygame.sprite.Sprite.__init__(self)

        # Aumenta o tamanho da imagem
        player_img = pygame.transform.scale(player_img, (100, 160))

        # Define estado atual
        # Usamos o estado para decidir se o jogador pode ou não pular
        self.state = STILL

        # Define a imagem do sprite. Nesse exemplo vamos usar uma imagem estática (não teremos animação durante o pulo)
        self.image = player_img

        # Detalhes sobre o posicionamento.
        self.rect = self.image.get_rect()

        # Começa no inicio da janela
        self.rect.centerx = WIDTH / 10
        self.rect.bottom = int(HEIGHT * 7 / 8)
        self.rect.top = 0

        self.speedy = 0

    # Metodo que atualiza a posição do personagem
    def update(self):
        self.speedy += GRAVITY
        # Atualiza o estado para caindo
        if self.speedy > 0:
            self.state = FALLING
        self.rect.y += self.speedy
        # Se bater no chão, para de cair
        if self.rect.bottom > GROUND:
            # Reposiciona para a posição do chão
            self.rect.bottom = GROUND
            # Para de cair
            self.speedy = 0
            # Atualiza o estado para parado
            self.state = STILL


    # Método que faz o personagem pular
    def jump(self):
        # Só pode pular se ainda não estiver pulando ou caindo
        if self.state == STILL:
            self.speedy -= JUMP_SIZE
            self.state = JUMPING

# Classe que reprenta os cactos
class Cactos(pygame.sprite.Sprite):
    def __init__(self, cactos_img, x, y, speedx):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        # Diminui o tamanho da imagem
        cactos_img = pygame.transform.scale(cactos_img, (70, 150))
        self.image = cactos_img
        # Detalhes sobre o posicionamento.
        self.rect = self.image.get_rect()
        # Posiciona o cacto
        self.rect.x = x
        self.rect.y = y

        self.speedx = speedx
        
    def update(self):
        self.rect.x += self.speedx

def game_screen(screen):

    # Variável para o ajuste de velocidade
    clock = pygame.time.Clock()

    # Carrega assets
    assets = load_assets(img_dir)

    # Carrega o fundo do jogo
    background = assets[BACKGROUND_IMG]
    # Redimensiona o fundo
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    background_rect = background.get_rect()

    # Cria Sprite do jogador
    player = Player(assets[PLAYER_IMG])
    # Cria um grupo de todos os sprites e adiciona o jogador.
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    
    # Cria um grupo para guardar somente os sprites do mundo (obstáculos, objetos, etc).
    # Esses sprites vão andar junto com o mundo (fundo)
    world_sprites = pygame.sprite.Group()

    # Cria cactos espalhados em posições aleatórias do mapa
    for i in range(INITIAL_CACTOS):
        cacto_x = 1160
        cacto_y = 600
        cacto = Cactos(assets[CACTOS_IMG], cacto_x, cacto_y, world_speed)
        world_sprites.add(cacto)
        # Adiciona também no grupo de todos os sprites para serem atualizados e desenhados
        all_sprites.add(cacto)

    PLAYING = 0
    DONE = 1

    state = PLAYING
    while state != DONE:

        # Ajusta a velocidade do jogo.
        clock.tick(FPS)

        # Processa os eventos (mouse, teclado, botão, etc).
        for event in pygame.event.get():
            print(event)
            # Verifica se foi fechado.
            if event.type == pygame.QUIT:
                state = DONE

            # Verifica se soltou alguma tecla.
            if event.type == pygame.KEYDOWN:
                # Dependendo da tecla, altera o estado do jogador.
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()

        # Depois de processar os eventos.
        # Atualiza a acao de cada sprite. O grupo chama o método update() de cada Sprite dentre dele.
        all_sprites.update()

        # Verifica se algum cacto saiu da janela
        for cacto in world_sprites:
            if cacto.rect.right < 0:
                # Destrói o cacto e cria um novo no final da tela
                cacto.kill()
                cacto_x = 1160
                cacto_y = 600
                new_cacto = Cactos(assets[CACTOS_IMG], cacto_x, cacto_y, world_speed)
                all_sprites.add(new_cacto)
                world_sprites.add(new_cacto)

        # A cada loop, redesenha o fundo e os sprites
        screen.fill(BLACK)

        # Atualiza a posição da imagem de fundo.
        background_rect.x += world_speed
        # Se o fundo saiu da janela, faz ele voltar para dentro.
        if background_rect.right < 0:
            background_rect.x += background_rect.width
        # Desenha o fundo e uma cópia para a direita.
        # Assumimos que a imagem selecionada ocupa pelo menos o tamanho da janela.
        # Além disso, ela deve ser cíclica, ou seja, o lado esquerdo deve ser continuação do direito.
        screen.blit(background, background_rect)
        # Desenhamos a imagem novamente, mas deslocada da largura da imagem em x.
        background_rect2 = background_rect.copy()
        background_rect2.x += background_rect2.width
        screen.blit(background, background_rect2)

        all_sprites.draw(screen)

        # Depois de desenhar tudo, inverte o display.
        pygame.display.flip()


# Inicialização do Pygame.
pygame.init()
pygame.mixer.init()

# Tamanho da tela.
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Nome do jogo
pygame.display.set_caption(TITULO)

# Comando para evitar travamentos.
try:
    game_screen(screen)
finally:
    pygame.quit()
    
