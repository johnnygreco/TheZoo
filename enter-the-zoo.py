#!/usr/bin/env python 

import os
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


title = u'WeLcOMe tO TheZoo'
if args.review:
    title += ' (reviewing)'


if config['out_path'] is None:
    out_path = os.path.dirname(config['catalog'])
else:
    out_path = config['out_path']


root = tk.Tk()
root.withdraw()
top = tk.Toplevel(root)
top.protocol("WM_DELETE_WINDOW", root.destroy)
top.title(title)
gui = GUI(
    root=root, 
    master=top, 
    review=args.review, 
    cat_file_name=config['catalog'], 
    figure_list=config['figures'],
    out_path=out_path,
    plot_1_cols=[config['x1'], config['y1']],
    plot_2_cols=[config['x2'], config['y2']],
    radec_cols=[config['ra_col'], config['dec_col']],
    clobber=args.clobber
)

         
while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass
