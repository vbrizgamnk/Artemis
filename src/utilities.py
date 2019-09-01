from functools import partial
import hashlib
import sys
import os
from PyQt5.QtWidgets import QMessageBox
import urllib3
from constants import Constants, Signal, Database, ChecksumWhat


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def uncheck_and_emit(button):
    """Set the button to the unchecked state and emit the clicked signal."""
    if button.isChecked():
        button.setChecked(False)
        button.clicked.emit()


def show_matching_strings(list_elements, text):
    """Show all elements of QListWidget that matches (even partially) a target text.

    Arguments:
    list_elements -- the QListWidget
    text -- the target text."""
    for index in range(list_elements.count()):
        item = list_elements.item(index)
        if text.lower() in item.text().lower() or item.isSelected():
            item.setHidden(False)
        else:
            item.setHidden(True)


def get_field_entries(db_entry, separator=Constants.FIELD_SEPARATOR):
    """Take a database entry and optionally a separator string.

    Return a list obtained by splitting the signal field with separator."""
    return [
        x.strip() for x in db_entry.split(separator)
    ]


def pop_up(cls, title, text,
           informative_text=None,
           connection=None,
           is_question=False,
           default_btn=QMessageBox.Yes):
    """Return a QMessageBox object.

    Keyword arguments:
    informative_text -- possible informative text to be displayed.
    connection -- a callable to connect the message when emitting the finished signal.
    is_question -- whether the message contains a question.
    default_btn -- the default button for the possible answer to the question."""
    msg = QMessageBox(cls)
    msg.setWindowTitle(title)
    msg.setText(text)
    if informative_text:
        msg.setInformativeText(informative_text)
    if connection:
        msg.finished.connect(connection)
    if is_question:
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(default_btn)
    msg.adjustSize()
    return msg


def is_mac_os():
    """Return True if running OS is Mac."""
    return sys.platform == 'darwin'


def get_cacert_file():
    """Return the path to the cacert.pem file."""
    if hasattr(sys, "_MEIPASS"):
        ca_certs = os.path.join(sys._MEIPASS, 'cacert.pem')
    else:
        ca_certs = 'cacert.pem'
    return ca_certs


def get_pool_manager():
    """Return a urllib3.PoolManager object."""
    return urllib3.PoolManager(ca_certs=get_cacert_file())


def checksum_ok(data, what):
    """Check whether the checksum of the 'data' argument is correct."""
    code = hashlib.sha256()
    code.update(data)
    if what is ChecksumWhat.FOLDER:
        n = 0
    elif what is ChecksumWhat.DB:
        n = 1
    else:
        raise ValueError("Wrong entry name.")
    try:
        # The downloaded file is a csv file with columns (last version == last line):
        # data.zip_SHA256 | db.csv_SHA256 | Version | Creation_date
        reference = get_pool_manager().request(
            'GET',
            Database.LINK_REF,
            timeout=4.0
        ).data.decode("utf-8").splitlines()[-1].split(Database.DELIMITER)[n]
    except Exception:
        raise
    return code.hexdigest() == reference


def connect_events_to_func(events_to_connect, fun_to_connect, fun_args):
    """Connect all elements of events_to_connect to the callable fun_to_connect.

    fun_args is a list of fun_to_connect arguments."""
    if fun_args is not None:
        for event in events_to_connect:
            event.connect(partial(fun_to_connect, *fun_args))
    else:
        for event in events_to_connect:
            event.connect(fun_to_connect)


def filters_limit(spinbox, filter_unit, confidence, sign=1):
    """Return the actual limit of a numerical filter."""
    band_filter = spinbox.value() * Constants.CONVERSION_FACTORS[filter_unit.currentText()]
    return band_filter + sign * (confidence.value() * band_filter) // 100


def is_undef_freq(current_signal):
    """Return whether the lower or upper frequency of a signal is undefined."""
    lower_freq = current_signal.at[Signal.INF_FREQ]
    upper_freq = current_signal.at[Signal.SUP_FREQ]
    return lower_freq == Constants.UNKNOWN or upper_freq == Constants.UNKNOWN


def is_undef_band(current_signal):
    """Return whether the lower or upper band of a signal is undefined."""
    lower_band = current_signal.at[Signal.INF_BAND]
    upper_band = current_signal.at[Signal.SUP_BAND]
    return lower_band == Constants.UNKNOWN or upper_band == Constants.UNKNOWN


def _change_unit(str_num):
    """Return a scale factor given the number of digits of a numeric string."""
    digits = len(str_num)
    if digits < 4:
        return 1
    elif digits < 7:
        return 1000
    elif digits < 10:
        return 10**6
    else:
        return 10**9


def format_numbers(lower, upper):
    """Return the string which displays the numeric limits of a filter."""
    units = {1: 'Hz', 1000: 'kHz', 10**6: 'MHz', 10**9: 'GHz'}
    lower_factor = _change_unit(lower)
    upper_factor = _change_unit(upper)
    pre_lower = lower
    pre_upper = upper
    lower = safe_cast(lower, int) / lower_factor
    upper = safe_cast(upper, int) / upper_factor
    if lower.is_integer():
        lower = int(lower)
    else:
        lower = round(lower, 2)
    if upper.is_integer():
        upper = int(upper)
    else:
        upper = round(upper, 2)
    if pre_lower != pre_upper:
        return f"{lower:,} {units[lower_factor]} - {upper:,} {units[upper_factor]}"
    else:
        return f"{lower:,} {units[lower_factor]}"


def safe_cast(value, cast_type, default=-1):
    """Call 'cast_type(value)' and return the result.

    If the operation fails return 'default'.
    Should be used to perform 'safe casts'.
    Keyword argument:
    default -- default value returned if the cast fails.
    """
    try:
        r = cast_type(value)
    except Exception:
        r = default
    finally:
        return r
