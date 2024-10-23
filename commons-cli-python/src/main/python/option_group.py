from main.python.java_handler import java_handler
from main.python.option import Option

@java_handler
class OptionGroup:
    """
    A group of mutually exclusive options.
    """
    def __init__(self):
        self.serial_version_uid = 1
        self.option_Map = {}
        self.required = False
    
    def add_option(self, option: Option):
        """
        Add the specified option to this group.
        :param option: the option to add to this group
        :return: this option group with the option added
        """
        # key - option name
        # value - the option
        self.option_Map[option.get_key()] = option
        return self

    def get_names(self):
        """
        :return: the names of the options in this group as a collection
        """
        # the key set is the collection of names
        return list(self.option_Map.keys())

    def get_options(self):
        """
        :return: the options in this group as a collection
        """
        # the values are the collection of options
        return list(self.option_Map.values())
    
    def get_selected(self):
        """
        :return: the selected option name
        """
        return self.selected
    
    def is_required(self):
        """
        Tests whether this option group is required.
        :return: whether this option group is required
        """
        return self.required
    
    def set_required(self, required: bool):
        """
        :param required: specifies if this group is required
        """
        self.required = required
    
    def set_selected(self, option: Option):
        """
        Set the selected option of this group to option.
        :param option: the option that is selected
        :raises AlreadySelectedException: if an option from this group has already been selected.
        """
        if option is None:
            # reset the option previously selected
            self.selected = None
            return
        
        # if no option has already been selected or the
        # same option is being reselected then set the
        # selected member variable
        from main.python.already_selected_exception import AlreadySelectedException
        
        option_key = option.get_key()

        if self.selected is not None and self.selected != option_key:
            raise AlreadySelectedException(self, option)

        self.selected = option_key

    def __str__(self):
        """
        Returns the stringified version of this OptionGroup.
        :return: the stringified representation of this group
        """
        buff = "["
        for i, option in enumerate(self.get_options()):
            if option.get_opt():
                buff += "-"
                buff += option.get_opt()
            else:
                buff += "--"
                buff += option.get_long_opt()

            if option.get_description():
                buff += " "
                buff += option.get_description()

            if i < len(self.get_options()) - 1:
                buff += ", "

        buff += "]"

        return buff

    def to_string(self):
        return str(self)
