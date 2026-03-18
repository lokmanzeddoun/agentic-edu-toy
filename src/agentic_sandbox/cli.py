from rich.console import Console
from rich.table import Table
import typer

from agentic_sandbox.config import load_environment
from agentic_sandbox.memory import DEFAULT_STORAGE_PATH
from agentic_sandbox.prototype import EducationalToyPrototype


app = typer.Typer(help="Starter CLI for agentic AI experiments.")
prototype_app = typer.Typer(help="Educational toy prototype commands.")
console = Console()

app.add_typer(prototype_app, name="prototype")


@app.callback()
def entrypoint() -> None:
    """Root CLI entrypoint."""
    load_environment()


@app.command()
def status() -> None:
    """Print the current project status."""
    prototype = EducationalToyPrototype.from_storage(DEFAULT_STORAGE_PATH)
    status_payload = prototype.status()
    table = Table(title="agentic-sandbox")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Package", "agentic-sandbox")
    table.add_row("Prototype", "educational-toy")
    table.add_row("Learner", status_payload.learner_name)
    table.add_row("Level", str(status_payload.level))
    table.add_row("LLM mode", "enabled" if status_payload.llm_enabled else "disabled")
    table.add_row("Model", status_payload.llm_model or "local fallback")
    table.add_row("Session", str(status_payload.storage_path))
    console.print(table)


@prototype_app.command("start")
def prototype_start(
    learner_name: str = typer.Option("Learner", "--name", "-n", help="Learner display name."),
    age: int = typer.Option(7, "--age", min=3, max=12, help="Learner age."),
) -> None:
    """Start or resume the educational toy prototype."""
    prototype = EducationalToyPrototype.from_storage(DEFAULT_STORAGE_PATH)
    opening = prototype.bootstrap(learner_name=learner_name, age=age)
    console.print(f"[bold blue]Meta-Agent[/bold blue]: {opening}")


@prototype_app.command("turn")
def prototype_turn(
    learner_input: str = typer.Argument(..., help="Learner answer for the current lesson."),
) -> None:
    """Submit a single learner turn to the prototype."""
    prototype = EducationalToyPrototype.from_storage(DEFAULT_STORAGE_PATH)
    response = prototype.handle_turn(learner_input)
    console.print(f"[bold magenta]Toy[/bold magenta]: {response.response_text}")


@prototype_app.command("chat")
def prototype_chat(
    learner_name: str = typer.Option("Learner", "--name", "-n", help="Learner display name."),
    age: int = typer.Option(7, "--age", min=3, max=12, help="Learner age."),
) -> None:
    """Launch an interactive terminal chat with the prototype."""
    prototype = EducationalToyPrototype.from_storage(DEFAULT_STORAGE_PATH)
    opening = prototype.bootstrap(learner_name=learner_name, age=age)
    console.print(f"[bold blue]Meta-Agent[/bold blue]: {opening}")
    console.print("[dim]Type 'exit' to end the session.[/dim]")

    while True:
        learner_input = typer.prompt("You")
        if learner_input.strip().lower() in {"exit", "quit"}:
            console.print("[bold yellow]Session saved.[/bold yellow]")
            break
        response = prototype.handle_turn(learner_input)
        console.print(f"[bold magenta]Toy[/bold magenta]: {response.response_text}")


@prototype_app.command("profile")
def prototype_profile() -> None:
    """Display the current learner state."""
    prototype = EducationalToyPrototype.from_storage(DEFAULT_STORAGE_PATH)
    profile = prototype.state.profile
    table = Table(title="Learner Profile")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Name", profile.learner_name)
    table.add_row("Age", str(profile.age))
    table.add_row("Level", str(profile.level))
    table.add_row("Total turns", str(profile.total_turns))
    table.add_row("Correct answers", str(profile.correct_answers))
    table.add_row("Incorrect answers", str(profile.incorrect_answers))
    table.add_row("Detected emotion", profile.detected_emotion)
    table.add_row("Current prompt", profile.current_prompt or "None")
    table.add_row("LLM mode", "enabled" if prototype.llm_enabled else "disabled")
    table.add_row("Model", prototype.llm_model or "local fallback")
    console.print(table)


@prototype_app.command("reset")
def prototype_reset() -> None:
    """Reset the persisted learner session."""
    prototype = EducationalToyPrototype.from_storage(DEFAULT_STORAGE_PATH)
    prototype.reset()
    console.print("[bold yellow]Prototype session has been reset.[/bold yellow]")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
