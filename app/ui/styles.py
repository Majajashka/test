APP_STYLE = """
QMainWindow, QWidget {
    background-color: #0d0e11; 
    color: #e3e6eb;            
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QMessageBox {
    background-color: #16181d;
}
QMessageBox QLabel {
    color: #e3e6eb;
    background: transparent;
}
QMessageBox QPushButton {
    min-width: 80px;
}


QFrame#card {
    background-color: #16181d; 
    border: 1px solid #242930;
    border-radius: 12px;       
}

QFrame#sidebar {
    background-color: #090a0c;
    border-right: 1px solid #1f2228;
}

QLabel#mainTitle {
    font-size: 32px;
    font-weight: 800;
    color: #528bff;            
    letter-spacing: 2px;
    background: transparent;
}

QLabel#pageTitle {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    padding-bottom: 4px;
    background: transparent;
}

QLabel#fieldLabel {
    font-size: 13px;
    font-weight: 600;
    color: #a9a9b3; 
    background: transparent;
}

QLabel#formHeading {
    font-size: 15px;
    font-weight: 500;
    color: #8c95a0;
    background: transparent;
}

QLabel#sidebarUserInfo {
    background-color: #16181d; 
    border-radius: 6px;
    color: #8c95a0;            
    font-size: 13px;
    margin: 8px 12px;          
}

QLabel#sidebarUserInfo strong {
    color: #ffffff;            
    font-weight: 600;
}


QLineEdit, QPlainTextEdit, QComboBox {
    background-color: #1f2228; 
    color: #ffffff;
    border: 1px solid #2f363d;
    border-radius: 6px;
    padding: 6px 12px;
    selection-background-color: #528bff;
}

QLineEdit:hover, QPlainTextEdit:hover, QComboBox:hover {
    border: 1px solid #444d56;
}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {
    border: 1px solid #528bff;
    background-color: #242930;
}

QPlainTextEdit {
    padding: 12px;
    line-height: 20px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left: none;
}


QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #30363d;
    color: #ffffff;
    border-color: #8b949e;
}

QPushButton:pressed {
    background-color: #161b22;
}

QPushButton#actionBtn {
    background-color: #238636; 
    color: #ffffff;
    border: 1px solid #2ea44f;
    font-weight: 600;
}

QPushButton#actionBtn:hover {
    background-color: #2ea44f;
}

QPushButton#actionBtn:pressed {
    background-color: #24833f;
}

QPushButton#actionBtn:disabled {
    background-color: #142318;
    color: #48634f;
    border-color: #1b3522;
}

QPushButton#switchBtn {
    background: transparent;
    border: none;
    color: #58a6ff;
    font-weight: 500;
    padding: 4px 8px;
}

QPushButton#switchBtn:hover {
    color: #79c0ff;
    text-decoration: underline;
}

QPushButton#navBtn {
    text-align: left;
    border: none;
    border-radius: 6px;
    padding: 10px 14px;
    background: transparent;
    color: #8c95a0;
    margin: 2px 8px;
}

QPushButton#navBtn:hover {
    background-color: #16181d;
    color: #ffffff;
}

QPushButton#navBtn:checked {
    background-color: #1f2228;
    color: #58a6ff;
    font-weight: 600;
}

QPushButton#browseBtn {
    background-color: #202024; 
    border: 1px solid #2f363d;
    border-left: none;         
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    font-size: 16px;           
    padding: 0px;
}

QPushButton#browseBtn:hover {
    background-color: #242930;
    color: #ffffff;
}

QPushButton#browseBtn:pressed {
    background-color: #161b22;
}


QGroupBox {
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 2ch;
    background-color: #111318;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
    color: #8c95a0;
    font-weight: 600;
    background: transparent;
}
"""