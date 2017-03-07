from __future__ import division, print_function

import os, sys
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from functools import partial
import webbrowser

import numpy as np
import matplotlib 
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
#matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .utils import hsc_map_url
filedir = os.path.dirname(__file__)
maindir = os.path.dirname(filedir)

cat_fn = 'cats/candy.csv'
out_fn = 'results/viz-'+cat_fn.split('/')[-1]
cat_fn = os.path.join(maindir, cat_fn)
out_fn = os.path.join(maindir, out_fn)

__all__ = ['maindir', 'GUI']

class GUI(object):

    def __init__(self, root, master, review, subset_fn=None):

        # initialize attributes
        self.root = root
        self.master = master
        self.save_delta_t = 5 # minutes
        self.current_idx = 0
        self.rgb_kw = dict(Q=8, dataRange=0.3)
        self.is_new_idx = True
        self.ell_visible = False
        self.flags = ['candy', 'junk', 'tidal', 'ambiguous']
        self._coord = None
        self.master.withdraw()
        self.review = review
        self.subset_fn = subset_fn
        self.out_fn = out_fn 
        if subset_fn is not None:
            self.out_fn = self.out_fn[:-4]+'-'+subset_fn

        # if output catalog exists, check if we want to reload progress
        if os.path.isfile(self.out_fn):
            if review:
                self.cat = pd.read_csv(self.out_fn)
                if review != 'all':
                    self.cat = self.cat[self.cat[review]==1]
                    self.cat_idx = self.cat.index
                    self.cat.reset_index(inplace=True)

            else:
                msg = 'Catalog exists. Want to start where you left off?'
                answer = messagebox.askyesno('HSC-HUGs Message', msg)
                                        
                if answer:
                    self.cat = pd.read_csv(self.out_fn)
                    flagged = self.cat['candy']==-1
                    if flagged.sum()==0:
                        msg = 'All sources have been classified.'
                        messagebox.showinfo('HSC-HUGs Message', msg)
                        sys.exit('Exiting without changing anything...')
                    self.current_idx = self.cat[flagged].index[0]
                else:
                    verify = messagebox.askyesno(
                        'Verify', 'Progress will be lost, okay?', default='no')
                    if verify:
                        self._load_cat(cat_fn)
                    else:
                        self.root.destroy()
                        sys.exit('Exiting without changing anything...')
        else:
            self._load_cat(cat_fn)

        top_fr = tk.Frame(self.master)
        mid_fr = tk.Frame(self.master)
        bot_fr = tk.Frame(self.master)
        
        # status info
        self.status = tk.Text(
            self.master, height=1, relief='sunken', bg=self.master.cget('bg'))
        self.status.pack(side='bottom', fill='x', anchor='w')

        top_fr.pack(side='top', expand=0)
        bot_fr.pack(side='bottom', expand=0, pady=10)
        mid_fr.pack(side='bottom', expand=0)

        self.fig = Figure(figsize=(6, 6))
        self.ax = self.fig.add_subplot(111)

        # create bottom buttons
        tk.Label(bot_fr, text='Source Index').grid(
            row=0, column=0, sticky='w')
        self.idx_evar= tk.IntVar()
        self.idx_evar.set(self.current_idx)
        idx_entry = tk.Entry(bot_fr, textvariable=self.idx_evar, takefocus=0)
        idx_entry.grid(row=0, column=1, sticky='w', padx=8)
        idx_entry.bind('<Return>', self.set_idx)

        prev_button = tk.Button(
            bot_fr, text='Previous', command=self.prev_idx)
        prev_button.grid(row=0, column=4, padx=12, sticky='w', columnspan=5)

        next_button = tk.Button(
            bot_fr, text='Next', command=self.next_idx)
        next_button.grid(row=0, column=9, sticky='w', columnspan=5)

        padx = 15
        if not review:
            # create middle buttons
            up_flag = partial(self.set_flag, 'candy')
            fn = os.path.join(filedir, 'buttons/up.gif')
            sig_img = tk.PhotoImage(file=fn)
            signal_button = tk.Button(
                mid_fr, image=sig_img, width='100', 
                height='100', command=up_flag) 
            signal_button.image = sig_img
            signal_button.grid(row=0, column=0, sticky='w', padx=padx)

            down_flag = partial(self.set_flag, 'junk')
            fn = os.path.join(filedir, 'buttons/down.gif')
            noise_img = tk.PhotoImage(file=fn)
            noise_button = tk.Button(
                mid_fr, image=noise_img, width='100', 
                height='100', command=down_flag)
            noise_button.image = noise_img
            noise_button.grid(row=0, column=1, sticky='w', padx=padx)

            tidal_flag = partial(self.set_flag, 'tidal')
            fn = os.path.join(filedir, 'buttons/tidal.gif')
            tidal_img = tk.PhotoImage(file=fn)
            tidal_button = tk.Button(
                mid_fr, image=tidal_img, width='100', 
                height='100', command=tidal_flag)
            tidal_button.image = tidal_img 
            tidal_button.grid(row=0, column=2, sticky='w', padx=padx)

            question_flag = partial(self.set_flag, 'ambiguous')
            fn = os.path.join(filedir, 'buttons/question-mark.gif')
            question_img = tk.PhotoImage(file=fn)
            question_button = tk.Button(
                mid_fr, image=question_img, width='100', 
                height='100', command=question_flag)
            question_button.image = question_img 
            question_button.grid(row=0, column=3, sticky='w', padx=padx)

            save_button = tk.Button(
                top_fr, text='Save Progess', command=self.save_progress)
            save_button.pack(side='left', padx=padx)

            # useful key bindings
            self.master.bind('s', self.save_progress)
            self.master.bind('1', up_flag)
            self.master.bind('2', down_flag)
            self.master.bind('3', tidal_flag)
            self.master.bind('4', question_flag)

        # create top buttons
        hmap_button = tk.Button(
            top_fr, text='hscMap', command=self.hsc_map)
        hmap_button.pack(side='left', padx=padx)

        quit_button = tk.Button(top_fr, text='Quit', command=self.quit)
        quit_button.pack(side='left', padx=padx)

        # useful key bindings
        self.master.bind('<Down>', self.prev_idx)
        self.master.bind('<Up>', self.next_idx)
        self.master.bind_all('<1>', lambda event: event.widget.focus_set())

        # build canvas
        self.fig.set_tight_layout(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.display_image()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.master.deiconify()

        # save progress every save_delta_t minutes
        if not review:
            self.root.after(self.save_delta_t*60*1000, self.save_progress)

    def _load_cat(self, cat_fn):
        self.cat = pd.read_csv(cat_fn)
        if self.subset_fn is not None:
            mask = np.loadtxt(self.subset_fn, dtype=bool)
            self.cat = self.cat.loc[mask].copy()

        self.cat['candy'] = -1
        self.cat['junk'] = -1
        self.cat['tidal'] = -1
        self.cat['ambiguous'] = -1

    def next_idx(self, event=None):
        self.current_idx += 1
        if self.current_idx > (len(self.cat)-1):
            msg = 'Congrats, visual inspection complete!'
            w = tk.Tk()
            w.withdraw()
            messagebox.showinfo('HSC-HUGs Message', msg, parent=w)
            w.destroy()
            self.quit()
        else:
            self.is_new_idx = True
            self.idx_evar.set(self.current_idx)
            self.display_image()

    def prev_idx(self, event=None):
        if self.current_idx >0:
            self.current_idx -= 1
            self.is_new_idx = True
            self.idx_evar.set(self.current_idx)
            self.display_image()

    def set_idx(self, event=None):
        self.current_idx = self.idx_evar.get()
        self.is_new_idx = True
        self.display_image()

    def hsc_map(self):
        ra, dec = self.cat.loc[self.current_idx, ['ra', 'dec']]
        webbrowser.open(hsc_map_url(ra, dec), new=1)

    def display_image(self):
        self.update_info()
        self.ax.cla()
        self.ax.set(xticks=[], yticks=[])
        fn = 'images/candy-{}.png'.format(self.current_idx)
        image = mpimg.imread(os.path.join(filedir, fn))
        self.ax.imshow(image)
        self.canvas.draw()

    def update_info(self):
        txt = 'r: {:.2f} arcsec - mu_0(g): {:.2f} - flag: {}'
        cols = ['r_e(g)', 'mu_0(g)']
        flag_cols = cols + self.flags
        info = self.cat.ix[self.current_idx, flag_cols]
        size, mu = info[cols]
        flags = info[self.flags]
        flag = flags[flags==1]
        if len(flag)==1:
            flag = flag.index[0]
        else:
            flag = 'n/a'
        if (self.review is not None) and (self.review != 'all'):
            txt = txt.replace('flag') 
            flag = self.cat_idx[self.current_idx]
        txt = txt.format(size, mu, flag)
        self.status.config(state='normal')
        self.status.delete(1.0, 'end')
        self.status.insert('insert', txt)
        self.status.config(state='disabled')

    def set_flag(self, flag, event=None):
        self.cat.loc[self.current_idx, flag] = 1
        others = [f for f in self.flags if f!=flag]
        self.cat.loc[self.current_idx, others] = 0
        self.next_idx()

    def save_progress(self, event=None):
        if self.review:
            print('No saving progess during review')
        else:
            self.cat.to_csv(self.out_fn, index=False)
            self.root.after(self.save_delta_t*60*1000, self.save_progress)

    def quit(self):
        if not self.review:
            self.save_progress()
        self.root.destroy()
