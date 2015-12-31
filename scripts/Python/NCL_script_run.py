""" NCL_script_run
All NCL scripts are run through this command, which manages logging
"""

import shlex
from subprocess import Popen, PIPE
import WhfLog

def run(cmd):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    Parameters
    ----------
    cmd : str
       The NCL command
    Returns 
    -------
    int:  exitcode
    """

    # log the command prior to doing anything
    WhfLog.debug_ncl(cmd)

    # do the command in a way where stdout and stderr can be grabbed as strings
    args = shlex.split(cmd)
    proc = Popen(args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode

    if err:
        # Log errors PRIOR to logging output
        WhfLog.error_ncl(err)
    if out:
        # Go ahead and log the output, which is usually some big multiline string
        WhfLog.debug_ncl(out)

    # return the exit code, for those who want to know
    return exitcode

    
