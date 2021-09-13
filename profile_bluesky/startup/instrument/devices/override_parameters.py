"""
user reconfiguration of various USAXS parameters
"""

__all__ = [
    "user_override",
]

from ..session_logs import logger

logger.info(__file__)


class UserOverride:
    """
    Define parameters that can be overriden from a user configuration file.

    To add additional parameter names that a user might override, define
    the new name in the reset() method as for ``usaxs_minstep``.  Refer to
    ``plans.axis_tuning`` for example back-end handling.  Such as::

        minstep = user_override.pick("usaxs_minstep", 0.000045)

    In the ``BS_conf.py`` file, import the `user_override`` object::

        from instrument.devices import user_override

    and then override the attribute(s) as desired::

        user_override.usaxs_minstep = 1.0e-5

    To clear all the override parameters, call ``user_override.reset()``.
    To remove a specific override (and regain the default setting used
    by the plan), set the value to ``user_override.undefined``, such as:
    ``user_override.usaxs_minstep = user_override.undefined``.
    """

    def __init__(self):
        # ALWAYS use ``user_override.undefined`` for comparisons and resets.
        self.undefined = object()

        self.reset()

    def reset(self):
        """
        Change all override values back to undefined.
        """

        # used in instrument.plans.axis_tuning.instrument_default_tune_ranges
        self.usaxs_minstep = self.undefined

    def pick(self, parameter, default):
        """
        Either pick the override parameter value if defined, or the default.
        """
        try:
            obj = getattr(self, parameter)
            if obj != self.undefined:
                return obj
        except:
            pass
        return default


user_override = UserOverride()
