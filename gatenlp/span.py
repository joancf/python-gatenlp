"""
Module for Span class
"""
from functools import total_ordering
from gatenlp.utils import support_annotation_or_set


@total_ordering
# class Span(namedtuple("Span", ["start", "end"])):
# NOTE: we cannot use structlcass, since that does not work with wrapping the init method so
# we can create a span from an annotation.
# class Span(structclass("Span", ("start", "end"))):
# Instead, we simply use slots for now.
class Span:

    __slots__ = ["start", "end"]

    @support_annotation_or_set
    def __init__(self, start, end):
        assert start is not None
        assert end is not None
        self.start = start
        self.end = end

    def __eq__(self, other) -> bool:
        if not isinstance(other, Span):
            return False
        if self is other:
            return True
        return self.start == other.start and self.end == other.end

    def __lt__(self, other) -> bool:
        if not isinstance(other, Span):
            raise Exception("Cannot compare to non-Annotation")
        if self.start < other.start:
            return True
        elif self.start > other.start:
            return False
        else:
            return self.end < other.end

    def __repr__(self) -> str:
        return f"Span({self.start},{self.end})"

    @property
    def length(self) -> int:
        return self.end - self.start

    @support_annotation_or_set
    def isoverlapping(self, start: int, end: int) -> bool:
        """
        Checks if this span is overlapping with the given span, annotation or
        annotation set.
        An annotation is overlapping with a span if the first or last character
        is inside that span.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span

        Returns:
          `True` if overlapping, `False` otherwise

        """
        return self.iscovering(start) or self.iscovering(end - 1)

    @support_annotation_or_set
    def iscoextensive(self, start: int, end: int) -> bool:
        """
        Checks if this span is coextensive with the given span, annotation or
        annotation set, i.e. has exactly the same start and end offsets.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span

        Returns:
          `True` if coextensive, `False` otherwise

        """
        return self.start == start and self.end == end

    @support_annotation_or_set
    def iswithin(self, start: int, end: int) -> bool:
        """
        Checks if this span is within the given span, annotation or
        annotation set, i.e. both the start and end offsets of this annotation
        are after the given start and before the given end.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span

        Returns:
          `True` if within, `False` otherwise

        """
        return start <= self.start and end >= self.end

    @support_annotation_or_set
    def isbefore(self, start: int, end: int, immediately=False) -> bool:
        """
        Checks if this span is before the other span, i.e. the end of this annotation
        is before the start of the other annotation or span.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span
          immediately: if true checks if this annotation ends immediately before the other one (Default value = False)

        Returns:
          True if before, False otherwise

        """
        if immediately:
            return self.end == start
        else:
            return self.end <= start

    @support_annotation_or_set
    def isafter(self, start: int, end: int, immediately=False) -> bool:
        """
        Checks if this span is after the other span, i.e. the start of this annotation
        is after the end of the other annotation or span.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span
          immediately: if true checks if this annotation starts immediately after the other one (Default value = False)

        Returns:
          True if after, False otherwise

        """
        if immediately:
            return self.start == end
        else:
            return self.start >= end

    @support_annotation_or_set
    def gap(self, start: int, end: int):
        """
        Return the gep between this span and the other span. This is the distance between
        the last character of the first span and the first character of the second span in
        sequence, so it is always independent of the order of the two span.

        This is negative if the spans overlap.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of span
          end: end offset of span

        Returns:
          size of gap

        """
        if self.start < start:
            ann1start = self.start
            ann1end = self.end
            ann2start = start
            ann2end = end
        else:
            ann2start = self.start
            ann2end = self.end
            ann1start = start
            ann1end = end
        return ann2start - ann1end

    @support_annotation_or_set
    def iscovering(self, start, end=None) -> bool:
        """
        Checks if this span is covering the given span, annotation or
        annotation set, i.e. both the given start and end offsets
        are after the start of this span and before the end of this span.

        If end is not given, then the method checks if start is an offset of a character
        contained in the span.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span

        Returns:
          True if covering, False otherwise

        """
        if end is None:
            if self.start == self.end:
                return self.start == start
            else:
                return self.start <= start < self.end
        else:
            return self.start <= start and self.end >= end

    @support_annotation_or_set
    def isstartingat(self, start: int, end: int) -> bool:
        """
        Check if this span is starting at the same offset as the other span or annotation.

        Args:
            start: start of other span/annotaiton
            end: end of other span/annotation, ignored

        Returns:
            True if span is starting at the same offset as the other span or annotation

        """
        return self.start == start

    @support_annotation_or_set
    def isendingwith(self, start: int, end: int) -> bool:
        """
        Checks if this span is ending at the same offset as the given span or annotation.

        Args:
            start: start of the span (ignored)
            end: end of the span

        Returns:
            True if ending at the same offset as the span or annotation

        """
        return self.end == end

    @support_annotation_or_set
    def isleftoverlapping(self, start: int, end: int) -> bool:
        """
        Checks if this span is overlapping with the given span, annotation or
        annotation set on the left, i.e. the last character is inside the span and the
        first character is before the span.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span

        Returns:
          `True` if left-overlapping, `False` otherwise

        """
        return self.start <= start and self.end <= end

    @support_annotation_or_set
    def isrightoverlapping(self, start: int, end: int) -> bool:
        """
        Checks if this span is overlapping with the given span, annotation or
        annotation set on the right, i.e. the first character is inside the span.

        Note: this can be called with an Annotation or AnnotationSet instead of `start` and `end`
          (see gatenlp._utils.support_annotation_or_set)

        Args:
          start: start offset of the span
          end: end offset of the span

        Returns:
          `True` if right-overlapping, `False` otherwise

        """
        return self.start >= start and self.end >= end
