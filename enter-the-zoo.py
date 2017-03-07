#!/usr/bin/env python 

import tkinter as tk
from argparse import ArgumentParser
from udg_zoo import GUI

parser = ArgumentParser('view candidates')
parser.add_argument('-r', '--review', type=str, default=None)
parser.add_argument('-s', '--subset', type=str, 
                    help='subset file name', default=None)
args = parser.parse_args()

title = u'hugs-pipe viz inspect'
if args.review:
    title += ' (reviewing '+args.review+')'

root = tk.Tk()
root.withdraw()
top = tk.Toplevel(root)
top.protocol("WM_DELETE_WINDOW", root.destroy)
top.title(title)
gui = GUI(root, top, args.review, args.subset)

while True:
    try:
        root.mainloop()
        break
    except UnicodeDecodeError:
        pass
