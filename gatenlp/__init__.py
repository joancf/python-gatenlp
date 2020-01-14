__version__ = "0.5"
import logging
try:
    import sortedcontainers
except Exception as ex:
    import sys
    print("ERROR: required package sortedcontainers cannot imported!", file=sys.stderr)
    print("Please install, using e.g. 'pip install -U sortedcontainers'", file=sys.stderr)
    sys.exit(1)
# TODO: check version of sortedcontainers (we have 2.1.0)
logging.basicConfig()
logger = logging.getLogger("gatenlp")
logger.setLevel(logging.INFO)

# this attribute globally holds the processing resource last defined
# so it can be used for interacting with the GATE python plugin
from gatenlp.gate_interaction import _pr_decorator as GateNlpPr
from gatenlp.gate_interaction import interact
from gatenlp.annotation import Annotation
from gatenlp.document import Document
from gatenlp.annotation_set import AnnotationSet
from gatenlp.exceptions import InvalidOffsetException
from gatenlp.changelog import ChangeLog

__all__ = ["GateNlpPr", "Annotation", "Document", "AnnotationSet",
           "InvalidOffsetException", "ChangeLog", "logger"]

gate_python_plugin_pr = None

