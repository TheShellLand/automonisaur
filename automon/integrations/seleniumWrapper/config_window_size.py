from automon.log import logger

log = logger.logging.getLogger(__name__)
log.setLevel(logger.INFO)


def set_window_size(width: int = 1920, height: int = 1080, device_type: str = None) -> (int, int):
    """set browser resolution"""

    if device_type == 'pixel3':
        width = 1080
        height = 2160

    if device_type == 'web-small' or device_type == '800x600':
        width = 800
        height = 600

    if device_type == 'web-small-2' or device_type == '1024x768':
        width = 1024
        height = 768

    if device_type == 'web-small-3' or device_type == '1280x960':
        width = 1280
        height = 960

    if device_type == 'web-small-4' or device_type == '1280x1024':
        width = 1280
        height = 1024

    if device_type == 'web' or device_type == '1920x1080':
        width = 1920
        height = 1080

    if device_type == 'web-2' or device_type == '1600x1200':
        width = 1600
        height = 1200

    if device_type == 'web-3' or device_type == '1920x1200':
        width = 1920
        height = 1200

    if device_type == 'web-large' or device_type == '2560x1400':
        width = 2560
        height = 1400

    if device_type == 'web-long' or device_type == '1920x3080':
        width = 1920
        height = 3080

    if not width and not height:
        width = 1920
        height = 1080

    log.debug(f'{int(width)}, {int(height)}')

    return int(width), int(height)
