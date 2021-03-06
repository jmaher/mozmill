import unittest
import os
import sys
import subprocess
from time import sleep

from mozprocess import processhandler

# This tests specifically the case reported in bug 671316
# TODO: Because of the way mutt works we can't just load a utils.py in here.
#       so, for all process handler tests, copy these two 
#       utility functions to to the top of your source.

def make_proclaunch(aDir):
    """ 
        Makes the proclaunch executable.  
        Params: 
            aDir - the directory in which to issue the make commands
        Returns:
            the path to the proclaunch executable that is generated
    """
    p = subprocess.Popen(["make"], shell=True, cwd=aDir)
    p.communicate()
    if sys.platform == "win32":
        exepath = os.path.join(aDir, "proclaunch.exe")
    else:
        exepath = os.path.join(aDir, "proclaunch")
    return exepath

def check_for_process(processName):
    """
        Use to determine if process is still running.
        
        Returns:
        detected -- True if process is detected to exist, False otherwise
        output -- if process exists, stdout of the process, '' otherwise
    """
    output = ''
    if sys.platform == "win32":
        # On windows we use tasklist
        p1 = subprocess.Popen(["tasklist"], stdout=subprocess.PIPE)
        output = p1.communicate()[0]
        detected = False
        for line in output:
            if processName in line:
                detected = True
                break
    else:
        p1 = subprocess.Popen(["ps", "-A"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", processName], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        output = p2.communicate()[0]
        detected = False
        for line in output:
            if "grep %s" % processName in line:
                continue
            elif processName in line:
                detected = True
                break

    return detected, output

class ProcTest2(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        
        # Ideally, I'd use setUpClass but that only exists in 2.7.
        # So, we'll do this make step now.
        self.proclaunch = make_proclaunch(os.path.dirname(__file__))
        unittest.TestCase.__init__(self, *args, **kwargs)
        
    def test_process_waittimeout(self):
        """ Process is started, runs to completion before our wait times out
        """
        p = processhandler.ProcessHandler([self.proclaunch,
                                          "process_waittimeout_10s.ini"],
                                          cwd=os.path.dirname(__file__))
        p.run()
        p.waitForFinish(timeout=30)

        detected, output = check_for_process(self.proclaunch)
        self.determine_status(detected,
                              output,
                              p.proc.returncode,
                              p.didTimeout)

    def test_process_waitnotimeout(self):
        """ Process is started runs to completion while we wait indefinitely
        """

        p = processhandler.ProcessHandler([self.proclaunch,
                                          "process_waittimeout_10s.ini"],
                                          cwd=os.path.dirname(__file__))
        p.run()
        p.waitForFinish()
        
        detected, output = check_for_process(self.proclaunch)
        self.determine_status(detected, 
                              output, 
                              p.proc.returncode, 
                              p.didTimeout)

    def determine_status(self, 
                         detected=False,
                         output = '',
                         returncode = 0,
                         didtimeout = False,
                         isalive=False,
                         expectedfail=[]):
        """
        Use to determine if the situation has failed. 
        Parameters:
            detected -- value from check_for_process to determine if the process is detected
            output -- string of data from detected process, can be ''
            returncode -- return code from process, defaults to 0
            didtimeout -- True if process timed out, defaults to False
            isalive -- Use True to indicate we pass if the process exists; however, by default
                       the test will pass if the process does not exist (isalive == False)
            expectedfail -- Defaults to [], used to indicate a list of fields that are expected to fail
        """
        if 'returncode' in expectedfail:
            self.assertTrue(returncode, "Detected an expected non-zero return code")
        else:
            self.assertTrue(returncode == 0, "Detected non-zero return code of: %d" % returncode)

        if 'didtimeout' in expectedfail:
            self.assertTrue(didtimeout, "Process timed out as expected")
        else:
            self.assertTrue(not didtimeout, "Detected that process timed out")

        if detected:
            self.assertTrue(isalive, "Detected process is still running, process output: %s" % output)
        else:
            self.assertTrue(not isalive, "Process ended")
