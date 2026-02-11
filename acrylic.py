import ctypes

# Accent states
ACCENT_DISABLED = 0
ACCENT_ENABLE_GRADIENT = 1
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
ACCENT_ENABLE_BLURBEHIND = 3
ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

# Window composition attribute
WCA_ACCENT_POLICY = 19


class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_uint32),
        ("AnimationId", ctypes.c_int),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t),
    ]


def enable_acrylic(hwnd, tint=0xCC202020):
    accent = ACCENTPOLICY()
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.AccentFlags = 0
    accent.GradientColor = tint  # AARRGGBB
    accent.AnimationId = 0

    accent_ptr = ctypes.pointer(accent)

    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = WCA_ACCENT_POLICY
    data.Data = ctypes.cast(accent_ptr, ctypes.c_void_p)
    data.SizeOfData = ctypes.sizeof(accent)

    set_window_comp_attr = ctypes.windll.user32.SetWindowCompositionAttribute
    set_window_comp_attr(hwnd, ctypes.byref(data))