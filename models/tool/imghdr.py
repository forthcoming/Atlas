__all__ = ["what"]

def what(file_or_content):
    content=b''
    if isinstance(file_or_content,bytes):
        content=file_or_content[:32]
    elif isinstance(file_or_content,str):
        with open(file_or_content, 'rb') as f:
            content = f.read(32)
    else:
        location = file_or_content.tell()
        content = file_or_content.read(32)
        file_or_content.seek(location)
    for test in tests:
        res = test(content)
        if res:
            return res


def jpeg(h):
    if h[6:10] in (b'JFIF', b'Exif') or h.startswith(b'\xff\xd8'):
        return 'jpeg'

def png(h):
    if h.startswith(b'\211PNG\r\n\032\n'):
        return 'png'

def gif(h):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def tiff(h):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

def rgb(h):
    """SGI image library"""
    if h.startswith(b'\001\332'):
        return 'rgb'

def pbm(h):
    """PBM (portable bitmap)"""
    if len(h) >= 3 and h[0] == ord(b'P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'

def pgm(h):
    """PGM (portable graymap)"""
    if len(h) >= 3 and h[0] == ord(b'P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'

def ppm(h):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and h[0] == ord(b'P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'

def rast(h):
    """Sun raster file"""
    if h.startswith(b'\x59\xA6\x6A\x95'):
        return 'rast'

def xbm(h):
    """X bitmap (X10 or X11)"""
    if h.startswith(b'#define '):
        return 'xbm'

def bmp(h):
    if h.startswith(b'BM'):
        return 'bmp'

def webp(h):
    if h.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'

def exr(h):
    if h.startswith(b'\x76\x2f\x31\x01'):
        return 'exr'

tests = [
    jpeg,
    png,
    gif,
    tiff,
    rgb,
    pbm,
    pgm,
    ppm,
    rast,
    xbm,
    bmp,
    webp,
    exr,
]
