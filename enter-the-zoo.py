#!/usr/bin/env python 

import tkinter as tk
from argparse import ArgumentParser
from udg_zoo import GUI

parser = ArgumentParser(__file__)
parser.add_argument('-r', '--review', action='store_true', 
                    help='review without classification')
parser.add_argument('-c', '--clobber', action='store_true', 
                    help='delete previous progress without warning')
parser.add_argument('--io', type=str, default=None,
                    help='input/output directory path (udg-zoo/io by default)')
args = parser.parse_args()

title = u'hugs-pipe viz inspect'
if args.review:
    title += ' (reviewing)'

root = tk.Tk()
root.withdraw()
top = tk.Toplevel(root)
top.protocol("WM_DELETE_WINDOW", root.destroy)
top.title(title)
gui = GUI(root, top, args.review, args.clobber, args.io)

while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass
