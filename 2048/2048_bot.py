from __future__ import print_function
import os
import neat
import visualize
import pygame, sys, time
from pygame.locals import *
from colours import *
from random import *
import math


tileMatrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
undoMat = []

TOTAL_POINTS = 0
DEFAULT_SCORE = 2
BOARD_SIZE = 4

pygame.init()

SURFACE = pygame.display.set_mode((400, 500), 0, 32)
pygame.display.set_caption("2048")

myfont = pygame.font.SysFont("monospace", 25)
scorefont = pygame.font.SysFont("monospace", 50)

def printMatrix():

    SURFACE.fill(BLACK)

    global BOARD_SIZE
    global TOTAL_POINTS

    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            pygame.draw.rect(SURFACE, getColour(tileMatrix[i][j]), (i*(400/BOARD_SIZE), j*(400/BOARD_SIZE) + 100, 400/BOARD_SIZE, 400/BOARD_SIZE))
            
            label = myfont.render(str(tileMatrix[i][j]), 1, (255,255,255))
            label2 = scorefont.render("Score:" + str(TOTAL_POINTS), 1, (255, 255, 255))

            SURFACE.blit(label, (i*(400/BOARD_SIZE) + 30, j*(400/BOARD_SIZE) + 130))
            SURFACE.blit(label2, (10, 20))

def printGameOver():
    global TOTAL_POINTS

    SURFACE.fill(BLACK)

    label = scorefont.render("Game Over!", 1, (255,255,255))
    label2 = scorefont.render("Score:" + str(TOTAL_POINTS), 1, (255,255,255))
    label3 = myfont.render("Press r to restart!", 1, (255,255,255))

    SURFACE.blit(label, (50, 100))
    SURFACE.blit(label2, (50, 200))
    SURFACE.blit(label3, (50, 300))

def placeRandomTile():
    count = 0
    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE):
            if tileMatrix[i][j] == 0:
                count += 1

    k = floor(random() * BOARD_SIZE * BOARD_SIZE)

    while tileMatrix[floor(k / BOARD_SIZE)][k % BOARD_SIZE] != 0:
        k = floor(random() * BOARD_SIZE * BOARD_SIZE)

    tileMatrix[floor(k / BOARD_SIZE)][k % BOARD_SIZE] = 2

def floor(n):
    return int(n - (n % 1))

def moveTiles():
    # We want to work column by column shifting up each element in turn.
    for i in range(0, BOARD_SIZE): # Work through our 4 columns.
        for j in range(0, BOARD_SIZE - 1): # Now consider shifting up each element by checking top 3 elements if 0.
            while tileMatrix[i][j] == 0 and sum(tileMatrix[i][j:]) > 0: # If any element is 0 and there is a number to shift we want to shift up elements below.
                for k in range(j, BOARD_SIZE - 1): # Move up elements below.
                    tileMatrix[i][k] = tileMatrix[i][k + 1] # Move up each element one.
                tileMatrix[i][BOARD_SIZE - 1] = 0

def mergeTiles():
    global TOTAL_POINTS

    for i in range(0, BOARD_SIZE):
        for k in range(0, BOARD_SIZE - 1):
                if tileMatrix[i][k] == tileMatrix[i][k + 1] and tileMatrix[i][k] != 0:
                    tileMatrix[i][k] = tileMatrix[i][k] * 2
                    tileMatrix[i][k + 1] = 0
                    TOTAL_POINTS += tileMatrix[i][k]
                    moveTiles()

def checkIfCanGo():
    for i in range(0, BOARD_SIZE ** 2):
        if tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE] == 0:
            return True

    for i in range(0, BOARD_SIZE):
        for j in range(0, BOARD_SIZE - 1):
            if tileMatrix[i][j] == tileMatrix[i][j + 1]:
                return True
            elif tileMatrix[j][i] == tileMatrix[j + 1][i]:
                return True
    return False

def reset():
    global TOTAL_POINTS
    global tileMatrix

    TOTAL_POINTS = 0
    SURFACE.fill(BLACK)

    tileMatrix = [[0 for i in range(0, BOARD_SIZE)] for j in range(0, BOARD_SIZE)]

def canMove():
    for i in range(0, BOARD_SIZE):
        for j in range(1, BOARD_SIZE):
            if tileMatrix[i][j-1] == 0 and tileMatrix[i][j] > 0:
                return True
            elif (tileMatrix[i][j-1] == tileMatrix[i][j]) and tileMatrix[i][j-1] != 0:
                return True

    return False

def saveGameState():
    f = open("savedata", "w")

    line1 = " ".join([str(tileMatrix[floor(x / BOARD_SIZE)][x % BOARD_SIZE]) for x in range(0, BOARD_SIZE**2)])
    
    f.write(line1 + "\n")
    f.write(str(BOARD_SIZE)  + "\n")
    f.write(str(TOTAL_POINTS))
    f.close()

def loadGameState():
    global TOTAL_POINTS
    global BOARD_SIZE
    global tileMatrix

    f = open("savedata", "r")

    mat = (f.readline()).split(' ', BOARD_SIZE ** 2)
    BOARD_SIZE = int(f.readline())
    TOTAL_POINTS = int(f.readline())

    for i in range(0, BOARD_SIZE ** 2):
        tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE] = int(mat[i])

    f.close()

    main(True)

def rotateMatrixClockwise():
    for i in range(0, int(BOARD_SIZE/2)):
        for k in range(i, BOARD_SIZE- i - 1):
            temp1 = tileMatrix[i][k]
            temp2 = tileMatrix[BOARD_SIZE - 1 - k][i]
            temp3 = tileMatrix[BOARD_SIZE - 1 - i][BOARD_SIZE - 1 - k]
            temp4 = tileMatrix[k][BOARD_SIZE - 1 - i]

            tileMatrix[BOARD_SIZE - 1 - k][i] = temp1
            tileMatrix[BOARD_SIZE - 1 - i][BOARD_SIZE - 1 - k] = temp2
            tileMatrix[k][BOARD_SIZE - 1 - i] = temp3
            tileMatrix[i][k] = temp4

def isArrow(k):
    return(k == pygame.K_UP or k == pygame.K_DOWN or k == pygame.K_LEFT or k == pygame.K_RIGHT)

def getRotations(k):
    if k == pygame.K_UP:
        return 0
    elif k == pygame.K_DOWN:
        return 2
    elif k == pygame.K_LEFT:
        return 1
    elif k == pygame.K_RIGHT:
        return 3
        
def convertToLinearMatrix():
    mat = []

    for i in range(0, BOARD_SIZE ** 2):
        if tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE]!=0:
            mat.append(math.log(tileMatrix[floor(i / BOARD_SIZE)][i % BOARD_SIZE], 2))
        else:
            mat.append(0)
    return mat

def eval_genomes(genomes, config):
    global TOTAL_POINTS
    global tileMatrix
    for genome_id, genome in genomes:
        genome.fitness = 0.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        reset()

        placeRandomTile()
        placeRandomTile()

        printMatrix()

        while checkIfCanGo():
            pygame.event.get()

            # rotations = getRotations(event.key)

            output = net.activate(convertToLinearMatrix())
            rotations = output.index(max(output))
            for i in range(0, rotations):
                rotateMatrixClockwise()

            if canMove():
                moveTiles()
                mergeTiles()
                placeRandomTile()
            else:
                break

            for j in range(0, (4 - rotations) % 4):
                rotateMatrixClockwise()

            printMatrix()

            pygame.display.update()
        genome.fitness = TOTAL_POINTS


def run(config_file):
    # Load configuration.
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(eval_genomes, 300)
    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
    visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)

pygame.display.quit()
pygame.quit()