from __future__ import division, print_function

import os, sys
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from functools import partial
import webbrowser

import numpy as np
import matplotlib 
matplotlib.use("TkAgg")
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .utils import hsc_map_url
filedir = os.path.dirname(__file__)
maindir = os.path.dirname(filedir)
default_io = os.path.join(maindir, 'io')

__all__ = ['GUI']

class GUI(object):

    def __init__(self, root, master, review, clobber=False, io=None):

        # initialize attributes
        self.root = root
        self.master = master
        self.save_delta_t = 5 # minutes
        self.current_idx = 0
        self.flags = ['candy', 'junk', 'tidal', 'ambiguous']
        self.master.withdraw()
        self.review = review
        self.io = io if io else default_io

        # setup file names 
        # TODO -- make this a cmd line arg
        self.cat_fn = os.path.join(self.io, 'candy.csv')
        self.out_fn = os.path.join(
            self.io, 'viz-results-'+self.cat_fn.split('/')[-1])

        # if output catalog exists, check if we want to reload progress
        if os.path.isfile(self.out_fn) and not clobber:
            if review:
                self.cat = pd.read_csv(self.out_fn)
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
                        self._load_cat(self.cat_fn)
                    else:
                        self.root.destroy()
                        sys.exit('Exiting without changing anything...')
        else:
            self._load_cat(self.cat_fn)

        # build figure
        fs = 15
        self.fig = Figure(figsize=(10, 6))
        adjust = dict(wspace=0.13, 
                      hspace=0.25, 
                      bottom=0.1, 
                      top=0.97, 
                      right=0.96,
                      left=-0.02)
        grid = plt.GridSpec(2, 3, **adjust)
        self.ax_img = self.fig.add_subplot(
            grid[0:2, 0:2], xticks=[], yticks=[])
        self.ax_top = self.fig.add_subplot(grid[0,2])
        self.ax_bot = self.fig.add_subplot(grid[1,2])
        self.ax_top.scatter(self.cat['g-i'], self.cat['g-r'], alpha=0.3)
        self.ax_top.set_xlabel('$g-i$', fontsize=fs)
        self.ax_top.set_ylabel('$g-r$', fontsize=fs)
        self.ax_top.set_xlim(self.cat['g-i'].min()-0.1, 
                             self.cat['g-i'].max()+0.1)
        self.ax_top.set_ylim(self.cat['g-r'].min()-0.1, 
                             self.cat['g-r'].max()+0.1)
        self.ax_bot.scatter(
            self.cat['r_e'], self.cat.mu_e_ave_forced_g, alpha=0.3)
        self.ax_bot.set_xlabel(
            r'$r_\mathrm{eff}\ \mathrm{[arcsec]}$', fontsize=fs)
        self.ax_bot.set_ylabel(
            r'$\langle\mu_e(g)\rangle\ \mathrm{[mag/arcsec^2]}$', fontsize=fs)
        self.ax_bot.set_xlim(0, 16)
        self.ax_bot.set_ylim(24, 29)
        self.p1 = None
        self.p2 = None

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

        # create bottom buttons
        tk.Label(bot_fr, text='Source Index').grid(
            row=0, column=0, sticky='w')
        self.idx_evar= tk.IntVar()
        self.idx_evar.set(self.current_idx)
        idx_entry = tk.Entry(bot_fr, textvariable=self.idx_evar, takefocus=0)
        idx_entry.grid(row=0, column=1, sticky='w', padx=8)
        idx_entry.bind('<Return>', self.set_idx)

        tk.Label(bot_fr, text='Notes').grid(
            row=1, column=0, sticky='w')
        self.note_evar= tk.StringVar()
        self.note_evar.set(self.cat.loc[self.current_idx, 'notes'])
        note_entry = tk.Entry(bot_fr, textvariable=self.note_evar, takefocus=0)
        note_entry.grid(row=1, column=1, sticky='nsew', padx=8, columnspan=15)
        note_entry.bind('<Return>', self.add_note)

        prev_button = tk.Button(
            bot_fr, text='Previous', command=self.prev_idx)
        prev_button.grid(row=0, column=4, padx=12, sticky='nsew', columnspan=5)

        next_button = tk.Button(
            bot_fr, text='Next', command=self.next_idx)
        next_button.grid(row=0, column=9, sticky='nsew', columnspan=5)

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

        # create top buttons
        hmap_button = tk.Button(
            top_fr, text='hscMap', command=self.hsc_map)
        hmap_button.pack(side='left', padx=padx)

        quit_button = tk.Button(top_fr, text='Quit', command=self.quit)
        quit_button.pack(side='left', padx=padx)

        # useful key bindings
        self.master.bind_all('<1>', lambda event: event.widget.focus_set())

        # build canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.display_image()
        self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        self.master.deiconify()

        # save progress every save_delta_t minutes
        if not review:
            self.root.after(self.save_delta_t*60*1000, self.save_progress)

    def _load_cat(self, cat_fn):
        self.cat = pd.read_csv(cat_fn)
        self.cat['g-i'] = self.cat.m_tot_forced_g - self.cat.m_tot 
        self.cat['g-i'] = self.cat['g-i'] - self.cat.A_g + self.cat.A_i
        self.cat['g-r'] = self.cat.m_tot_forced_g - self.cat.m_tot_forced_r
        self.cat['g-r'] = self.cat['g-r'] - self.cat.A_g + self.cat.A_r
        self.cat['candy'] = -1
        self.cat['junk'] = -1
        self.cat['tidal'] = -1
        self.cat['ambiguous'] = -1
        self.cat['notes'] = " "

    def next_idx(self, event=None):
        self.add_note()
        self.current_idx += 1
        if self.current_idx > (len(self.cat)-1):
            msg = 'Congrats, visual inspection complete!'
            w = tk.Tk()
            w.withdraw()
            messagebox.showinfo('HSC-HUGs Message', msg, parent=w)
            w.destroy()
            self.quit()
        else:
            self.idx_evar.set(self.current_idx)
            self.note_evar.set(self.cat.loc[self.current_idx, 'notes'])
            self.display_image()

    def prev_idx(self, event=None):
        if self.current_idx > 0:
            self.add_note()
            self.current_idx -= 1
            self.idx_evar.set(self.current_idx)
            self.note_evar.set(self.cat.loc[self.current_idx, 'notes'])
            self.display_image()

    def set_idx(self, event=None):
        self.add_note()
        self.current_idx = self.idx_evar.get()
        self.note_evar.set(self.cat.loc[self.current_idx, 'notes'])
        self.display_image()

    def hsc_map(self):
        ra, dec = self.cat.loc[self.current_idx, ['ra', 'dec']]
        webbrowser.open(hsc_map_url(ra, dec), new=1)

    def display_image(self):
        self.update_info()
        self.ax_img.cla()
        self.ax_img.set(xticks=[], yticks=[])
        fn = 'images/candy-{}.png'.format(self.current_idx)
        image = mpimg.imread(os.path.join(self.io, fn))
        self.ax_img.imshow(image)

        idx = self.current_idx
        if self.p1 is not None:
            self.p1.remove()
            self.p2.remove()
        self.p1 = self.ax_top.scatter(self.cat.loc[idx, 'g-i'], 
                                      self.cat.loc[idx, 'g-r'], 
                                      c='k', s=300, marker='*', edgecolor='k')
        self.p2 = self.ax_bot.scatter(self.cat.loc[idx, 'r_e'],
                                      self.cat.loc[idx, 'mu_e_ave_forced_g'],
                                      c='k', s=300, marker='*', edgecolor='k')
        self.canvas.draw()

    def update_info(self):
        txt = 'id = {}, mu_0(g) = {:.2f}, n = {:.3f}, ell = {:.3f}, flag = {}' 
        cols = ['id', 'mu_0_forced_g', 'n', 'ell']
        flag_cols = cols + self.flags
        info = self.cat.ix[self.current_idx, flag_cols]
        ID, mu, n, ell = info[cols]
        flags = info[self.flags]
        flag = flags[flags==1]
        if len(flag)==1:
            flag = flag.index[0]
        else:
            flag = 'n/a'
        txt = txt.format(ID, mu, n, ell, flag)
        self.status.config(state='normal')
        self.status.delete(1.0, 'end')
        self.status.insert('insert', txt)
        self.status.config(state='disabled')

    def set_flag(self, flag, event=None):
        self.cat.loc[self.current_idx, flag] = 1
        others = [f for f in self.flags if f!=flag]
        self.cat.loc[self.current_idx, others] = 0
        self.next_idx()

    def add_note(self, event=None):
        note = self.note_evar.get()
        self.cat.loc[self.current_idx, 'notes'] = note

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
