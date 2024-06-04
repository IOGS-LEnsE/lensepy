__all__ = [
    "widget_slider",      # refers to the 'widget_slider.py' file
    "widget_histogram",   # refers to the 'widget_histogram.py' file
    "widget_image_display",     # refers to the 'widget_image_display.py' file
]

#### Style Sheet for LEnsE API

# Colors
# ------
BLUE_IOGS = '#0A3250'
ORANGE_IOGS = '#FF960A'
WHITE = '#000000'
GRAY = '#727272'
BLACK = '#FFFFFF'

# Styles
# ------
styleH1 = f"font-size:20px; padding:7px; color:{BLUE_IOGS};font-weight: bold;"
no_style = f"background-color:{GRAY}; color:{BLACK}; font-size:15px;"

unactived_button = f"background-color:{BLUE_IOGS}; color:white; font-size:15px; font-weight:bold; border-radius: 10px;"
actived_button = f"background-color:{ORANGE_IOGS}; color:white; font-size:15px; font-weight:bold; border-radius: 10px;"