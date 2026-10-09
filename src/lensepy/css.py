
#### Style Sheet for LEnsE API

# Symbols
LAMBDA = '\u03BB'

# Colors
# ------
BLUE_IOGS = '#0A3250'
ORANGE_IOGS = '#FF960A'
GREEN_IOGS = (0, 180, 0)
RED_IOGS = (200, 0, 0)
WHITE = '#000000'
GRAY = '#727272'
BLACK = '#FFFFFF'

# Styles
# ------
STYLE_H1 = {
    'WHITE': {
        'CLASSIC': f"font-size:18px; padding:0px; color:{BLUE_IOGS};font-weight: bold;",
        'LITE': f"font-size:14px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
    },
    'BLACK':{
        'CLASSIC': f"font-size:18px; padding:0px; color:{ORANGE_IOGS};font-weight: bold;",
        'LITE': f"font-size:14px; padding:0px; color:{ORANGE_IOGS};font-weight: bold;"
    }
}
STYLE_H2 = {
    'CLASSIC': f"font-size:16px; padding:0px; color:{BLUE_IOGS}; font-weight: bold;",
    'LITE': f"font-size:12px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
}
STYLE_H3 = {
    'CLASSIC': f"font-size:14px; padding:0px; color:{BLUE_IOGS};",
    'LITE': f"font-size:10px; padding:0px; color:{BLUE_IOGS};"
}
NO_STYLE = {
    'CLASSIC': f"background-color:{GRAY}; color:{BLACK}; font-size:14px;",
    'LITE': f"background-color:{GRAY}; color:{BLACK}; font-size:12px;"
}
STYLE_L = {
    'CLASSIC': f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;",
    'LITE': f"font-size:10px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
}
STYLE_T = {
    'CLASSIC': f"font-size:14px; padding:5px; font-weight: bold; background-color: white;",
    'LITE': f"font-size:10px; padding:2px; font-weight: bold; background-color: white;"
}


styleH1 = f"font-size:18px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
styleH2 = f"font-size:16px; padding:0px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3 = f"font-size:14px; padding:0px; color:{BLUE_IOGS};"
styleH1_s = f"font-size:14px; padding:0px; color:{BLUE_IOGS};font-weight: bold;"
styleH2_s = f"font-size:12px; padding:0px; color:{BLUE_IOGS}; font-weight: bold;"
styleH3_s = f"font-size:10px; padding:0px; color:{BLUE_IOGS};"
styleCheckbox = f"font-size: 14px; padding: 3px; color: {BLUE_IOGS}; font-weight: normal;"
no_style = f"background-color:{GRAY}; color:{BLACK}; font-size:14px;"
no_style_s = f"background-color:{GRAY}; color:{BLACK}; font-size:12px;"
styleL = f"font-size:14px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
styleT = f"font-size:14px; padding:5px; font-weight: bold; background-color: white;"
styleL_s = f"font-size:10px; padding:0px; color:{ORANGE_IOGS}; font-weight: bold;"
styleT_s = f"font-size:10px; padding:2px; font-weight: bold; background-color: white;"


DISABLED_BUTTON = {
    'CLASSIC': f"background-color:{GRAY}; color:{BLACK}; font-size:14px; border-radius: 10px;",
    'LITE': f"background-color:{GRAY}; color:{BLACK}; font-size:10px; border-radius: 10px;"
}
INACTIVATED_BUTTON = {
    'CLASSIC': f"background-color:{BLUE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;",
    'LITE': f"background-color:{BLUE_IOGS}; color:white; font-size:10px; border-radius: 10px;"
}
ACTIVATED_BUTTON = {
    'CLASSIC': f"background-color:{ORANGE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;",
    'LITE': f"background-color:{ORANGE_IOGS}; color:white; font-size:10px; font-weight:bold; border-radius: 10px;"
}
disabled_button = f"background-color:{GRAY}; color:{BLACK}; font-size:14px; border-radius: 10px;"
unactived_button = f"background-color:{BLUE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;"
actived_button = f"background-color:{ORANGE_IOGS}; color:white; font-size:14px; font-weight:bold; border-radius: 10px;"
BUTTON_HEIGHT = {'CLASSIC': 37, 'LITE': 22} #px
OPTIONS_BUTTON_HEIGHT = {'CLASSIC': 18, 'LITE': 14} #px


StyleSheet = '''
#IOGSProgressBar {
    text-align: center;
    color: white;
    width: 10px; 
    min-height: 16px;
    max-height: 16px;
    border-radius: 6px;
}
#IOGSProgressBar::chunk {
    border-radius: 6px;
    background-color: #FF960A;
}
'''

def progress_bar_color(bg_color, fg_color):
    css_text = (f'QProgressBar {{ border: 2px solid #444;'
                f'border-radius: 5px; background-color: {bg_color};'
                f'color: white; }}'
                f' QProgressBar::chunk {{ background-color: {fg_color};'
                f'border-radius: 3px; }}')
    return css_text