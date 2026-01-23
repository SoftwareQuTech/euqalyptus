from dataclasses import dataclass
from inspect import *
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
    if filename is None:
        raise RuntimeError(f"Cannot obtain source file name for function '{function}'")
    else:
        _, line_number = getsourcelines(function)
        return DebugInfo(filename, line_number, line_number, 0, 0)


def get_debug_info_for_function_name(func_name: str) -> DebugInfo:
    matching_frames = [frame for frame in stack() if frame.function == func_name]
    if len(matching_frames) <= 0:
        raise RuntimeError(
            f"Could not identify corresponding frame for function name '{func_name}'"
        )
    else:
        frame_info = matching_frames[0]
        if hasattr(frame_info, "positions") and frame_info.positions is not None:
            frame_pos = frame_info.positions
            return DebugInfo(
                frame_info.filename,
                frame_pos.lineno if frame_pos.lineno is not None else 0,
                frame_pos.end_lineno if frame_pos.end_lineno is not None else 0,
                frame_pos.col_offset if frame_pos.col_offset is not None else 0,
                frame_pos.end_col_offset if frame_pos.end_col_offset is not None else 0,
            )
        else:
            return DebugInfo(frame_info.filename, frame_info.lineno, 0, 0, 0)
