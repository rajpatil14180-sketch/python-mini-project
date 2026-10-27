"""Launch GharPar PG Manager."""
from ui.app import GharParApp


def main():
    """FEATURE: Application Startup
    Start the desktop application."""
    app = GharParApp()
    app.mainloop()


if __name__ == "__main__":
    main()
