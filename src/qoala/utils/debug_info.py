from dataclasses import dataclass
from inspect import stack, getsourcefile, getsourcelines
from typing import Callable


function_name = ""


@dataclass
class DebugInfo:
    filename: str
    line_start: int
    line_end: int
    col_start: int
    col_end: int


def get_debug_info() -> DebugInfo:
    return get_debug_info_for_function_name(function_name)


def get_debug_info_for_function(function: Callable) -> DebugInfo:
    filename = getsourcefile(function)
    code, line_number = getsourcelines(function)
    return DebugInfo(filename, line_number, line_number, 0, 0)


def get_debug_info_for_function_name(func_name: str) -> DebugInfo:
    matching_frames = [frame for frame in stack() if frame.function == func_name]
    if len(matching_frames) <= 0:
        raise RuntimeError(f"Could not identify corresponding frame for function name '{func_name}'")
    else:
        frame_info = matching_frames[0]
    return DebugInfo(
        frame_info.filename,
        frame_info.positions.lineno,
        frame_info.positions.end_lineno,
        frame_info.positions.col_offset,
        frame_info.positions.end_col_offset
    )
