#!/usr/bin/env python 


import tkinter as tk
import numpy as np
from argparse import ArgumentParser
import yaml
from thezoo import GUI


parser = ArgumentParser(__file__)
parser.add_argument('-c', '--config', required=True, 
                    help='configuration file')
parser.add_argument('-r', '--review', action='store_true', 
                    help='review without classification')
parser.add_argument('--clobber', action='store_true', 
                    help='delete previous progress without warning')
args = parser.parse_args()


with open(args.config, 'r') as fn:
    config = yaml.load(fn, Loader=yaml.FullLoader)


title = u'WeLcOMe To TheZoo'
if args.review:
    title += ' (reviewing)'


root = tk.Tk()
root.withdraw()
top = tk.Toplevel(root)
top.protocol("WM_DELETE_WINDOW", root.destroy)
top.title(title)
gui = GUI(
    root=root, 
    master=top, 
    review=args.review, 
    cat_file_name=config['cat_file_name'], 
    figure_list=config['figure_list'],
    out_path=config['out_path'],
    plot_1_cols=config['plot_1_cols'],
    plot_2_cols=config['plot_2_cols'],
    radec_cols=config['radec_cols'],
    clobber=args.clobber
)

         
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass
