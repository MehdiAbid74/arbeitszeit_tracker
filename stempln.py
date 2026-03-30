import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DATEN_ORDNER = "arbeitszeiten"

WOCHENTAGE = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}


def ordner_erstellen():
    os.makedirs(DATEN_ORDNER, exist_ok=True)


def aktuelle_monatsdatei():
    jetzt = datetime.now()
    return os.path.join(DATEN_ORDNER, jetzt.strftime("%Y-%m") + ".csv")


def datei_fuer_monat_erstellen_wenn_noetig(datei):
    if not os.path.exists(datei):
        with open(datei, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Datum", "Uhrzeit", "Aktion"])


class ArbeitszeitTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Arbeitszeit Tracker")
        self.root.geometry("980x650")
        self.root.resizable(False, False)

        ordner_erstellen()
        self.datei = aktuelle_monatsdatei()
        datei_fuer_monat_erstellen_wenn_noetig(self.datei)

        self.letzte_aktion = self.letzte_aktion_laden()

        titel = tk.Label(
            self.root,
            text="Arbeitszeit Tracker",
            font=("Arial", 20, "bold")
        )
        titel.pack(pady=10)

        self.heute_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.heute_label.pack()

        self.uhrzeit_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.uhrzeit_label.pack(pady=3)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=8)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Einstempeln",
            width=18,
            command=self.einstempeln
        ).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Ausstempeln",
            width=18,
            command=self.ausstempeln
        ).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Übersicht anzeigen",
            width=18,
            command=self.uebersicht_anzeigen
        ).grid(row=0, column=2, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="CSV exportieren",
            width=18,
            command=self.csv_exportieren
        ).grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Monatsstunden",
            width=18,
            command=self.monatsstunden_anzeigen
        ).grid(row=0, column=4, padx=5, pady=5)

        self.tree = ttk.Treeview(
            self.root,
            columns=("tag", "datum", "ein", "aus", "stunden"),
            show="headings",
            height=20
        )

        self.tree.heading("tag", text="Tag")
        self.tree.heading("datum", text="Datum")
        self.tree.heading("ein", text="Einstempeln")
        self.tree.heading("aus", text="Ausstempeln")
        self.tree.heading("stunden", text="Stunden")

        self.tree.column("tag", width=180, anchor="center")
        self.tree.column("datum", width=140, anchor="center")
        self.tree.column("ein", width=180, anchor="center")
        self.tree.column("aus", width=180, anchor="center")
        self.tree.column("stunden", width=140, anchor="center")

        self.tree.pack(pady=15)

        self.monat_summe_label = tk.Label(
            self.root,
            text="Gesamtstunden im Monat: 00:00",
            font=("Arial", 12, "bold")
        )
        self.monat_summe_label.pack(pady=5)

        self.zeit_aktualisieren()
        self.status_aktualisieren()
        self.uebersicht_anzeigen()

    def aktuelle_datei_aktualisieren(self):
        self.datei = aktuelle_monatsdatei()
        datei_fuer_monat_erstellen_wenn_noetig(self.datei)

    def zeit_aktualisieren(self):
        self.aktuelle_datei_aktualisieren()

        jetzt = datetime.now()
        tag_en = jetzt.strftime("%A")
        tag_de = WOCHENTAGE.get(tag_en, tag_en)

        self.heute_label.config(text=f"Heute: {tag_de}, {jetzt.strftime('%d.%m.%Y')}")
        self.uhrzeit_label.config(text=f"Aktuelle Uhrzeit: {jetzt.strftime('%H:%M:%S')}")

        self.root.after(1000, self.zeit_aktualisieren)

    def letzte_aktion_laden(self):
        self.aktuelle_datei_aktualisieren()

        letzte = None
        with open(self.datei, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for zeile in reader:
                letzte = zeile["Aktion"]
        return letzte

    def status_aktualisieren(self):
        if self.letzte_aktion == "EIN":
            self.status_label.config(text="Status: Eingestempelt", fg="green")
        else:
            self.status_label.config(text="Status: Nicht eingestempelt", fg="red")

    def eintrag_speichern(self, aktion):
        self.aktuelle_datei_aktualisieren()

        jetzt = datetime.now()
        datum = jetzt.strftime("%Y-%m-%d")
        uhrzeit = jetzt.strftime("%H:%M:%S")

        with open(self.datei, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([datum, uhrzeit, aktion])

        self.letzte_aktion = aktion
        self.status_aktualisieren()

    def einstempeln(self):
        if self.letzte_aktion == "EIN":
            messagebox.showwarning("Warnung", "Du bist schon eingestempelt.")
            return

        self.eintrag_speichern("EIN")
        messagebox.showinfo("Gespeichert", "Einstempeln gespeichert.")
        self.uebersicht_anzeigen()

    def ausstempeln(self):
        if self.letzte_aktion != "EIN":
            messagebox.showwarning("Warnung", "Du musst zuerst einstempeln.")
            return

        self.eintrag_speichern("AUS")
        messagebox.showinfo("Gespeichert", "Ausstempeln gespeichert.")
        self.uebersicht_anzeigen()

    def daten_laden(self):
        self.aktuelle_datei_aktualisieren()

        daten = {}

        with open(self.datei, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for zeile in reader:
                datum = zeile["Datum"]
                uhrzeit = zeile["Uhrzeit"]
                aktion = zeile["Aktion"]

                if datum not in daten:
                    daten[datum] = []

                daten[datum].append((uhrzeit, aktion))

        return daten

    def sekunden_zu_zeittext(self, sekunden):
        stunden = int(sekunden // 3600)
        minuten = int((sekunden % 3600) // 60)
        return f"{stunden:02d}:{minuten:02d}"

    def tag_auswerten(self, datum, eintraege):
        erste_ein = ""
        letzte_aus = ""
        gesamt_sekunden = 0
        start_zeit = None

        eintraege_sortiert = sorted(eintraege, key=lambda x: x[0])

        for uhrzeit, aktion in eintraege_sortiert:
            zeit_obj = datetime.strptime(datum + " " + uhrzeit, "%Y-%m-%d %H:%M:%S")

            if aktion == "EIN":
                if erste_ein == "":
                    erste_ein = uhrzeit
                start_zeit = zeit_obj

            elif aktion == "AUS":
                letzte_aus = uhrzeit
                if start_zeit is not None:
                    diff = (zeit_obj - start_zeit).total_seconds()
                    if diff > 0:
                        gesamt_sekunden += diff
                    start_zeit = None

        datum_obj = datetime.strptime(datum, "%Y-%m-%d")
        tag_en = datum_obj.strftime("%A")
        tag_de = WOCHENTAGE.get(tag_en, tag_en)
        datum_text = datum_obj.strftime("%d.%m.%Y")

        return {
            "tag": tag_de,
            "datum": datum_text,
            "erste_ein": erste_ein if erste_ein else "-",
            "letzte_aus": letzte_aus if letzte_aus else "-",
            "sekunden": int(gesamt_sekunden),
            "stunden_text": self.sekunden_zu_zeittext(gesamt_sekunden)
        }

    def monatsdaten(self):
        daten = self.daten_laden()
        zeilen = []
        monat_sekunden = 0

        for datum in sorted(daten.keys()):
            info = self.tag_auswerten(datum, daten[datum])
            zeilen.append(info)
            monat_sekunden += info["sekunden"]

        return zeilen, monat_sekunden

    def uebersicht_anzeigen(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        zeilen, monat_sekunden = self.monatsdaten()

        for info in zeilen:
            self.tree.insert(
                "",
                "end",
                values=(
                    info["tag"],
                    info["datum"],
                    info["erste_ein"],
                    info["letzte_aus"],
                    info["stunden_text"]
                )
            )

        self.monat_summe_label.config(
            text=f"Gesamtstunden im Monat: {self.sekunden_zu_zeittext(monat_sekunden)}"
        )

    def monatsstunden_anzeigen(self):
        _, monat_sekunden = self.monatsdaten()
        messagebox.showinfo(
            "Monatsstunden",
            f"Du hast in diesem Monat {self.sekunden_zu_zeittext(monat_sekunden)} Stunden gearbeitet."
        )

    def csv_exportieren(self):
        zeilen, monat_sekunden = self.monatsdaten()

        if not zeilen:
            messagebox.showwarning("Keine Daten", "Für diesen Monat gibt es keine Daten.")
            return

        aktueller_monat = datetime.now().strftime("%Y-%m")
        standard_name = f"arbeitszeiten_{aktueller_monat}.csv"

        pfad = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=standard_name,
            filetypes=[("CSV-Dateien", "*.csv")]
        )

        if not pfad:
            return

        with open(pfad, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Tag", "Datum", "Einstempeln", "Ausstempeln", "Stunden"])

            for info in zeilen:
                writer.writerow([
                    info["tag"],
                    info["datum"],
                    info["erste_ein"],
                    info["letzte_aus"],
                    info["stunden_text"]
                ])

            writer.writerow([])
            writer.writerow(["Gesamtstunden", "", "", "", self.sekunden_zu_zeittext(monat_sekunden)])

        messagebox.showinfo("Export fertig", f"CSV gespeichert:\n{pfad}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ArbeitszeitTracker(root)
    root.mainloop()