import subprocess

# Linux Python script to bulk copy the contents of floppy disks to a hard disk.

class FloppyDiskDrive:
    def __init__(self, name, label, uuid):
        self.name = name
        self.label = label
        self.uuid = uuid

    def get_device_path(self):
        return "/dev/" + self.name

    def copy_to_hard_disk(self, destination_path):
        subprocess.call(["sudo", "dd", "if=" + self.get_device_path(), "of=" + destination_path])


def get_floppy_disk_drives():
    floppy_disk_drives = []

    # Execute `lsblk` and store the output in a string.
    lsblk_output = subprocess.check_output(['lsblk', '-o', 'NAME,SIZE,UUID,LABEL']).decode('utf-8')

    # Loop through the output and find any devices with a size of 1.4M
    for line in lsblk_output.splitlines():
        line_parts = line.split()
        size = line_parts[1]
        if size == '1.4M':

            # Get name and label of floppy disk drive
            name = line_parts[0]

            # Don't copy loop devices (mounted images)
            if name.startswith('loop'):
                continue

            if len(line_parts) > 2:
                uuid = line_parts[2]
            else:
                uuid = ""

            if len(line_parts) > 3:
                label = line_parts[3]
            else:
                label = ""

            floppy_disk_drives.append(FloppyDiskDrive(name, label, uuid))

    return floppy_disk_drives


# Get user desktop folder
desktop_path = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode("utf-8").strip()

# Append bulk-floppy-copy to the desktop path, creating it if it doesn't exist
desktop_path = desktop_path + "/bulk-floppy-copy-output"
subprocess.call(["mkdir", "-p", desktop_path])

# Output user desktop folder
print("Desktop path: " + desktop_path)

# Start infinite loop
while True:

    # Prompt to insert floppy disk
    print("Insert new floppy disk...")

    # Sleep for a few seconds
    subprocess.call(["sleep", "5"])

    floppy_disk_drives = get_floppy_disk_drives()

    # If we have no floppy disk drives, exit.
    if len(floppy_disk_drives) == 0:
        print('No floppy disk found.')
        continue

    # If we have more than one floppy disk drive, exit.
    if len(floppy_disk_drives) > 1:
        print('More than one floppy disk drive found.')
        continue

    # If we have one floppy disk drive, continue.
    floppy_disk_drive = floppy_disk_drives[0]

    # Output floppy disk drive details.
    print('Floppy disk drive: ' + floppy_disk_drive.name)
    print('Floppy disk label: ' + floppy_disk_drive.label)
    print('Floppy disk UUID: ' + floppy_disk_drive.uuid)

    # Make .img file name consisting of datetime, UUID, and label if present
    image_file_name = subprocess.check_output(['date', '+%Y-%m-%d-%H-%M-%S']).decode('utf-8').strip()
    if floppy_disk_drive.uuid != "":
        image_file_name = image_file_name + "_" + floppy_disk_drive.uuid
    if floppy_disk_drive.label != "":
        image_file_name = image_file_name + "_" + floppy_disk_drive.label
    image_file_name = image_file_name + ".img"

    destination_path = desktop_path + "/" + image_file_name

    # Copy floppy disk content to user desktop folder
    print('Copying floppy disk to: ' + destination_path)
    floppy_disk_drive.copy_to_hard_disk(destination_path)

    print('Copy complete.')

    print('Please eject floppy disk.')

    while True:
        # Sleep for a few seconds
        subprocess.call(["sleep", "1"])

        floppy_disk_drives = get_floppy_disk_drives()

        if len(floppy_disk_drives) == 0:
            break

        print('Floppy disk still inserted. Please eject floppy disk.')

    print('Floppy disk ejected.')
