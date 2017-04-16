"""
2-input XOR example -- this is most likely the simplest possible example.
"""

from __future__ import print_function
import os
import neat
import visualize
import math
import numpy as np
import pygame
import pickle
from pygame.locals import *
from sys import exit
import random

def eval_genomes(genomes, config):
    print ('Length of genome : '+ str(len(genomes)))
    counters = 0
    for genome_id, genome in genomes:
        print('Counter = ' + str(counters))
        counters += 1
        genome.fitness = 0.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)

        pygame.init()

        screen=pygame.display.set_mode((640,480),0,32)
        pygame.display.set_caption("Pong Pong!")

        #Creating 2 bars, a ball and background.
        back = pygame.Surface((640,480))
        background = back.convert()
        background.fill((0,0,0))
        bar = pygame.Surface((10,50))
        bar1 = bar.convert()
        bar1.fill((0,0,255))
        bar2 = bar.convert()
        bar2.fill((255,0,0))
        circ_sur = pygame.Surface((15,15))
        circ = pygame.draw.circle(circ_sur,(0,255,0),(15/2,15/2),15/2)
        circle = circ_sur.convert()
        circle.set_colorkey((0,0,0))

        # some definitions
        bar1_x, bar2_x = 10. , 620.
        bar1_y, bar2_y = 215. , 215.
        circle_x, circle_y = 307.5, 232.5
        bar1_move, bar2_move = 0. , 0.
        speed_x, speed_y, speed_circ = 750., 750., 750.
        ai_speed = 0.0
        bar1_score, bar2_score = 0,0
        #clock and font objects
        clock = pygame.time.Clock()
        font = pygame.font.SysFont("calibri",40)
        timers = 0
        while (bar2_score <= bar1_score) and (bar1_score <= 4):
            pygame.event.get()
            timers += 1
            output = net.activate([circle_x, circle_y, bar1_x, bar1_y])
            if output[0] > 0:
                bar1_move = -ai_speed
            else:
                bar1_move = ai_speed

            score1 = font.render(str(bar1_score), True,(255,255,255))
            score2 = font.render(str(bar2_score), True,(255,255,255))

            screen.blit(background,(0,0))
            frame = pygame.draw.rect(screen,(255,255,255),Rect((5,5),(630,470)),2)
            middle_line = pygame.draw.aaline(screen,(255,255,255),(330,5),(330,475))
            screen.blit(bar1,(bar1_x,bar1_y))
            screen.blit(bar2,(bar2_x,bar2_y))
            screen.blit(circle,(circle_x,circle_y))
            screen.blit(score1,(250.,210.))
            screen.blit(score2,(380.,210.))

            bar1_y += bar1_move
            
        # movement of circle
            time_passed = clock.tick(30)
            time_sec = time_passed / 1000.0
            
            circle_x += speed_x * time_sec
            circle_y += speed_y * time_sec
            ai_speed = speed_circ * time_sec
        #AI of the computer.
            if circle_x >= 305.:
                if not bar2_y == circle_y + 7.5:
                    if bar2_y < circle_y + 7.5:
                        bar2_y += ai_speed
                    if  bar2_y > circle_y - 42.5:
                        bar2_y -= ai_speed
                else:
                    bar2_y == circle_y + 7.5
            
            if bar1_y >= 420.: bar1_y = 420.
            elif bar1_y <= 10. : bar1_y = 10.
            if bar2_y >= 420.: bar2_y = 420.
            elif bar2_y <= 10.: bar2_y = 10.
        #since i don't know anything about collision, ball hitting bars goes like this.
            if circle_x <= bar1_x + 10.:
                if circle_y >= bar1_y - 7.5 and circle_y <= bar1_y + 42.5:
                    circle_x = 20.
                    speed_x = -speed_x
            if circle_x >= bar2_x - 15.:
                if circle_y >= bar2_y - 7.5 and circle_y <= bar2_y + 42.5:
                    circle_x = 605.
                    speed_x = -speed_x
            if circle_x < 5.:
                bar2_score += 1
                circle_x, circle_y = 320., 232.5
                bar1_y,bar_2_y = 215., 215.
            elif circle_x > 620.:
                bar1_score += 1
                circle_x, circle_y = 307.5, 232.5
                bar1_y, bar2_y = 215., 215.
            if circle_y <= 10.:
                speed_y = -speed_y
                circle_y = 10.
            elif circle_y >= 457.5:
                speed_y = -speed_y
                circle_y = 457.5
            genome.fitness = (bar1_score - bar2_score)
            pygame.display.update()
    
    pygame.display.quit()
    pygame.quit()

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

    # Run for up to 10 generations.
    winner = p.run(eval_genomes,10)
    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    visualize.plot_stats(stats, ylog=True, view=True, filename="feedforward-fitness.svg")
    visualize.plot_species(stats, view=True, filename="feedforward-speciation.svg")

    # Display the winning genome.
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward')
    run(config_path)