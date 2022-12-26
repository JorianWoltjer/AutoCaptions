from rich.console import Console

console = Console()

class log:
    def info(*args, **kwargs):
        """Print an informational message prefixed with `[*]`"""
        console.print(r"\[[bright_blue]*[/bright_blue]]", *args, **kwargs)

    def success(*args, **kwargs):
        """Print a successful message prefixed with `[+]`"""
        console.print(r"\[[bright_green]+[/bright_green]]", *args, **kwargs)

    def warning(*args, **kwargs):
        """Print a warning message prefixed with `[!]`"""
        console.print(r"\[[bright_yellow]![/bright_yellow]]", *args, **kwargs)

    def error(*args, exit_after=True, **kwargs):
        """Prints an error message prefixed with `[!]`. **Exits** after printing (unless `exit_after=False`)"""
        console.print(r"\[[bright_red]![/bright_red]]", *args, **kwargs)
        if exit_after: exit()


if __name__ == "__main__":
    log.info("Some information.")
    log.success("Success! We did it!")
    log.warning("Be warned...")
    log.error("Oh no, an error!")
