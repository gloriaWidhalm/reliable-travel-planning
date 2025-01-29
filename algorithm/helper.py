# This file contains functions that are used in multiple files, and it is more convenient to have them in a separate file.

def is_transfer_needed(trip_identifier_1: str | None, trip_identifier_2: str | None) -> bool:
    """
    Check if a transfer is needed between two trips. If the trip identifiers are different, a transfer is needed.
    Otherwise, we assume we are in the same train and no transfer is needed.
    """
    # check if the trip identifiers are different
    if trip_identifier_1 and trip_identifier_2 and trip_identifier_1 != trip_identifier_2:
        return True
    return False