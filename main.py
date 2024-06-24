from calendar import c
from re import L
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkcalendar import *
import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from config import config
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import csv
import json
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns

trenutni_korisnik = ""

class App(tb.Window):
    def __init__(self, *args, **kwargs):
        tb.Window.__init__(self, *args, **kwargs)

        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)

        self.title('FitTrack')
        self.iconphoto(False,tb.PhotoImage(file='Slike/FitTrack_Logo.png'))
        self.geometry("1000x800")

        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)

        self.frames= {}

        for F in (Login,Main,Create_User):
            frame = F(container,self)

            self.frames[F] = frame

            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(Login)
        self.set_theme("flatly")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
    
    def set_theme(self,theme_name):
        style = tb.Style()
        style.theme_use(theme_name)

class Login(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)

        login_frame = tb.Frame(self, width=400,height=400, )
        login_frame.place( relx=0.5,rely=0.3, anchor=CENTER )

        naslov_l = tb.Label(login_frame, text="FitTrack", bootstyle="success", font=("Lato",35,"italic"))
        naslov_l.grid(row=0,column=0, columnspan=2)

        ime_labela = tb.Label(login_frame,text="Korisnicko ime:", font=("Lato",12),bootstyle="dark")
        ime_labela.grid(row=1, column=0, padx= 5, sticky='e')

        ime_unos = tb.Entry(login_frame)  
        ime_unos.grid(row=1, column=1, pady=10)

        lozinka_labela = tb.Label(login_frame,text="Lozinka:", font=("Lato",12), bootstyle="dark")
        lozinka_labela.grid(row=2, column=0, padx= 5, sticky='e')

        loznika_unos = tb.Entry(login_frame, show="*")
        loznika_unos.grid(row=2, column=1, pady=10)

        def provera(ime,lozinka):
            params = config()
            connection = psycopg2.connect(**params)
            k = connection.cursor()
            query = "SELECT nalozi.korisnicko_ime, nalozi.lozinka FROM nalozi WHERE korisnicko_ime=%s AND lozinka=%s"
            k.execute(query, (ime,lozinka))
            provera = k.fetchone()
            connection.commit()
            k.close()
            connection.close()
            if provera:
                return True
            return False

        def uloguj():
            ime = ime_unos.get()
            lozinka=loznika_unos.get()
            if provera(ime,lozinka) == True:
                controller.show_frame(Main)
                global trenutni_korisnik 
                trenutni_korisnik = ime 
                
            else:
                messagebox.showwarning("Showwarning","Pogresno korisnicko ime ili lozinka")

        prijava_dugme = tb.Button(login_frame,text = "Prijavi se", 
            command=uloguj, bootstyle="success-outline")
        prijava_dugme.grid(row=3,column=0, pady=15)

        napravi_nalog = tb.Button(login_frame, text = "Napravi nalog",
            command= lambda : controller.show_frame(Create_User),
            bootstyle="success-outline")
        napravi_nalog.grid(row=3,column=1, pady=15)

 
class Main(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self,parent)

        def profil_strana():
            profil_frame= tb.Frame(main_frame)
            profil_frame.pack(side=TOP, anchor=NW)
            global trenutni_korisnik
            
            korisnik= tb.Label(profil_frame, text=trenutni_korisnik, bootstyle="secondary", font=("Lato", 25)) 
            korisnik.pack(pady=30,padx=10, anchor=W)

            info_frame=tb.LabelFrame(profil_frame, text="Summary", bootstyle="secondary")
            info_frame.pack(expand=TRUE, padx=10)    

            broj_treninga= tb.Label(info_frame, text="Broj treninga:", bootstyle="success",font=("Lato", 10, "bold"))
            broj_treninga.grid(row=0,column=0, padx=20, pady=10)
            
            najcesci_trening= tb.Label(info_frame, text="Najcesci trening:", bootstyle="success", font=("Lato", 10, "bold"))
            najcesci_trening.grid(row=0,column=1, padx=20)

            broj_kalorija= tb.Label(info_frame, text="Ukupan broj kalorija potroseno:", bootstyle="success", font=("Lato", 10, "bold"))
            broj_kalorija.grid(row=0,column=2, padx=20)


            def ukupan_br_treninga(kor_ime):
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="SELECT COUNT(datum) FROM trening  WHERE korisnicko_ime =%s"
                k.execute(query, (kor_ime,))
                br = k.fetchone()
                k.close()
                connection.close()
                return br
            
            def najcesci_trening(kor_ime):
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="SELECT vrsta_tr FROM trening WHERE korisnicko_ime = %s GROUP BY vrsta_tr ORDER BY COUNT(vrsta_tr) DESC LIMIT 1;"
                k.execute(query, (kor_ime,))
                br = k.fetchone()
                k.close()
                connection.close()
                return br
            
            def ukupan_broj_kalorija(kor_ime):
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="SELECT SUM(kalorije) FROM trening WHERE korisnicko_ime = %s;"
                k.execute(query,(kor_ime,))
                br = k.fetchone()
                k.close()
                connection.close()
                return br

            ukupan_tr = ukupan_br_treninga(trenutni_korisnik)
            najcesci_tr = najcesci_trening(trenutni_korisnik)
            ukupan_kl = ukupan_broj_kalorija(trenutni_korisnik)

            br_tr_prikaz= tb.Label(info_frame, text=ukupan_tr, bootstyle="success",font=("Lato", 10))
            br_tr_prikaz.grid(row=1,column=0, pady=5)

            naj_tr_prikaz= tb.Label(info_frame, text=najcesci_tr,bootstyle="success", font=("Lato", 10))
            naj_tr_prikaz.grid(row=1,column=1)

            br_kr_prikaz= tb.Label(info_frame, text=ukupan_kl, bootstyle="success" , font=("Lato", 10))
            br_kr_prikaz.grid(row=1,column=2)


            heder = tb.Label(profil_frame, text='Vrsta treninga Datum Trajanje treninga(min) Puls Potrosene kalorije', bootstyle="success", font=("Lato", 10))
            heder.pack(pady=30,padx=10, anchor=W)
            


            def uzmi_podatke():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query = "SELECT vrsta_tr, datum , trajanje_treninga, puls, kalorije FROM trening WHERE korisnicko_ime = %s"
                k.execute(query, (trenutni_korisnik,))
                rows = k.fetchall()
                connection.close()
                return rows

            
              
            def ucitaj_podatke():
                global data
                data = []
                
                rows = uzmi_podatke()
                for row_index, row in enumerate(rows, start=1):
                    tb.Label(prikaz_frame, text=row[0]).grid(row=row_index, column=0, padx=5, pady=5, sticky='w')
                    tb.Label(prikaz_frame, text=row[1]).grid(row=row_index, column=1, padx=5, pady=5, sticky='w')
                    tb.Label(prikaz_frame, text=row[2]).grid(row=row_index, column=2, padx=5, pady=5, sticky='w')
                    tb.Label(prikaz_frame, text=row[3]).grid(row=row_index, column=3, padx=5, pady=5, sticky='w')
                    tb.Label(prikaz_frame, text=row[4]).grid(row=row_index, column=4, padx=5, pady=5, sticky='w')
                    data.append((row[0], row[1], row[2],row[3],row[4]))

           
            prikaz_canvas = tk.Canvas(profil_frame)
            prikaz_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            brisanje_scrollbar = tb.Scrollbar(profil_frame, orient=tk.VERTICAL, command=prikaz_canvas.yview)
            brisanje_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
           
            prikaz_frame = tb.Frame(prikaz_canvas)
            prikaz_frame.pack(padx=10, pady=10, anchor='w')

            prikaz_canvas.create_window((0, 0), window=prikaz_frame, anchor='nw')
            prikaz_frame.bind("<Configure>", lambda event, canvas=prikaz_canvas: canvas.configure(scrollregion=canvas.bbox("all")))
            prikaz_canvas.configure(yscrollcommand=brisanje_scrollbar.set)

           
            ucitaj_podatke()

        def statistika_strana():
            statistika_frame= tb.Frame(main_frame)
            statistika_frame.pack(side=TOP, anchor=NW)
            global trenutni_korisnik    

            opcije_frame = tb.LabelFrame(statistika_frame, text="Izaberite statistiku koju zelite da analizirate:", height=400, width=800, bootstyle="success")
            opcije_frame.pack(padx=10, pady=10, anchor='w')

            def histogram():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                
                query = "SELECT trajanje_treninga FROM trening WHERE korisnicko_ime = %s"
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.commit()
                connection.close()
                df= pd.DataFrame(podaci, columns=['trajanje_treninga'])
              
                plt.figure(figsize=(10, 6))
                plt.hist(df['trajanje_treninga'], bins=20, edgecolor='black')
                plt.title('Distribucija Trajanja Treninga')
                plt.xlabel('Trajanje Treninga (u minutima)')
                plt.ylabel('Broj Treninga')
                plt.grid(True)
                plt.show()

                


            def linijski():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                
                query = "SELECT datum, kalorije FROM trening WHERE korisnicko_ime = %s ORDER BY datum"
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.commit()
                connection.close()
                df= pd.DataFrame(podaci, columns=['datum', 'kalorije'])
              
                plt.figure(figsize=(10, 6))
                plt.plot(df['datum'], df['kalorije'], marker='o', linestyle='-')
                plt.title('Trosenje kalorije po treningu')
                plt.xlabel('Datum')
                plt.ylabel('Potrosene kalorije')
                plt.grid(True)
                plt.show()
                

            def bar():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query = "SELECT vrsta_tr, AVG(kalorije) as prosecne_kalorije FROM trening WHERE korisnicko_ime = %s GROUP BY vrsta_tr"
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.commit()
                connection.close()
                df= pd.DataFrame(podaci, columns=['vrsta_tr', 'prosecne_kalorije'])
              
                plt.figure(figsize=(10, 6))
                plt.bar(df['vrsta_tr'], df['prosecne_kalorije'], color='blue')
                plt.title('Prosecno utrosene kalorije po vrsti treninga')
                plt.xlabel('Vrsta treninga')
                plt.ylabel('Prosecne kalorije')
                plt.xticks(rotation=45)
                plt.grid(axis='y')
                plt.show()

            
            def scatter():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query = "SELECT trajanje_treninga, puls FROM trening WHERE korisnicko_ime = %s"
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.commit()
                connection.close()
                df= pd.DataFrame(podaci, columns=['trajanje_treninga', 'puls'])
              
                plt.figure(figsize=(10, 6))
                plt.scatter(df['trajanje_treninga'], df['puls'], color='blue')
                plt.title('Prikaz odnosa izmedju trajanja treninga i pulsa')
                plt.xlabel('Trajanje treninga')
                plt.ylabel('Puls')
                plt.grid(True)
                plt.show()
                

            def pie():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query = "SELECT vrsta_tr, COUNT(*) as broj_treninga FROM trening WHERE korisnicko_ime = %s GROUP BY vrsta_tr"
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.close()
                df= pd.DataFrame(podaci, columns=['vrsta_tr', 'broj_treninga'])
              
                plt.figure(figsize=(10, 6))
                plt.pie(df['broj_treninga'], labels =df['vrsta_tr'],autopct='%1.1f%%', startangle=140)
                plt.title('Prikaz distribucije odradjenih treninga')
                plt.axis('equal')
                plt.show()
                

            def heat():
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query = """SELECT EXTRACT(DAY FROM datum) as dan, vrsta_tr, COUNT(*) as broj_treninga
                    FROM trening
                    WHERE korisnicko_ime = %s
                    GROUP BY dan, vrsta_tr
                    ORDER BY dan, vrsta_tr"""
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.close()
                df= pd.DataFrame(podaci, columns=['dan', 'vrsta_tr', 'broj_treninga'])
                df_pivot = df.pivot(index="vrsta_tr", columns="dan", values="broj_treninga")
                df_pivot = df_pivot.fillna(0).astype(int)
                plt.figure(figsize=(12, 8))
                sns.heatmap(df_pivot, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5)
                plt.title('Aktivnosti Korisnika po Danima i Vrsti Treninga')
                plt.xlabel('Dan u Mesecu')
                plt.ylabel('Vrsta Treninga')
                plt.show()

               

            histogram_dugme = tb.Button(opcije_frame, text="Prikaz distribucije trajanja treninga", width=40, bootstyle="success", command=histogram)
            histogram_dugme.grid(row=0, column=0, padx=10, pady=10)

            linijski_dugme = tb.Button(opcije_frame, text="Prikaz sagorelih kalorija tokom vremena", width=40,  bootstyle="success", command=linijski)
            linijski_dugme.grid(row=0, column=1, padx=10, pady=10)

            bar_dugme = tb.Button(opcije_frame, text="Prosecne sagorele kalorije po vrsti treninga", width=40, bootstyle="success", command=bar)
            bar_dugme.grid(row=1, column=0, padx=10, pady=10)

            scatter_dugme = tb.Button(opcije_frame, text="Prikaz odnosa izmedju trajanja treninga i pulsa", width=40, bootstyle="success", command=scatter)
            scatter_dugme.grid(row=1, column=1, padx=10, pady=10)

            pie_dugme = tb.Button(opcije_frame, text="Prikaz distribucije odradjenih treninga", width=40, bootstyle="success", command=pie)
            pie_dugme.grid(row=2, column=0, padx=10, pady=10)

            heat_dugme = tb.Button(opcije_frame, text="Prikaz aktivnosti korisnika ", width=40, bootstyle="success", command=heat)
            heat_dugme.grid(row=2, column=1, padx=10, pady=10)


        def trening_strana():
            trening_frame= tb.Frame(main_frame)
            trening_frame.pack(side=TOP, anchor=NW)

            unos_frame = tb.LabelFrame(trening_frame, text = "Unesite podatke o treningu", height=400, width=800, bootstyle="success")
            unos_frame.pack(padx=10, pady=10, anchor='w')

            trajanje_tr = tb.Label(unos_frame, text="Unesite vreme trajanja treninga u minutima:", font=("Lato", 15), bootstyle="success")
            trajanje_tr.grid(row=0,column=0, padx=10, pady=10, sticky="w" )
            trajanje_tr_unos = tb.Entry(unos_frame )
            trajanje_tr_unos.grid(row=0, column=1, padx=10)

            puls = tb.Label(unos_frame, text="Unesite puls:", font=("Lato", 15), bootstyle="success")
            puls.grid(row=1,column=0, padx=10, pady=10, sticky="w" )
            puls_unos = tb.Entry(unos_frame )
            puls_unos.grid(row=1, column=1, padx=10)

            kalorije = tb.Label(unos_frame, text="Unesite potrosene kalorije:", font=("Lato", 15), bootstyle="success")
            kalorije.grid(row=2,column=0, padx=10, pady=10, sticky="w" )
            kalorije_unos = tb.Entry(unos_frame )
            kalorije_unos.grid(row=2, column=1, padx=10)

            datum = tb.Label(unos_frame, text="Izaberite datum treninga:", font=("Lato", 15), bootstyle="success")
            datum.grid(row=3,column=0, padx=10, pady=10, sticky="w" )
            datum_unos = tb.DateEntry(unos_frame)
            datum_unos.grid(row=3, column=1, padx=10)

            vrsta_tr = tb.Label(unos_frame, text="Izaberite odradjeni trening:", font=("Lato", 15), bootstyle="success")
            vrsta_tr.grid(row=4,column=0, padx=10, pady=10, sticky="w" )

            lista_treninga = []
            params = config()
            connection = psycopg2.connect(**params)
            k = connection.cursor()
            query="SELECT ime_treninga FROM vrsta_treninga"
            k.execute(query)
            
            for row in k:
                lista_treninga.append(row)
            connection.commit()
            k.close()
            connection.close()

            vrsta_treninga = tb.Combobox(unos_frame, state=READONLY, values=lista_treninga)
            vrsta_treninga.grid(row=4, column=1, padx=10)

            def unos_tr():
                global trenutni_korisnik
                trajanje = trajanje_tr_unos.get()
                puls= puls_unos.get()
                kalorije = kalorije_unos.get()
                datum = datum_unos.entry.get()
                vrsta = vrsta_treninga.get().strip()

                if trajanje == 0 or puls == 0 or kalorije == 0 or vrsta == "":
                    messagebox.showwarning("showwarning", "Nisu sva polja popunjena")
                else:
                    connection = psycopg2.connect(**params)
                    k = connection.cursor()
                    query="SELECT MAX(trening_id) FROM trening"
                    k.execute(query)
                    poslednj_tr_id = k.fetchone()[0]
                    novi_tr_id = poslednj_tr_id+1
                    query="INSERT INTO trening(trening_id,korisnicko_ime,trajanje_treninga,puls,kalorije, datum, vrsta_tr) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                    k.execute(query,(novi_tr_id,trenutni_korisnik,trajanje,puls,kalorije,datum,vrsta))
                    connection.commit()
                    k.close()
                    connection.close()
                    messagebox.showinfo("showinfo", "Trening je uspesno unesen")

            unos_treninga = tb.Button(unos_frame, text="Unesi trening", width=15, bootstyle="success", command=unos_tr)
            unos_treninga.grid(row=5,column=0,  columnspan=2,pady=10, padx=10, sticky="e")


            def uzmi_podatke():
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="SELECT trening_id, datum, vrsta_tr FROM trening WHERE korisnicko_ime  = %s"
                k.execute(query, (trenutni_korisnik,))
                rows = k.fetchall()
                connection.commit()
                k.close()
                connection.close()
                return rows
            
            def obrisi():
                cekiran = [id_var.get() for id_var, _, _ in data if id_var.get() != ""]
                if cekiran:
                    connection = psycopg2.connect(**params)
                    k = connection.cursor()
                    placeholders = ','.join(['%s'] * len(cekiran))
                    query = f"DELETE FROM trening WHERE trening_id IN ({placeholders})"
                    k.execute(query,cekiran)
                    connection.commit()
                    k.close()
                    connection.close()
                    refresuj_podatke()
                    messagebox.showinfo("showinfo", "Uspesno ste obrisali")

            
            def refresuj_podatke():
                for widget in brisanje_frame.winfo_children():
                    if isinstance(widget, tb.Checkbutton) or isinstance(widget, tb.Label):
                        widget.destroy()
                ucitaj_podatke()

            def ucitaj_podatke():
                global data
                data = []
                rows = uzmi_podatke()
                for row in rows:
                    id_var = tk.StringVar(value="")
                    cb = tb.Checkbutton(brisanje_frame, variable=id_var, onvalue=str(row[0]), offvalue="")
                    cb.grid(row=rows.index(row), column=0, padx=5, pady=5, sticky='w')
                    tb.Label(brisanje_frame, text=row[1]).grid(row=rows.index(row), column=1, padx=5, pady=5, sticky='w')
                    tb.Label(brisanje_frame, text=row[2]).grid(row=rows.index(row), column=2, padx=5, pady=5, sticky='w')
                    data.append((id_var, row[1], row[2]))

            
            brisanje_canvas = tk.Canvas(trening_frame)
            brisanje_canvas.pack(side=LEFT, fill=BOTH, expand=True)

           
            brisanje_scrollbar = tb.Scrollbar(trening_frame, orient=VERTICAL, command=brisanje_canvas.yview)
            brisanje_scrollbar.pack(side=RIGHT, fill=Y)

          
            content_frame = tb.Frame(trening_frame)
            content_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=10)

            brisanje_frame = tb.LabelFrame(brisanje_canvas, text="Obrišite trening", bootstyle="success")
            brisanje_frame.pack(padx=10, pady=10, anchor='w')

            brisanje_canvas.create_window((0, 0), window=brisanje_frame, anchor='nw')
            brisanje_frame.bind("<Configure>", lambda event, canvas=brisanje_canvas: canvas.configure(scrollregion=canvas.bbox("all")))
            brisanje_canvas.configure(yscrollcommand=brisanje_scrollbar.set)

          
            brisanje_button = tb.Button(content_frame, text="Obriši odabrano",width=15, bootstyle="success", command=obrisi)
            brisanje_button.pack(padx=10, pady=10)

            ucitaj_podatke()


        def podesavanje_strana():
            podesavanje_frame= tb.Frame(main_frame)
            podesavanje_frame.pack(side=TOP, anchor=NW)

            profil_frame = tb.LabelFrame(podesavanje_frame, text="Izmene profila", height=400, width=800, bootstyle="success")
            profil_frame.pack(padx=10, pady=10, anchor='w')
            
            loz_lb = tb.Label(profil_frame, text="Nova lozinku:", font=("Lato", 15), bootstyle="success")
            loz_lb.grid(row=0,column=0, padx=10, pady=10, sticky="w" )
            loz_unos = tb.Entry(profil_frame, show="*")
            loz_unos.grid(row=0, column=1, padx=10)

            loz_pr_lb = tb.Label(profil_frame, text="Ponovite lozinku:", font=("Lato", 15), bootstyle="success")
            loz_pr_lb.grid(row=1,column=0, padx=10, pady=10, sticky="w" )
            loz_pr_unos = tb.Entry(profil_frame, show="*")
            loz_pr_unos.grid(row=1, column=1, padx=10)


            def izmena_profila():
                global trenutni_korisnik
                nova_loz = loz_unos.get()
                nova_loz_pr = loz_pr_unos.get()

                if  nova_loz.strip() == "" or nova_loz_pr.strip() == "":
                    messagebox.showwarning("showwarning", "Nisu sva polja popunjena")
                elif nova_loz != nova_loz_pr:
                    messagebox.showwarning("showwarning", "Lozinke se ne podudaraju")
                    
                else:
                    params = config()
                    connection = psycopg2.connect(**params)
                    k = connection.cursor()
                    query="UPDATE nalozi SET lozinka=%s WHERE korisnicko_ime = %s"
                    k.execute(query,(nova_loz, trenutni_korisnik))
                    connection.commit()
                    k.close()
                    connection.close()
                    messagebox.showinfo("showinfo", "Sifra je uspesno promenjena")

                

            izmena_but = tb.Button(profil_frame, text="Izmeni", 
                                   width=15, bootstyle="success", command=izmena_profila)
            izmena_but.grid(row=2,column=0,  columnspan=2,pady=10, padx=10, sticky="e")

            god_lb =tb.Label(profil_frame,text="Izaberite vase godine",  font=("Lato", 15), bootstyle="success")
            god_lb.grid(row=3, column=0,padx=10)
            god_sp = tb.Spinbox(profil_frame, from_=0, to=99, state=READONLY)    
            god_sp.grid(row=3, column=1, padx=10)


            def izmena_godina():
                global trenutni_korisnik
                nove_god  = god_sp.get()
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="UPDATE nalozi SET godine=%s WHERE korisnicko_ime = %s"
                k.execute(query, (nove_god, trenutni_korisnik))
                connection.commit()
                k.close()
                connection.close()
                messagebox.showinfo("showinfo", "Godine su uspesno promenjene")

            izmena_but_2 = tb.Button(profil_frame, text="Izmeni", 
                                   width=15, bootstyle="success", command=izmena_godina)
            izmena_but_2.grid(row=4,column=0,  columnspan=2,pady=10, padx=10, sticky="e")


            podaci_frame = tb.LabelFrame(podesavanje_frame, text="Podaci", height=200, width=800)
            podaci_frame.pack(padx=10, pady=10, anchor='w')

            text_lb = tb.Label(podaci_frame, text="Izaberite format za preuzimanje podataka")
            text_lb.grid(row=0, column=0, padx=10)
            format_cb = tb.Combobox(podaci_frame, state="readonly", values=["PDF","CSV", "JSON", "Txt"])
            format_cb.grid(row=0, column=1)


            def preuzmi():
                format= format_cb.get()
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="SELECT * FROM trening WHERE korisnicko_ime = %s"
                k.execute(query,(trenutni_korisnik,))
                podaci = k.fetchall()
                k.close()
                connection.close()

                if format == "PDF":

                    kolone = ["Trening id", "Korisnicko ime", "Trajanje(min)", "Puls", "Potrosene kalorije", "Datum treninga", "Vrsta treninga"]
                    ime_pdf = f"{trenutni_korisnik}_podaci.pdf"
                    pdf = SimpleDocTemplate(ime_pdf, pagesize = letter)
                    tabela_podaci= []
                    tabela_podaci.append(kolone)
                    for red in podaci:
                        tabela_podaci.append(red)

                    tabela = Table(tabela_podaci)

                    stil_za_kolone = TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), 
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),      
                            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),                
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),     
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),              
                            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),   
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),      
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)        
                        ])
                    tabela.setStyle(stil_za_kolone)
                    pdf_sadrzaj = [tabela]
                    pdf.build(pdf_sadrzaj)
                    messagebox.showinfo("showinfo", "Podaci su uspesno sacuvani")

                elif format == "CSV":

                    kolone = ["Trening id", "Korsinicko ime", "Trajanje(min)", "Puls", "Potrosene kalorije", "Datum treninga", "Vrsta treninga"]
                    ime_csv = f"{trenutni_korisnik}_podaci.csv"
                    with open(ime_csv, "w", newline='', encoding='utf-8') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        csv_writer.writerow(kolone)
                        csv_writer.writerows(podaci)
                    messagebox.showinfo("showinfo", "Podaci su uspesno sacuvani")

                elif format == "JSON":
                    json_podaci = []
                    for red in podaci:
                        json_red = {
                            "trening_id": red[0],
                            "korisnicko ime": red[1],
                            "trajanje": red[2],
                            "puls": red[3],
                            "kalorije": red[4],
                            "datum": red[5].isoformat(), 
                            "vrsta": red[6]
                        }
                        json_podaci.append(json_red)
                    ime_json=f"{trenutni_korisnik}_podaci.json"
                    with open(ime_json, 'w', encoding='utf-8') as json_file:
                        json.dump(json_podaci, json_file, ensure_ascii=False, indent=4)
                    messagebox.showinfo("showinfo", "Podaci su uspesno sacuvani")
          
                else:
                    ime_txt = f"{trenutni_korisnik}_podaci.txt"
                    with open(ime_txt, 'w') as txt_file:
                        for red in podaci:
                            txt_file.write(str(red) + '\n')
                    messagebox.showinfo("showinfo", "Podaci su uspesno sacuvani")


            izmena_but = tb.Button(podaci_frame, text="Preuzmi podatke", 
                                   width=15, bootstyle="success", command=preuzmi)
            izmena_but.grid(row=1,column=0,  columnspan=2,pady=10, padx=10, sticky="e")



        def resetuj_stranu():
            for frame in main_frame.winfo_children():
                frame.destroy()

        def sakriji_indikatore():
            profil_indikator.config(bootstyle="inverse-success")
            statistika_indikator.config(bootstyle="inverse-success")
            trening_indikator.config(bootstyle="inverse-success")
            podesavanja_indikator.config(bootstyle="inverse-success")


        def indikatori(oznaka, strana ):
            sakriji_indikatore()
            oznaka.config(bootstyle="inverse-info")
            resetuj_stranu()
            strana()
            

        button_frame = tb.Frame(self, bootstyle="success")
        button_frame.pack(side=LEFT)
        button_frame.pack_propagate(False)
        button_frame.configure(width=200, height=800)

        ime_label = tb.Label(button_frame, text="FitTrack", bootstyle="inverse-success", font=("Lato", 25, "italic"))
        ime_label.place(x=30, y=30)

        profil_dugme = tb.Button(button_frame, text ="Profil", width=15, 
                                bootstyle="outline-success", command=lambda:indikatori(profil_indikator, profil_strana))
        profil_dugme.place(x=30, y=100)

        profil_indikator= tb.Label(button_frame, text=' ', bootstyle="inverse-success")
        profil_indikator.place(x=22, y=100, width=7, height=35)

        statistika_dugme = tb.Button(button_frame, text = "Statistika", width=15, 
                                bootstyle="outline-success",  command=lambda:indikatori(statistika_indikator, statistika_strana))  
        statistika_dugme.place(x=30, y= 150)

        statistika_indikator= tb.Label(button_frame, text=' ', bootstyle="inverse-success")
        statistika_indikator.place(x=22, y=150, width=7, height=35)

        trening_dugme = tb.Button(button_frame, text = "Trening", width=15, 
                                bootstyle="outline-success",  command=lambda:indikatori(trening_indikator, trening_strana))
        trening_dugme.place(x=30, y=200)

        trening_indikator= tb.Label(button_frame, text=' ', bootstyle="inverse-success")
        trening_indikator.place(x=22, y=200, width=7, height=35)

        podesavanja_dugme = tb.Button(button_frame, text = "Podesavanja", width=15, 
                                    bootstyle="outline-success",  command=lambda:indikatori(podesavanja_indikator, podesavanje_strana))
        podesavanja_dugme.place(x=30, y=250)

        podesavanja_indikator= tb.Label(button_frame, text=' ', bootstyle="inverse-success")
        podesavanja_indikator.place(x=22, y=250, width=7, height=35)

        izloguj_dugme = tb.Button(button_frame, text = "Izloguj se",
             command=lambda : controller.show_frame(Login), width=15 , bootstyle="outline-success")
        izloguj_dugme.place(x=30, y=720)


        main_frame = tb.Frame(self)
        main_frame.pack(side=LEFT)
        main_frame.pack_propagate(False)
        main_frame.configure(height=800, width=800)
       

class Create_User(tk.Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)


        create_frame = tb.Frame(self, width=500,height=800)
        create_frame.place( relx=0.5,rely=0.3, anchor=CENTER )


        ime_labela = tb.Label(create_frame, text="Kreirajte vas korisnicki nalog", style="success", font=("Lato", 20,"italic"))
        ime_labela.grid(row=0, column=0, columnspan=2,pady=10)

        ime_labela = tb.Label(create_frame, text="Korisnicko ime:", font=("Lato",12),bootstyle="dark")
        ime_labela.grid(row=1, column=0, sticky="e", pady=10)

        ime_unos = tb.Entry(create_frame)
        ime_unos.grid(row=1, column=1)

        lozinka_labela = tb.Label(create_frame, text="Lozinka:" ,font=("Lato",12),bootstyle="dark")
        lozinka_labela.grid(row=2, column=0, sticky="e",pady=10)

        loznika_unos = tb.Entry(create_frame, show="*")
        loznika_unos.grid(row=2, column=1)

        lozinka_labela_1 = tb.Label(create_frame, text="Ponovite lozinku:",font=("Lato",12),bootstyle="dark")
        lozinka_labela_1.grid(row=3, column=0, sticky="e",pady=10)

        loznika_unos_1 = tb.Entry(create_frame, show="*")
        loznika_unos_1.grid(row=3, column=1)

        email_labela = tb.Label(create_frame, text="Unesite email:",font=("Lato",12),bootstyle="dark")
        email_labela.grid(row=4, column=0, sticky="e",pady=10)

        email_unos = tb.Entry(create_frame)
        email_unos.grid(row=4, column=1)

        godine_labela = tb.Label(create_frame,text="Unesite koliko imate godina:",font=("Lato",12),bootstyle="dark")
        godine_labela.grid(row=5, column=0, sticky="e",pady=10)

        godine_val = StringVar()
        godine_unos = tb.Entry(create_frame, textvariable=godine_val)
        godine_unos.grid(row=5, column=1)

        pol_labela = tb.Label(create_frame, text="Izaberite Vas pol:",font=("Lato",12),bootstyle="dark")
        pol_labela.grid(row=6, column=0, sticky="e",pady=10)

        pol_combo = tb.Combobox(create_frame, state="readonly", values=["Muski", "Zenski"])
        pol_combo.grid(row=6, column=1)

        def postoji_kor(ime):
            params = config()
            connection = psycopg2.connect(**params)
            k = connection.cursor()
            query = "SELECT nalozi.korisnicko_ime FROM nalozi WHERE korisnicko_ime=%s"
            k.execute(query, (ime,))
            provera = k.fetchone()
            connection.commit()
            k.close()
            connection.close()
            if provera:
                return True
            return False
        
        def postoji_email(email):
            params = config()
            connection = psycopg2.connect(**params)
            k = connection.cursor()
            query = "SELECT nalozi.email FROM nalozi WHERE email=%s"
            k.execute(query, (email,))
            provera = k.fetchone()
            connection.commit()
            k.close()
            connection.close()
            if provera:
                return True
            return False

        def Kreiranje_Naloga():
            kor_ime = ime_unos.get().strip()
            lozinka = loznika_unos.get().strip()
            lozinka_pon = loznika_unos_1.get().strip()
            godine = godine_val.get()
            pol = pol_combo.get().strip()
            email = email_unos.get()

            godine_int = int(godine) if godine.isdigit() else 0

            if kor_ime == "" or lozinka == "" or lozinka_pon == "" or godine_int < 1 or pol == "":
                messagebox.showwarning("showwarning", "Nisu sva polja popunjena")
            elif lozinka != lozinka_pon:
                messagebox.showwarning("showwarning", "Lozinke se ne podudaraju")
            elif postoji_kor(kor_ime):
                messagebox.showwarning("showwarning", "Korisnicko ime vec postoji")
            elif postoji_email(email):
                messagebox.showwarning("showwarning", "Email je u upotrebi")
                
            else:
                params = config()
                connection = psycopg2.connect(**params)
                k = connection.cursor()
                query="INSERT INTO nalozi(nalog_id, korisnicko_ime, lozinka, godine, pol, email) VALUES (DEFAULT, %s, %s, %s, %s, %s)"
                k.execute(query,(kor_ime, lozinka, godine_int, pol, email))
                connection.commit()
                k.close()
                connection.close()
                messagebox.showinfo("showinfo", "Nalog je uspesno kreiran")

        kreiraj_korisnika = tb.Button(create_frame, text="Kreiraj nalog",
             command=Kreiranje_Naloga, style="success-outline")
        kreiraj_korisnika.grid(row=8, column=0, pady=10)

        idi_log = tb.Button(create_frame, text="Nazad", 
            command=lambda: controller.show_frame(Login), style="success-outline")
        idi_log.grid(row=8, column=1, pady=10)


app = App()
app.mainloop()