from collections import namedtuple
import hashlib
import re
from pandas import read_csv

from PyQt5.QtWidgets import QMessageBox

# class _ReadOnlyProperty(object):
#     def __init__(self, value):
#         self.__value = value
    
#     def __get__(self, obj, objtype):
#         return self.__value

#     def __set__(self, obj, value):
#         return NotImplementedError("Cannot change a constant.")

# def __make_read_only(cls):
#     for k, v in cls.__dict__.items():
#         if not callable(getattr(cls, k)) and '__' not in k:
#             setattr(cls, k, _ReadOnlyProperty(v))
#     # def raise_err(self, attr, value):
#     #     raise NotImplementedError("Cannot add an attribute.")
#     # setattr(cls, '__setattr__', raise_err)
#     return cls

# @__make_read_only
class Constants(object):
    class Messages(object):
        NO_DB_AVAIL    = "No database available.\nGo to Updates->Update database."
        NO_DB          = "No database"
    DB_LOCATION        = "https://aresvalley.com/Storage/Artemis/Database/data.zip"
    REF_LOC            = "https://aresvalley.com/Storage/Artemis/Database/data.zip.log"
    DB_NAME            = "db.csv"
    DB_NAMES           = ("name",
                          "inf_freq",
                          "sup_freq",
                          "mode",
                          "inf_band",
                          "sup_band",
                          "location",
                          "url",
                          "description",
                          "modulation",
                          "category_code",
                          "acf",)
    DB_WIKI_CLICKED    = "url_clicked"
    DB_STRINGS         = ('inf_freq',
                          'sup_freq',
                          'mode',
                          'inf_band',
                          'sup_band',
                          'category_code',)
    DATA_FOLDER        = "Data"
    SPECTRA_FOLDER     = "Spectra"
    SPECTRA_EXT        = ".png"
    AUDIO_FOLDER       = "Audio"
    THEMES_FOLDER      = "themes"
    THEME_EXTENSION    = ".th"
    ICONS_FOLDER       = "icons"
    DEFAULT_THEME      = "1-system"
    CURRENT_THEME      = ".current_theme"
    THEME_COLORS       = "colors.txt"
    NOT_AVAILABLE      = "spectrumnotavailable.png"
    NOT_SELECTED       = "nosignalselected.png"
    SEARCH_LABEL_IMG   = "search_icon.png"
    VOLUME_LABEL_IMG   = "volume.png"
    __Band             = namedtuple("Band", ["lower", "upper"])
    __ELF              = __Band(0, 30) # Formally it is (3, 30) Hz.
    __SLF              = __Band(30, 300)
    __ULF              = __Band(300, 3000)
    __VLF              = __Band(3000, 30000)
    __LF               = __Band(30 * 10**3, 300 * 10**3)
    __MF               = __Band(300 * 10 ** 3, 3000 * 10**3)
    __HF               = __Band(3 * 10**6, 30 * 10**6)
    __VHF              = __Band(30 * 10**6, 300 * 10**6)
    __UHF              = __Band(300 * 10**6, 3000 * 10**6)
    __SHF              = __Band(3 * 10**9, 30 * 10**9)
    __EHF              = __Band(30 * 10**9, 300 * 10**9)
    BANDS              = (__ELF, __SLF, __ULF, __VLF, __LF, __MF, __HF, __VHF, __UHF, __SHF, __EHF)
    ACTIVE_COLOR       = "#39eaff"
    INACTIVE_COLOR     = "#9f9f9f"
    CONVERSION_FACTORS = {"Hz" : 1, 
                          "kHz": 1000, 
                          "MHz": 1000000, 
                          "GHz": 1000000000}
    MODES              = {"FM": ("NFM", "WFM"),
                          "AM": (),
                          "CW": (),
                          "SK": ("FSK", "PSK", "MSK"),
                          "SB": ("LSB", "USB", "DSB"),
                          "Chirp Spread Spectrum": (),
                          "FHSS-TDM": (),
                          "RAW": (),
                          "SC-FDMA": (),}
    APPLY              = "Apply"
    REMOVE             = "Remove"
    UNKNOWN            = "N/A"
    MODULATIONS        = ("8VSB",
                          "AFSK",
                          "AM",
                          "BFSK",
                          "C4FM",
                          "CDMA",
                          "COFDM",
                          "CW",
                          "FFSK",
                          "FM",
                          "FMCW",
                          "FMOP",
                          "FSK",
                          "GFSK",
                          "GMSK",
                          "IFK",
                          "MFSK",
                          "MSK",
                          "OFDM",
                          "OOK",
                          "PAM",
                          "PPM",
                          "PSK",
                          "QAM",
                          "TDMA",)
    LOCATIONS          = (UNKNOWN,
                          "Australia",
                          "Canada",
                          "Central Europe",
                          "China",
                          "Cyprus",
                          "Eastern Europe",
                          "Europe",
                          "Europe, japan and Asia",
                          "Exmouth, Australia",
                          "Finland",
                          "France",
                          "Germany",
                          "Home Base Mobile , AL",
                          "Hungary",
                          "Iran",
                          "Israel",
                          "Japan",
                          "LaMour, North Dakota",
                          "Lualualei, Hawaii",
                          "North America",
                          "North Korea",
                          "Poland",
                          "Romania",
                          "Ruda, Sweden",
                          "UK",
                          "United Kingdom",
                          "United States",
                          "Varberg, Sweden",
                          "World Wide",
                          "Worldwide",)

# Constants = __Constants()

def reset_apply_remove_btn(button):
    if button.isChecked():
        button.setChecked(False)
        button.clicked.emit()

def throwable_message(cls, title, text, connection = None):
    msg = QMessageBox(cls)
    msg.setWindowTitle(title)
    msg.setText(text)
    if connection:
        msg.setText(text).finished.connect(connection)
    return msg

def checksum_ok(data, what):
    code = hashlib.sha256()
    code.update(data)
    if what == "folder":
        n = 0
    elif what == "db":
        n = 1
    else:
        raise ValueError("Wrong entry name.")
    try:
        reference = read_csv(Constants.REF_LOC, delimiter = '*').iat[-1, n]
    except HTTPError:
        return False
    return code.hexdigest() == reference

def is_valid_html_color(color):
    return bool(re.match("#([a-zA-Z0-9]){6}", color))
