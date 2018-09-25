# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 08:16:32 2018

@author: USER
"""

import torch
import torch.nn
import torch.optim as optim
import torchvision.transforms as Transform
from torchvision.utils import save_image

import numpy as np
import os

import datasets
import ACGAN
import utils
from argparse import ArgumentParser

hair_mapping =  ['orange', 'white', 'aqua', 'gray', 'green', 'red', 'purple', 
                 'pink', 'blue', 'black', 'brown', 'blonde']
hair_dict = {
    'orange' : 0,
    'white': 1, 
    'aqua': 2.
    'gray': 3,
    'green': 4,
    'red': 5,
    'purple': 6,
    'pink': 7,
    'blue': 8,
    'black': 9,
    'brown': 10,
    'blonde': 11
}

eye_mapping = ['black', 'orange', 'pink', 'yellow', 'aqua', 'purple', 'green', 
               'brown', 'red', 'blue']
eye_dict = {
    'black': 0,
    'orange': 1,
    'pink': 2,
    'yellow': 3,
    'aqua' : 4,
    'purple': 5,
    'green': 6,
    'brown': 7,
    'red': 8,
    'blue': 9
}


parser = ArgumentParser()
parser.add_argument('-t', '--type', help = 'Type of anime generation.', 
                    choices = ['fix_noise', 'fix_hair_eye', 'change_hair', 'change_eye'], type = str)
parser.add_argument('-d', '--model_dir', help = 'Folder where the trained model is saved',
                    default = '../models', type = str)
parser.add_argument('-h', '--hair_color', help = 'Determine the hair color of the anime characters.'.
                    default = None, choices = hair_mapping, type = str)
parser.add_argument('-e', '--eye_color', help = 'Determine the eye color of the anime characters.'.
                    default = None, choices = eye_mapping, type = str)
parser.add_argument('-s', '--sample_dir', help = 'Folder to save the generated samples.',
                    default = '../generated')
args = parser.parse_args()

def generate_by_attributes(hair_color, eye_color):
    hair_tag = torch.zeros(64, hair_classes).to(device)
    eye_tag = torch.zeros(64, eye_classes).to(device)
    hair_class = hair_dict[hair_color]
    eye_class = eye_dict[eye_color]
    for i in range(64):
        hair_tag[i][hair_class], eye_tag[i][eye_class] = 1, 1
    
    tag = torch.cat((hair_tag, eye_tag), 1)
    z = torch.randn(64, latent_dim).to(device)
    
    output = G(z, tag)
    save_image(utils.denorm(output), '../samples/{} hair {} eyes.png'.format(hair_mapping[hair_class], eye_mapping[eye_class]))

def hair_grad():
    eye = torch.zeros(eye_classes).to(device)
    eye[np.random.randint(eye_classes)] = 1
    eye.unsqueeze_(0)
    eye = torch.cat([eye for _ in range(batch_size)], dim = 0).to(device)
    
    z = torch.randn(latent_dim).unsqueeze(0).to(device)
    img_list = []
    for i in range(hair_classes):
        hair = torch.zeros(hair_classes).to(device)
        hair[i] = 1
        hair.unsqueeze_(0)
        tag = torch.cat((hair, eye), 1)
        img_list.append(G(z, tag))
        
    output = torch.cat(img_list, 0)
    print(output.shape)
    save_image(utils.denorm(output), '../{}/change_hair_color.png'.format(args.sample_dir), nrow = hair_classes)

def eye_grad():
    hair = torch.zeros(hair_classes).to(device)
    hair[np.random.randint(hair_classes)] = 1
    hair.unsqueeze_(0)
    hair = torch.cat([hair for _ in range(batch_size)], dim = 0).to(device)
    
    z = torch.randn(latent_dim).unsqueeze(0).to(device)
    img_list = []
    for i in range(eye_classes):
        eye = torch.zeros(eye_classes).to(device)
        eye[i] = 1
        eye.unsqueeze_(0)
        tag = torch.cat((hair, eye), 1)
        img_list.append(G(z, tag))
        
    output = torch.cat(img_list, 0)
    print(output.shape)
    save_image(utils.denorm(output), '../{}/change_eye_color.png'.format(args.sample_dir), nrow = eye_classes)

def fix_noise():
    z = torch.randn(latent_dim).unsqueeze(0).to(device)
    img_list = []
    for i in range(eye_classes):
        for j in range(hair_classes):
            eye = torch.zeros(eye_classes).to(device)
            hair = torch.zeros(hair_classes).to(device)
            eye[i], hair[j] = 1, 1
            eye.unsqueeze_(0)
            hair.unsqueeze_(0)
    
            tag = torch.cat((hair, eye), 1)
            img_list.append(G(z, tag))
        
    output = torch.cat(img_list, 0)
    save_image(utils.denorm(output), '../{}/fix_noise.png'.format(args.sample_dir), nrow = hair_classes)

def main():
    if not os.path.exists(args.sample_dir):
        os.mkdir(sample_dir)
    latent_dim = 100
    hair_classes = 12
    eye_classes = 10
    batch_size = 1

    device = 'cpu'
    G_path = '../{}/ACGAN_generator.ckpt'.format(args.model_dir)

    G = G = ACGAN.Generator(latent_dim = latent_dim, code_dim = hair_classes + eye_classes)
    prev_state = torch.load(G_path)
    G.load_state_dict(prev_state['model'])
    G = G.eval()

    if args.type == 'fix_hair_eye':
        generate_by_attributes(args.hair_color,  args.eye_color)
    elif args.type == 'change_eye':
        eye_grad()
    elif args.type == 'change_hair':
        hair_grad()
    else:
        fix_noise()
    


