import importlib
import os

from app.core.db import Migrations, connect_to_db

FUNCTION_NAME = "run"


def migrate():
    print(f"[MIGRATE] Running migrations\n")
    connect_to_db()
    current_migration = Migrations.objects.all().order_by("-applied_at").first()
    if not current_migration:
        current_migration = Migrations.objects.create(revision="0000")

    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
    files = os.listdir(folder_path)

    for file in files:
        full_file_path = os.path.join(folder_path, file)
        if os.path.isfile(full_file_path):
            filename, extension = os.path.splitext(file)
            if filename.isdigit() and filename > current_migration.revision:
                print(f"[MIGRATE] found unapplied migration {filename}\n")
                module_name = (
                    full_file_path.replace(".py", "").replace("/app/", "", 1).replace(os.path.sep, ".")
                )  # remove the file extension to get the module name
                module = importlib.import_module(module_name)  # dynamically import the module
                function = getattr(module, FUNCTION_NAME)  # get the function by name
                function()  # call the function
                print(f"[MIGRATE] applied migration {filename}\n")
                Migrations.objects.create(revision=filename)
                print(f"[MIGRATE] updated current revision to {filename}\n")

    print(f"[MIGRATE] !!!!!! DONE !!!!!!\n")


if __name__ == "__main__":
    migrate()
