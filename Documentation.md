

# Introduction #

The most important place for documentation is in docstrings in the code itself. Every module, class, and public member should have a docstring to specify its purpose and usage.

# Online documentation #

Every night, the documentation is generated for all open branches in the three repositories. This documentation is available at

http://amcat.vu.nl/api

# What to include #

http://www.python.org/dev/peps/pep-0257/ contains some general guidelines on what (not) to include in a docstring.

DON't include:
  * Things that are part of the signature, ie don't include the argument names, superclass, complete member lists etc.

DO include:
  * The purpose and usage of a member
  * Everything that is part of the interface contract, ie what kind of input is expected (type and/or description), what kind of output is expected, what kind of errors will be thrown that one might wish to catch

Often, a module contains a single (main) class, and the documentation of the module can overlap with the class. In that case, document the purpose and general usage in the module docstring and point to the main class for more details.

For model classes, briefly state what the model represents in the real world.

# Format #

The current documentation is in epytext. We are considering moving to something that produces prettier output.

# Compliance #

Note that the pylint-based UnitTests checks whether all public members have docstrings.