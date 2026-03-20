import inspect

def has_parameters(func):
    sig = inspect.getargspec(func)
    return len(sig.args) > 0

class Command:
    def __init__(self, name, description, usage_lines=[], synonyms=None, method=None, preprocess_parameters_method=None, is_quit_command=False):
        self.name = name
        self.description = description
        self.usage_lines = usage_lines
        self.synonyms = synonyms if synonyms is not None else []
        self.method = method
        self.preprocess_parameters_method = preprocess_parameters_method
        self.is_quit_command = is_quit_command

    def get_usage_text(self):
        usage_text = "Usage: {}".format(self.name)
        if self.usage_lines:
            usage_text += " " + " ".join(self.usage_lines)
        if self.synonyms:
            usage_text += " (Synonyms: " + ", ".join(self.synonyms) + ")"

        return usage_text

    def matches_command_line(self, command_line):
        command_text = command_line[0] if isinstance(command_line, list) else command_line
        if command_text == self.name or command_text in self.synonyms:
            return True
        return False

    def execute(self, command_line):
        command_parameters = command_line[1:] if isinstance(command_line, list) else []
        if self.method is None:
            return None
        else:
            if has_parameters(self.method):
                if self.preprocess_parameters_method:
                    final_command_parameters = self.preprocess_parameters_method(command_parameters)
                else:
                    final_command_parameters = command_parameters
                return self.method(final_command_parameters)
            else:
                return self.method()

    def __str__(self):
        return "{}: {}\nUsage: {}".format(self.name, self.description, self.get_usage_text())

class CommandResult:
    def __init__(self, success, data=None, is_quit_command=False, message=None):
        self.success = success
        self.data = data
        self.is_quit_command = is_quit_command
        self.message = message

    def __str__(self):
        return "CommandResult(success={}, data={}, is_quit_command={}, message={})".format(self.success, self.data, self.is_quit_command, self.message)

    def get_success(self):
        return self.success

    def get_data(self):
        return self.data

    def get_is_quit_command(self):
        return self.is_quit_command

    def get_message(self):
        return self.message


class CommandExecutor:

    def __init__(self, commands=None):
        self.commands = commands if commands is not None else []

    def register_command(self, command):
        self.commands.append(command)

    def execute_command(self, command_line):
        for command in self.commands:
            if command.matches_command_line(command_line):
                try:
                    return CommandResult(
                        True, 
                        data=command.execute(command_line), 
                        is_quit_command=command.is_quit_command
                    )

                except Exception as e:
                    return CommandResult(False, message=str(e))
        return CommandResult(False, message="Unknown command '" + command_line[0] + "'")