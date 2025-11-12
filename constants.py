# Constants defined as per my current protocol definition
# To be migrated to a more complex mechanism, cause what if file contents tart with fssg or end with FEG.
FILE_START_SEND_FLAG = "FSSG"
FILE_END_FLAG = bytes("FEG", "utf-8")
FILE_METADATA_SEPARATOR = "|"


# This is just part of the custom protocol for this operation
# Used as a flag that tells the client upon reception that Im about to send a file
# After-wards the protocol used, sends the file name, and its size(used to calculate progress), then the file bytes sequence