import shutil
import tempfile

from twisted.internet.utils import getProcessOutputAndValue


class InvalidGPGSignature(Exception):
    """Raised when the gpg signature for a given file is invalid."""


def gpg_verify(filename, signature, gpg="/usr/bin/gpg"):
    """Verify the GPG signature of a file.

    @param filename: Path to the file to verify the signature against.
    @param signature: Path to signature to use.
    @param gpg: Optionally, path to the GPG binary to use.
    @return: a C{Deferred} resulting in C{True} if the signature is
            valid, C{False} otherwise.
        """

    def remove_gpg_home(ignored):
        shutil.rmtree(gpg_home)
        return ignored

    def check_gpg_exit_code((out, err, code)):
        if code != 0:
            raise InvalidGPGSignature("%s failed (out='%s', err='%s', "
                                      "code='%d')" % (gpg, out, err, code))

    gpg_home = tempfile.mkdtemp()
    args = ("--no-options", "--homedir", gpg_home, "--no-default-keyring",
            "--ignore-time-conflict", "--keyring", "/etc/apt/trusted.gpg",
            "--verify", signature, filename)

    result = getProcessOutputAndValue(gpg, args=args)
    result.addBoth(remove_gpg_home)
    result.addCallback(check_gpg_exit_code)
    return result
