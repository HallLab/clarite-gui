if __name__ == "__main__":

    import sys
    from gui import AppContext

    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
