# MTech-Dissertation-Rpi-NAS
NOTE:  After setup before starting project
```
source /home/pi/MTech-Dissertation-RPI-NAS/venv/bin/activate
```
- Building a Smart NAS System Using Raspberry Pi 4B with Bluetooth File Transfer and WhatsApp Alerts

## Objectives
1. ***NAS Implementation***: Build a fully functional NAS on Raspberry Pi 4B with external storage and Samba/CIFS sharing, accessible to Windows/Linux/Android clients.
2.  ***Web Dashboard*** : Create a Flask web interface hosted on the Pi to display system metrics (disk, CPU, memory, active users, recent uploads) in-browser over LAN.
3.  ***Bluetooth File Transfer***: Enable the Pi to receive files via Bluetooth OBEX (bluez/obexpushd), automating the Bluetooth file-upload service on boot.
4. ***Alert Automation***: Develop Python scripts to monitor system status (disk usage, connectivity) and send real-time WhatsApp alerts through Twilio API when thresholds/events occur.
5. Security (CIA Triad): Design security for Confidentiality (user-authenticated Samba, storage encryption), Integrity (checksums, change-logging, backups) and Availability        (RAID redundancy, auto-restart, health alerts).

## Hardware :Quantity: its specifications
1. ***Raspberry Pi***: 1: 4b model, 2Gb RAM, 5V, 3A
2. ***Power Adapter***: 1: 5V 3A
3. ***USB Drive***: 1: 128Gb
4. ***User Equipment***:(Laptop, mobile) with wifi and bluetooth enabled
5. ***SD Card***:1: minimum 16Gb

## Tech Stack
- Raspberry Pi 4B(ARM Cortex A-72)
- Linux(Rasbion OS, 64 bits)
- python language
- Networking
- HTML
- Git and Github

## Phases
1. ***Prerequisite Setup***: Components collection, environment setup( OS installation, installing packages).
2. ***Samba NAS setup***: Samba installation, configuration and testing drag and drop feature.
3. ***Dashboard setup using flask***: Flask installation, configuration and testing for uploading, downloading and deleting file using web browser.
4. ***Bluetooth file sharing***: uploading file to NAS setup without wifi need.
5. ***Whatsapp alert setup***: Receive real-time alert for setup being deactivated, or storage being full.
6. ***Demonstration and documentation***: Detailed information related to project setup from scratch.


