import csv
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
        self.root.geometry("1120x700")
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
            width=16,
            command=self.einstempeln
        ).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Pause starten",
            width=16,
            command=self.pause_starten
        ).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Pause beenden",
            width=16,
            command=self.pause_beenden
        ).grid(row=0, column=2, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Ausstempeln",
            width=16,
            command=self.ausstempeln
        ).grid(row=0, column=3, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Übersicht anzeigen",
            width=16,
            command=self.uebersicht_anzeigen
        ).grid(row=0, column=4, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Monatsstunden",
            width=16,
            command=self.monatsstunden_anzeigen
        ).grid(row=0, column=5, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="CSV exportieren",
            width=16,
            command=self.csv_exportieren
        ).grid(row=1, column=1, padx=5, pady=5)

        tk.Button(
            button_frame,
            text="PDF exportieren",
            width=16,
            command=self.pdf_exportieren
        ).grid(row=1, column=2, padx=5, pady=5)

        self.tree = ttk.Treeview(
            self.root,
            columns=("tag", "datum", "ein", "aus", "pause", "stunden"),
            show="headings",
            height=22
        )

        self.tree.heading("tag", text="Tag")
        self.tree.heading("datum", text="Datum")
        self.tree.heading("ein", text="Einstempeln")
        self.tree.heading("aus", text="Ausstempeln")
        self.tree.heading("pause", text="Pause")
        self.tree.heading("stunden", text="Arbeitsstunden")

        self.tree.column("tag", width=160, anchor="center")
        self.tree.column("datum", width=140, anchor="center")
        self.tree.column("ein", width=150, anchor="center")
        self.tree.column("aus", width=150, anchor="center")
        self.tree.column("pause", width=120, anchor="center")
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
        if self.letzte_aktion in ["EIN", "PAUSE_ENDE"]:
            self.status_label.config(text="Status: Eingestempelt", fg="green")
        elif self.letzte_aktion == "PAUSE_START":
            self.status_label.config(text="Status: In Pause", fg="orange")
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
        if self.letzte_aktion in ["EIN", "PAUSE_START", "PAUSE_ENDE"]:
            messagebox.showwarning("Warnung", "Du bist schon eingestempelt.")
            return

        self.eintrag_speichern("EIN")
        messagebox.showinfo("Gespeichert", "Einstempeln gespeichert.")
        self.uebersicht_anzeigen()

    def pause_starten(self):
        if self.letzte_aktion not in ["EIN", "PAUSE_ENDE"]:
            messagebox.showwarning("Warnung", "Du musst zuerst einstempeln.")
            return

        self.eintrag_speichern("PAUSE_START")
        messagebox.showinfo("Gespeichert", "Pause gestartet.")
        self.uebersicht_anzeigen()

    def pause_beenden(self):
        if self.letzte_aktion != "PAUSE_START":
            messagebox.showwarning("Warnung", "Es läuft gerade keine Pause.")
            return

        self.eintrag_speichern("PAUSE_ENDE")
        messagebox.showinfo("Gespeichert", "Pause beendet.")
        self.uebersicht_anzeigen()

    def ausstempeln(self):
        if self.letzte_aktion not in ["EIN", "PAUSE_ENDE"]:
            messagebox.showwarning("Warnung", "Du musst zuerst einstempeln oder die Pause beenden.")
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
        eintraege_sortiert = sorted(eintraege, key=lambda x: x[0])

        erste_ein = ""
        letzte_aus = ""
        arbeits_sekunden = 0
        pause_sekunden = 0

        arbeits_start = None
        pause_start = None

        for uhrzeit, aktion in eintraege_sortiert:
            zeit_obj = datetime.strptime(datum + " " + uhrzeit, "%Y-%m-%d %H:%M:%S")

            if aktion == "EIN":
                if erste_ein == "":
                    erste_ein = uhrzeit
                arbeits_start = zeit_obj

            elif aktion == "PAUSE_START":
                if arbeits_start is not None:
                    diff = (zeit_obj - arbeits_start).total_seconds()
                    if diff > 0:
                        arbeits_sekunden += diff
                arbeits_start = None
                pause_start = zeit_obj

            elif aktion == "PAUSE_ENDE":
                if pause_start is not None:
                    diff = (zeit_obj - pause_start).total_seconds()
                    if diff > 0:
                        pause_sekunden += diff
                pause_start = None
                arbeits_start = zeit_obj

            elif aktion == "AUS":
                letzte_aus = uhrzeit
                if arbeits_start is not None:
                    diff = (zeit_obj - arbeits_start).total_seconds()
                    if diff > 0:
                        arbeits_sekunden += diff
                arbeits_start = None
                pause_start = None

        datum_obj = datetime.strptime(datum, "%Y-%m-%d")
        tag_en = datum_obj.strftime("%A")
        tag_de = WOCHENTAGE.get(tag_en, tag_en)
        datum_text = datum_obj.strftime("%d.%m.%Y")

        return {
            "tag": tag_de,
            "datum": datum_text,
            "erste_ein": erste_ein if erste_ein else "-",
            "letzte_aus": letzte_aus if letzte_aus else "-",
            "pause_text": self.sekunden_zu_zeittext(pause_sekunden),
            "sekunden": int(arbeits_sekunden),
            "stunden_text": self.sekunden_zu_zeittext(arbeits_sekunden)
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
                    info["pause_text"],
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
            writer.writerow(["Tag", "Datum", "Einstempeln", "Ausstempeln", "Pause", "Arbeitsstunden"])

            for info in zeilen:
                writer.writerow([
                    info["tag"],
                    info["datum"],
                    info["erste_ein"],
                    info["letzte_aus"],
                    info["pause_text"],
                    info["stunden_text"]
                ])

            writer.writerow([])
            writer.writerow(["Gesamtstunden", "", "", "", "", self.sekunden_zu_zeittext(monat_sekunden)])

        messagebox.showinfo("Export fertig", f"CSV gespeichert:\n{pfad}")

    def pdf_exportieren(self):
        zeilen, monat_sekunden = self.monatsdaten()

        if not zeilen:
            messagebox.showwarning("Keine Daten", "Für diesen Monat gibt es keine Daten.")
            return

        aktueller_monat = datetime.now().strftime("%Y-%m")
        standard_name = f"arbeitszeiten_{aktueller_monat}.pdf"

        pfad = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=standard_name,
            filetypes=[("PDF-Dateien", "*.pdf")]
        )

        if not pfad:
            return

        doc = SimpleDocTemplate(pfad, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        titel = Paragraph(f"Arbeitszeiten {aktueller_monat}", styles["Title"])
        elements.append(titel)
        elements.append(Spacer(1, 12))

        table_data = [["Tag", "Datum", "Einstempeln", "Ausstempeln", "Pause", "Arbeitsstunden"]]

        for info in zeilen:
            table_data.append([
                info["tag"],
                info["datum"],
                info["erste_ein"],
                info["letzte_aus"],
                info["pause_text"],
                info["stunden_text"]
            ])

        table_data.append(["", "", "", "", "Gesamt", self.sekunden_zu_zeittext(monat_sekunden)])

        table = Table(table_data, repeatRows=1)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ]))

        elements.append(table)
        doc.build(elements)

        messagebox.showinfo("Export fertig", f"PDF gespeichert:\n{pfad}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ArbeitszeitTracker(root)
    root.mainloop()