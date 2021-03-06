import asyncio
import pytest
import subprocess
from textwrap import dedent
from simpervisor import atexitasync 
import sys
import signal
import os
import time


@pytest.mark.parametrize('signum, handlercount', [
    (signal.SIGTERM, 1), (signal.SIGINT, 1),
    (signal.SIGTERM, 5), (signal.SIGINT, 5),
])
def test_atexitasync(signum, handlercount):
    """
    Test signal handlers receive signals properly
    """
    signalprinter_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'child_scripts',
        'signalprinter.py'
    )
    proc = subprocess.Popen([sys.executable, signalprinter_file, str(handlercount)], stdout=subprocess.PIPE)

    # Give the process time to register signal handlers
    time.sleep(0.5)
    proc.send_signal(signum)

    # Make sure the signal is handled by our handler in the code
    stdout, stderr = proc.communicate()
    expected_output = '\n'.join([
        'handler {} received {}'.format(i, signum)
        for i in range(handlercount)
    ]) + '\n'

    assert stdout.decode() == expected_output

    # The code should exit cleanly
    retcode = proc.wait()
    assert retcode == 0
