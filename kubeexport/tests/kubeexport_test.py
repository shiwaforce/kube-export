import sys
import unittest
from contextlib import contextmanager
import kubeexport.kubeexport as kubeexport
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class ProcoTestSuite(unittest.TestCase):

    def test_without_command(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_command('-h')
            self.assertIsNotNone(context.exception)
        self.assertIn(kubeexport.__doc__.strip(), out.getvalue().strip())

    @contextmanager
    def captured_output(self):
        new_out, new_err = StringIO(), StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = new_out, new_err
            yield sys.stdout, sys.stderr
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def run_command(self, *args):
        runnable = kubeexport.Kubexport(argv=list(args))
        runnable.start()
