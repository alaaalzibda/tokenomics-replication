'''
Main entry point for the Palindrome Detector GUI application.
'''
import sys
from gui_app import PalindromeGUI
def main():
    app = PalindromeGUI()
    app.title("Palindrome Detector")
    # Optionally set a minimum size
    app.minsize(900, 600)
    app.mainloop()
if __name__ == "__main__":
    main()