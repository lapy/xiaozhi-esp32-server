import os
import importlib.util
import asyncio

print("Please prepare configuration according to the instructions in doc/performance_testerer.md before use.")


def list_performance_tester_modules():
    performance_tester_dir = os.path.join(
        os.path.dirname(__file__), "performance_tester"
    )
    modules = []
    for file in os.listdir(performance_tester_dir):
        if file.endswith(".py"):
            modules.append(file[:-3])
    return modules


async def load_and_execute_module(module_name):
    module_path = os.path.join(
        os.path.dirname(__file__), "performance_tester", f"{module_name}.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "main"):
        main_func = module.main
        if asyncio.iscoroutinefunction(main_func):
            await main_func()
        else:
            main_func()
    else:
        print(f"No main function found in module {module_name}.")


def get_module_description(module_name):
    module_path = os.path.join(
        os.path.dirname(__file__), "performance_tester", f"{module_name}.py"
    )
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "description", "No description available")


def main():
    modules = list_performance_tester_modules()
    if not modules:
        print("No available performance testing tools in performance_tester directory.")
        return

    print("Available performance testing tools:")
    for idx, module in enumerate(modules, 1):
        description = get_module_description(module)
        print(f"{idx}. {module} - {description}")

    try:
        choice = int(input("Please select the performance testing tool number to call: ")) - 1
        if 0 <= choice < len(modules):
            asyncio.run(load_and_execute_module(modules[choice]))
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a valid number.")


if __name__ == "__main__":
    main()
