
"""
manage the user folder
"""

__all__ = [
    "matchUserInApsbss",
    "newUser",
    "techniqueSubdirectory"
]

from ..session_logs import logger
logger.info(__file__)

from ..devices import apsbss as apsbss_object
from ..devices import user_data
from ..framework import RE
from ..framework import specwriter
from .check_file_exists import filename_exists
from apstools.utils import cleanupText
import apstools.beamtime.apsbss
import datetime
import os
import pyRestTable


APSBSS_SECTOR = "09"
APSBSS_BEAMLINE = "9-ID-B,C"


def _pick_esaf(user, now, cycle):
    """
    Pick the first matching ESAF

    Criteria:

    * match user name
    * has not yet expired
    * earliest start

    RETURNS

    esaf_id or None
    """
    def esafSorter(obj):
        return obj["experimentStartDate"]

    get_esafs = apstools.beamtime.apsbss.getCurrentEsafs
    esafs = [
        esaf["esafId"]
        for esaf in sorted(get_esafs(APSBSS_SECTOR), key=esafSorter)
        # pick those that have not yet expired
        if esaf["experimentEndDate"] > now
        # and match user last name
        if user in [
            entry["lastName"]
            for entry in esaf["experimentUsers"]
        ]
    ]

    if len(esafs) == 0:
        logger.warning(
            "No unexpired ESAFs found that match user %s",
            user
        )
        return None
    elif len(esafs) > 1:
        logger.warning(
            "ESAF(s) %s match user %s at this time, picking first one",
            str(esafs), user)

    return str(esafs[0])


def _pick_proposal(user, now, cycle):
    """
    Pick the first matching proposal

    Criteria:

    * match user name
    * has not yet expired
    * earliest start

    RETURNS

    proposal_id or None
    """
    def proposalSorter(obj):
        return obj["startTime"]

    get_proposals = apstools.beamtime.apsbss.api_bss.listProposals
    proposals = [
        p["id"]
        for p in sorted(
            get_proposals(beamlineName=APSBSS_BEAMLINE, runName=cycle),
            key=proposalSorter
            )
        # pick those that have not yet expired
        if p["endTime"] > now
        # and match user last name
        if user in [
            entry["lastName"]
            for entry in p["experimenters"]
        ]
    ]

    if len(proposals) == 0:
        logger.warning(
            "No unexpired proposals found that match user %s",
            user
        )
        return None
    elif len(proposals) > 1:
        logger.warning(
            "proposal(s) %s match user %s at this time, picking first one",
            str(proposals), user)

    return str(proposals[0])


def _apsbss_summary_table(apsbss_object):
    """return a table of apsbss local PVs"""
    contents = {
        "ESAF number" : apsbss_object.esaf.esaf_id,
        "ESAF title" : apsbss_object.esaf.title,
        "ESAF names" : apsbss_object.esaf.user_last_names,
        "ESAF start" : apsbss_object.esaf.start_date,
        "ESAF end" : apsbss_object.esaf.end_date,
        "Proposal number" : apsbss_object.proposal.proposal_id,
        "Proposal title" : apsbss_object.proposal.title,
        "Proposal names" : apsbss_object.proposal.user_last_names,
        "Proposal start" : apsbss_object.proposal.start_date,
        "Proposal end" : apsbss_object.proposal.end_date,
        "Mail-in flag" : apsbss_object.proposal.mail_in_flag,
    }
    table = pyRestTable.Table()
    table.labels="key value PV".split()
    for k, v in contents.items():
        table.addRow((k, v.get(), v.pvname))

    return table


def matchUserInApsbss(user):
    """
    pull information from apsbss matching on user name and date
    """
    dt = datetime.datetime.now()
    now = str(dt)
    cycle = apstools.beamtime.apsbss.getCurrentCycle()

    esaf_id = _pick_esaf(user, now, cycle)
    proposal_id = _pick_proposal(user, now, cycle)

    if esaf_id is not None or proposal_id is not None:
        # update the local apsbss PVs
        logger.info("ESAF %s", esaf_id)
        logger.info("Proposal %s", proposal_id)

        prefix = apsbss_object.prefix
        apstools.beamtime.apsbss.epicsSetup(
            prefix,
            APSBSS_BEAMLINE,
            cycle
            )
        apstools.beamtime.apsbss.epicsClear(prefix)

        apsbss_object.esaf.esaf_id.put(esaf_id or "")
        apsbss_object.proposal.proposal_id.put(proposal_id or "")

        logger.info("APSBSS PVs updated from APS Oracle databases.")
        apstools.beamtime.apsbss.epicsUpdate(prefix)

        table = _apsbss_summary_table(apsbss_object)
        logger.info("ESAF & Proposal Overview:\n%s", str(table))
    else:
        logger.warning("APSBSS not updated.")
    logger.warning(
        "You should check that PVs in APSBSS contain correct information.")


def _setSpecFileName(path, scan_id=1):
    """
    SPEC file name
    """
    stub = os.path.basename(path)
    # TODO: full path?
    fname = f"{stub}.dat"
    if filename_exists(fname):
        logger.warning(">>> file already exists: %s <<<", fname)
        specwriter.newfile(fname, RE=RE)
        handled = "appended"
    else:
        specwriter.newfile(fname, scan_id=scan_id, RE=RE)
        handled = "created"
    logger.info(f"SPEC file name : {specwriter.spec_filename}")
    logger.info(f"File will be {handled} at end of next bluesky scan.")


def newUser(user, scan_id=1, month=None, day=None):
    """
    setup for a new user

    Create (if necessary) new user directory in
    current working directory with month, day, and
    given user name as shown in the following table.
    Each technique (SAXS, USAXS, WAXS) will be
    reponsible for creating its subdirectory
    as needed.

    ======================  ========================
    purpose                 folder
    ======================  ========================
    user data folder base   <CWD>/MM_DD_USER
    SPEC data file          <CWD>/MM_DD_USER/MM_DD_USER.dat
    AD folder - SAXS        <CWD>/MM_DD_USER/MM_DD_USER_saxs/
    folder - USAXS          <CWD>/MM_DD_USER/MM_DD_USER_usaxs/
    AD folder - WAXS        <CWD>/MM_DD_USER/MM_DD_USER_waxs/
    ======================  ========================
    """
    global specwriter

    dt = datetime.datetime.now()
    month = month or dt.month
    day = day or dt.day

    clean = cleanupText(user)
    stub = f"{month:02d}_{day:02d}_{clean}"
    path = os.path.join(os.getcwd(), stub)

    if not os.path.exists(path):
        logger.info("Creating user directory: %s", path)
        os.mkdir(path)
    user_data.user_dir.put(path)    # set in the PV

    # SPEC file name
    _setSpecFileName(path, scan_id=scan_id)

    matchUserInApsbss(user)     # update ESAF & Proposal, if available

    return path


def techniqueSubdirectory(technique):
    """
    Create a technique-based subdirectory per table in ``newUser()``.

    NOTE: Assumes CWD is now the directory returned by ``newFile()``
    """
    pwd = os.getcwd()
    stub = os.path.basename(pwd)
    path = os.path.join(pwd, f"{stub}_{technique}")

    if not os.path.exists(path):
        logger.info("Creating technique directory: %s", path)
        os.mkdir(path)

    return path
