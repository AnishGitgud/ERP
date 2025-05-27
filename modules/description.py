"""Not the most important module, primitive class for testing purposes mainly."""

from .stream import Stream

def get_description(self, stream: Stream) -> str:
    # find in storage stream_name = stream, get stream_name.description
    description = "Test"    # Placeholder - get from storage file
    return description

def set_description(self, stream: Stream, description: str):
    # set description in storage file
    # find in storage stream_name = stream, set stream_name.description = description
    pass

def get_note(self, stream: Stream) -> str:
    # find in storage stream_name = stream, get stream_name.note
    note = "Test"    # Placeholder - get from storage file
    return note

def set_note(self, stream: Stream, note: str):
    # set note in storage file
    # find in storage stream_name = stream, set stream_name.note = note
    pass

def get_idea(self, stream: Stream) -> str:
    # find in storage stream_name = stream, get stream_name.idea
    idea = "Test"    # Placeholder - get from storage file
    return idea

def set_idea(self, stream: Stream, idea: str):
    # set idea in storage file
    # find in storage stream_name = stream, set stream_name.idea = idea
    pass