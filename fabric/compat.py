import six
import sys

filter_ = filter
map_ = map


def filter(*args, **kwargs):
    return list(filter_(*args, **kwargs))


def map(*args, **kwargs):
    return list(map_(*args, **kwargs))


try:

    from contextlib import nested

except ImportError:

    from contextlib import contextmanager

    # backported from python 2.7
    @contextmanager
    def nested(*managers):
        """Combine multiple context managers into a single nested context manager.

       This function has been deprecated in favour of the multiple manager form
       of the with statement.

       The one advantage of this function over the multiple manager form of the
       with statement is that argument unpacking allows it to be
       used with a variable number of context managers as follows:

          with nested(*managers):
              do_something()

        """
        exits = []
        vars = []
        exc = (None, None, None)
        try:
            for mgr in managers:
                exit = mgr.__exit__
                enter = mgr.__enter__
                vars.append(enter())
                exits.append(exit)
            yield vars
        except:
            exc = sys.exc_info()
        finally:
            while exits:
                exit = exits.pop()
                try:
                    if exit(*exc):
                        exc = (None, None, None)
                except:
                    exc = sys.exc_info()
            if exc != (None, None, None):
                # Don't rely on sys.exc_info() still containing
                # the right information. Another exception may
                # have been raised and caught by an exit method
                raise six.reraise(*exc)

try:
    from contextlib import suppress
except ImportError:
    # backported from python 3.4
    class suppress:
    """Context manager to suppress specified exceptions

    After the exception is suppressed, execution proceeds with the next
    statement following the with statement.

         with suppress(FileNotFoundError):
             os.remove(somefile)
         # Execution still resumes here if the file was already removed
    """

    def __init__(self, *exceptions):
        self._exceptions = exceptions

    def __enter__(self):
        pass

    def __exit__(self, exctype, excinst, exctb):
        # Unlike isinstance and issubclass, CPython exception handling
        # currently only looks at the concrete type hierarchy (ignoring
        # the instance and subclass checking hooks). While Guido considers
        # that a bug rather than a feature, it's a fairly hard one to fix
        # due to various internal implementation details. suppress provides
        # the simpler issubclass based semantics, rather than trying to
        # exactly reproduce the limitations of the CPython interpreter.
        #
        # See http://bugs.python.org/issue12029 for more details
        return exctype is not None and issubclass(exctype, self._exceptions)
