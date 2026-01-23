from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, List, TypeVar, Optional

from qnet.ir import Context, Operation, Location

from qoala.utils.debug_info import DebugInfo

_T = TypeVar("_T")


@dataclass(init=False)
class QoalaCompilable(ABC):
    @abstractmethod
    def compile(self, ctx: Context, location: Optional[Location] = None) -> None:
        """
        Compiles the operation,

        Parameters
        ----------
        ctx: Context
            The QNet Context object for creating QNet instructions.
        location: Optional[Location]
            A location object to be used as the location in the original file by the
            operations generated. Implementations of this method might ignore the
            value passed here.
        """
        pass


@dataclass(init=False)
class QoalaExpression(QoalaCompilable, ABC):
    _ir_vals: List[Operation]
    _containing_block: "QoalaBlock"  # type: ignore[name-defined]
    debug_info: DebugInfo

    def __init__(self):
        self._ir_vals = []

    @property
    def ir_value(self) -> Operation | None:
        if len(self._ir_vals) <= 0:
            return None
        # We return the "most recent" value for this expression
        return self._ir_vals[-1]

    @ir_value.setter
    def ir_value(self, new_ir_val: Operation) -> None:
        self._ir_vals.append(new_ir_val)

    @property
    def ir_values(self) -> List[Operation]:
        return self._ir_vals

    @property
    def qoala_block(self) -> "QoalaBlock":  # type: ignore[name-defined]
        return self._containing_block

    @qoala_block.setter
    def qoala_block(self, new_block: "QoalaBlock"):  # type: ignore[name-defined]
        self._containing_block = new_block

    @abstractmethod
    def can_evaluate_to(self, cls) -> bool:
        """
        Returns whether this instance can be evaluated to a given type.

        Parameters
        ----------
        cls:
            A subtype of ``QoalaValue``. The potential type to check if this
            instance can evaluate to.

        Returns
        -------
        bool:
            ``true`` if this instance can evaluate to the given type, ``false``
            otherwise.
        """
        pass


class checkbaseir:
    """
    Decorator used to "hook" the decorated function and check if the "ir" attribute
    is present before calling the decorated function.
    INTERNALS: This decorator is based on the example found at
    https://stackoverflow.com/questions/30104047/how-can-i-decorate-an-instance-method-with-a-decorator-class.
    This implementation relies on python "descriptors" (see
    https://docs.python.org/3/glossary.html#term-descriptor and
    https://docs.python.org/3/reference/datamodel.html#descriptors) which allows to define
    a "custom" behavior when trying to access an attribute (specifically, a function) of
    a class. By applying this decorator on a function, it will turn the decorated function
    (attribute) into a "descriptor", since it will define the "__get__" method.
    When python needs to access the decorated attribute of the object, it will look into
    the instance's dictionary for the attribute (function) name *before actually operating
    the attribute* (calling the function). Since the attribute is now a descriptor, it will
    invoke the '__get__' function to get the real attribute. In this class, we simply perform
    a "partial initialization" of the '__call__' method, setting the instance of the involved
    object as an argument of the '__call__' method.
    Finally, when the python runtime will invoke the returned attribute (a partially initialize
    function call), it will do it through the "__call__" method, since the decorated function
    has been annotated. In this place we can make the check about the presence of the "ir"
    attribute.
    """

    def __init__(self, to_ir_func: Callable):
        # Constructor of the decorator. We simply keep a reference of the decorated function
        self._to_ir_func = to_ir_func

    def __call__(self, instance: QoalaExpression, *args, **kwargs):
        # Since this function is partially initialized, we get a reference of the object
        # that originally contains the decorated method. We can then check if the object's
        # IR has already been computed or not.
        if instance.ir_value is not None:
            return instance.ir_value
        else:
            # If not, we compute the object's IR by calling the decorated function
            return self._to_ir_func(instance, *args, **kwargs)

    def __get__(self, instance: QoalaExpression, owner: Any | None = None):
        # The "__get__" function will be invoked before invoking the actual "__call__" method, since
        # this decorator is also a descriptor.
        # Considering that python decorators are just syntax sugar, the "self" argument of the
        # call refers to the *decorator* object. A descriptor also receives the actual instance
        # on which the '__call__' function will get invoked. For this reason, we need to perform a
        # partial initialization of that method; this will simply set an argument on the "__call__"
        # function, so we can "save" the instance of the object on which we are applying the call.
        return partial(self.__call__, instance)
