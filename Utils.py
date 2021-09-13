import win32api
import shutil


def get_drives(priority_drive_name):
    """
    This function returns a list of drives that are suitable for storing the data files. They must have enough free
    space.
    """

    drives_list = []
    error_list = []

    # Save
    local_drive_letter = win32api.GetWindowsDirectory().split("\\")[0] + "\\"

    # 1. Save on the local drive if there is space
    _, _, local_free = shutil.disk_usage(local_drive_letter)

    if (local_free / 1073741824) < 2:
        error_list.append('Local disk is low on space')
    else:
        drives_list.append(local_drive_letter)

    # 2. Save in external drive, prioritize one named in priority_drive_name. Else get one with the largest space

    # Get names of attached drives
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    drives.remove(local_drive_letter)

    priority_drive = None

    for drive in drives:
        if win32api.GetVolumeInformation(drive)[0].upper() == priority_drive_name:
            priority_drive = drive

    if priority_drive:
        # check that the priority drive has enough space
        _, _, priority_drive_free = shutil.disk_usage(priority_drive)

        if (priority_drive_free / 1073741824) < 2:
            error_list.append("Clear Sky Drive is low on space")
            priority_drive = False
        else:
            drives_list.append(priority_drive)
    else:
        error_list.append("No drive named" + priority_drive + "!")

    # If priority drive has not been found or does not have enough free space

    if not priority_drive:
        drive_space = {}
        for drive in drives:
            _, _, free = shutil.disk_usage(drive)

            if (free / 1073741824) >= 2:
                drive_space[drive] = free

        if len(drive_space) != 0:
            external_drive = max(drive_space, key=drive_space.get)
            drives_list.append(external_drive)
        else:
            error_list.append("No external drive found or did not have enough space")

    error_message = '\n'.join(error_list)

    return drives_list, error_message
