'''
Arquivo que possui todas as classes com os sprites
que será utilizado pelo pygame
'''

import random
import pygame
from parameters import *
from assets import *
from functions import *
from game_loop import *

# Class que representa os blocos do cenário
class Tile(pygame.sprite.Sprite):

    # Construtor da classe.
    def __init__(self, assets, x, y, speedx):
        
        # Construtor da classe pai (Sprite).
        pygame.sprite.Sprite.__init__(self)

        # Aumenta o tamanho do tile.
        block_img = pygame.transform.scale(assets[BLOCK_IMG], (TILE_SIZE*3, TILE_SIZE))

        # Define a imagem do tile.
        self.image = block_img
        
        # Detalhes sobre o posicionamento.
        self.rect = self.image.get_rect()

        # Posiciona o tile
        self.rect.x = x
        self.rect.y = y
        self.speedx = speedx

    def update(self):
        self.rect.x += self.speedx

# Classe Bullet que representa os tiros
class Bullet(pygame.sprite.Sprite):
    
    # Construtor da classe.
    def __init__(self, assets, right, centery):
        
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        # Diminui o tamanho do tiro.
        bullet_img = pygame.transform.scale(assets[BULLET_IMG], (BULLET_SIZE, BULLET_SIZE))
        self.image = bullet_img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.centery = centery
        self.rect.right = right
        self.speedx = 10  # Velocidade fixa para direita

    def update(self):
        
        # A bala só se move no eixo x
        self.rect.x += self.speedx

        # Se o tiro passar do inicio da tela, morre.
        if self.rect.right < 0:
            self.kill()

# Classe Jogador que representa o herói
class Player(pygame.sprite.Sprite):

    # Construtor da classe.
    def __init__(self, assets, groups, config):

        # Construtor da classe pai (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.groups = groups
        self.assets = assets

        # Aumenta o tamanho da imagem
        player_img = pygame.transform.scale(config[0], (config[1], config[2]))

        # Guarda os grupos de sprites para tratar as colisões
        self.blocks = groups['all_blocks']

        self.image = player_img

        # Define estado atual
        # Usamos o estado para decidir se o jogador pode ou não pular
        self.state = STILL

         # Define sequências de sprites de cada animação
        self.dino = config[3]
        if self.dino == True:
            spritesheet = load_spritesheet(player_img, 1, 5)
            self.animations = {
                STILL: spritesheet[2:4],
                JUMPING: spritesheet[2:3],
                MEGA_JUMP_1: spritesheet[2:3],
                MEGA_JUMP_2: spritesheet[2:3],
                FALLING: spritesheet[3:4],
            }
            # Define animação atual
            self.animation = self.animations[self.state]
            
            # Inicializa o primeiro quadro da animação
            self.frame = 0
            self.image = self.animation[self.frame]

            # Controle de ticks de animação: troca de imagem a cada self.frame_ticks milissegundos.
            self.frame_ticks = 75

        # Detalhes sobre o posicionamento.
        self.rect = self.image.get_rect()

        # Começa o jogador no chao
        self.rect.centerx = config[4]
        self.rect.bottom = int(config[5])
        self.rect.top = 0
        self.speedy = 0
        
        # Guarda o tick da primeira imagem
        self.last_update = pygame.time.get_ticks()

        # Só será possível atirar uma vez a cada 400 milissegundos
        self.last_shot = pygame.time.get_ticks()
        self.shoot_ticks = 400

        # Variável que contem a altura maxima do jogador antes de cair
        self.highest_y = self.rect.bottom

        # Contador de pulos
        self.jumps = 0

        # Estabelece vida
        self.health = 100

        self.mask = pygame.mask.from_surface(self.image)

    # Metodo que atualiza a posição do personagem
    def update(self):
        self.speedy += GRAVITY

        # Atualiza o estado para caindo
        if self.speedy > 0:
            self.state = FALLING
        self.rect.y += self.speedy

        # Se bater no chão, para de cair
        if self.rect.bottom > GROUND:
            # Reinicia o contador de pulo
            self.jumps = 0
            # Reposiciona para a posição do chão
            self.rect.bottom = GROUND
            # Para de cair
            self.speedy = 0
            # Atualiza o estado para parado
            self.state = STILL

        # Atualiza a altura no mapa
        if self.state != FALLING:
            self.highest_y = self.rect.bottom
            
        # Verifica se colidiu com o bloco caso o jogador esteja caindo
        if self.speedy > 0:  # Está indo para baixo
            collisions = pygame.sprite.spritecollide(self, self.blocks, False)

            # Verifica para cada bloco colidido se foi atingido a parte de cima
            for block in collisions:
                if self.highest_y <= block.rect.top:
                    self.rect.bottom = block.rect.top
                    
                    # Atualiza a altura no mapa
                    self.highest_y = self.rect.bottom
                    
                    # Para de cair
                    self.speedy = 0
                    
                    # Atualiza o estado para parado
                    self.state = STILL

                    # Reinicia o contador de pulo
                    self.jumps = 0

        # Update de movimentacao 
        # Verifica o tick atual.
        now = pygame.time.get_ticks()

        if self.dino == True:
            # Verifica quantos ticks se passaram desde a ultima mudança de frame.
            elapsed_ticks = now - self.last_update

            # Se já está na hora de  mudar de imagem...
            if elapsed_ticks > self.frame_ticks:

                # Marca o tick da nova imagem.
                self.last_update = now

                # Avança um quadro.
                self.frame += 1

                # Atualiza animação atual
                self.animation = self.animations[self.state]

                # Reinicia a animação caso o índice da imagem atual seja inválido
                if self.frame >= len(self.animation):
                    self.frame = 0

                # Armazena a posição do centro da imagem
                center = self.rect.center
                # Atualiza imagem atual
                self.image = self.animation[self.frame]
                # Atualiza os detalhes de posicionamento
                self.rect = self.image.get_rect()
                self.rect.center = center

    # Método que faz o personagem pular
    def jump(self):
        if self.jumps < 2:
            
            # Só pode pular se ainda não estiver pulando ou caindo
            if self.state == STILL:
                self.speedy -= JUMP
                self.jumps += 1
                self.state = JUMPING
           
            # Tipos de MEGA JUMP;
            elif self.state == JUMPING: 
                self.speedy -= JUMP
                self.jumps += 1
                self.state = MEGA_JUMP_1 
            elif self.state == FALLING:
                self.speedy -= JUMP
                self.jumps += 1
                self.state = MEGA_JUMP_2
        else:
            self.jumps += 0

    # Função que representa a vida do jogador
    def life(self, screen):
        pygame.draw.rect(screen, (255,0,0), (self.rect.x, self.rect.y - 60, 100,10))
        if self.health >= 0:
            pygame.draw.rect(screen, (0,255,0), (self.rect.x, self.rect.y - 60, 100 - (100 - self.health),10))

    # Função que representa os tiros
    def shoot(self):
        
        # Verifica se pode atirar
        now = pygame.time.get_ticks()
        
        # Verifica quantos ticks se passaram desde o último tiro.
        elapsed_ticks = now - self.last_shot

        # Se já pode atirar novamente...
        if elapsed_ticks > self.shoot_ticks:
            # Marca o tick da nova imagem.
            self.last_shot = now
            
            # O novo tiro vai ser criada logo a direita e no centro vertical do jogador
            new_bullet = Bullet(self.assets, self.rect.right, self.rect.centery)
            self.groups['all_sprites'].add(new_bullet)
            self.groups['all_bullets'].add(new_bullet)

# Classe que representa o boss
class Boss(pygame.sprite.Sprite):
    def __init__(self, groups, assets):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        boss_img = pygame.transform.scale(assets[BOSS_IMG], (BOSS_SIZE, BOSS_SIZE))
        self.image = boss_img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH - 100
        self.rect.bottom = HEIGHT - 360
        self.speedy = 0
        self.groups = groups
        self.assets = assets

        # Só será possível atirar uma vez a cada 500 milissegundos
        self.last_shot = pygame.time.get_ticks()
        self.shoot_ticks = 2000

        # Ele não pode mudar de velocidade a todo frame
        self.last_speed = pygame.time.get_ticks()
        self.speed_tick = 500

        # Estabelece vida
        self.health = 200

    def update(self):
        
        # Verifica se pode mudar a speed
        time = pygame.time.get_ticks()
        elapsed_ticks = time - self.last_speed

        # Se já pode disparar novamente...
        if elapsed_ticks > self.speed_tick:
            # Marca o tick da nova imagem.
            self.last_speed = time
            self.speedy = random.choice([-5,5])
            
        # Atualização da posição do boss, manter comentado a linha abaixo para ficar estático
        self.rect.y += self.speedy

        # Mantém dentro da tela
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.top <= 100:
            self.rect.top = 101
            self.rect.y += self.speedy

        if self.rect.bottom >= HEIGHT - 100:
            self.rect.bottom = HEIGHT - 100
            self.rect.y -= self.speedy

    def puke(self):

        # Verifica se pode disparar
        now = pygame.time.get_ticks()
        # Verifica quantos ticks se passaram desde o último disparo.
        elapsed_ticks = now - self.last_shot

        # Se já pode disparar novamente...
        if elapsed_ticks > self.shoot_ticks:

            # Marca o tick da nova imagem.
            self.last_shot = now
            
            # O novo puke vai ser criada logo a esquerda e no centro vertical do boss
            new_puke = Puke(self.assets, self.rect.left, self.rect.centery)
            self.groups['all_sprites'].add(new_puke)
            self.groups['all_puke'].add(new_puke)

    def life(self, screen):
        pygame.draw.rect(screen, (255,0,0), (self.rect.x , self.rect.y - 60, 200,10))
        if self.health >= 0:
            pygame.draw.rect(screen, (0,255,0), (self.rect.x, self.rect.y - 60, 200 - (200 - self.health),10))

# Classe Puke que representa os disparos do boss
class Puke(pygame.sprite.Sprite):
    
    # Construtor da classe.
    def __init__(self, assets, left, centery):
        
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        puke_img = pygame.transform.scale(assets[PUKE_IMG], (70, 100))
        self.image = puke_img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.centery = centery
        self.rect.left = left
        self.speedx = -10  # Velocidade fixa para esquerda
        self.speedy = random.randint(0,5) # Velocidade aleatória para baixo

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        
        # Se o puke passar do inicio da tela, morre.
        if self.rect.bottom < 0:
            self.kill()

# Classe que reprenta os cactos
class Cactos(pygame.sprite.Sprite):
    def __init__(self, assets, x, y, speedx):
        
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)
        
        # Diminui o tamanho da imagem
        cactos_img = pygame.transform.scale(assets[CACTOS_IMG], (70, 100))
        self.image = cactos_img
        
        # Detalhes sobre o posicionamento.
        self.rect = self.image.get_rect()
        
        # Posiciona o cacto
        self.rect.x = x
        self.rect.y = y
        self.speedx = speedx
        
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.speedx