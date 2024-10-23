from main.python.option import Option
from main.python.option_group import OptionGroup
from main.python.util import Util
from main.python.java_handler import java_handler

@java_handler
class Options:
    """
    Main entry-point into the library.

    Options represents a collection of Option objects, which describe the possible options for a command-line. 

    It may flexibly parse long and short options, with or without values. Additionally, it may parse only a portion of a
    commandline, allowing for flexible multi-stage parsing.
    """
    def __init__(self):
        # The serial version UID.
        self.serial_version_uid = 1

        # a map of the options with the character key
        self.short_opts = {}

        # a map of the options with the long key
        self.long_opts = {}

        # a map of the required options
        self.required_opts = []

        # a map of the option groups
        self.option_groups = {}

    def add_option(self, opt: str | Option, *args):
        """
        Adds an option instance.

        :param opt: the option that is to be added or short single-character name of the option.
        :return: the resulting Options instance
        """
        if(len(args) == 0):
            return self._add_option(opt)
        
        if(len(args) == 1):
            # Add an option that only contains a short-name, opt. The option does not take an argument.
            # *args = (description)
            # description: Self-documenting description
            return self.add_option(opt, None, False, *args)
        
        if(len(args) == 2):
            # Add an option that only contains a short-name, opt. It may be specified as requiring an argument.
            # *args = (has_arg, description)
            # has_arg: flag signalling if an argument is required after this option
            # description: Self-documenting description
            return self.add_option(opt, None, *args)
        
        if(len(args) == 3):
            # Add an option that contains a short-name, opt and a long-name. It may be specified as requiring an argument.
            # *args = (long_opt, has_arg, description)
            # long_opt: Long multi-character name of the option.
            # has_arg: flag signalling if an argument is required after this option
            # description: Self-documenting description
            return self.add_option(Option(opt, *args))

    def _add_option(self, opt: Option):
        """
        Adds an option instance

        :param opt: the option that is to be added
        :return: the resulting Options instance
        """
        key = opt.get_key()

        # add it to the long option list
        if opt.has_long_opt():
            self.long_opts[opt.get_long_opt()] = opt

        # if the option is required add it to the required list
        if opt.is_required():
            if key in self.required_opts:
                del self.required_opts[self.required_opts.index(key)]
            self.required_opts.append(key)

        self.short_opts[key] = opt

        return self
    
    def add_option_group(self, group: OptionGroup):
        """
        Add the specified option group.

        :param group: the OptionGroup that is to be added
        :return: the resulting Options instance
        """
        if group.is_required():
            self.required_opts.append(group)

        for option in group.get_options():
            # an Option cannot be required if it is in an
            # OptionGroup, either the group is required or
            # nothing is required
            option.set_required(False)
            self.add_option(option)
            self.option_groups[option.get_key()] = group

        return self
    
    def add_required_option(self, opt: str, long_opt: str, has_arg: bool, description: str):
        """
        Add an option that contains a short-name and a long-name.
        The added option is set as required. It may be specified as requiring an argument.

        :param opt: Short single-character name of the option.
        :param long_opt: Long multi-character name of the option.
        :param has_arg: flag signalling if an argument is required after this option
        :param description: Self-documenting description
        :return: the resulting Options instance
        """
        option = Option(opt, long_opt, has_arg, description)
        option.set_required(True)
        self.add_option(option)
        return self

    def get_matching_options(self, opt: str):
        """
        Gets the options with a long name starting with the name specified.

        :param opt: the partial name of the option
        :return: the options matching the partial name specified, or an empty list if none matches
        """
        opt = opt.lstrip('-')

        matching_opts = []

        # for a perfect match return the single option only
        if opt in self.long_opts:
            return [opt]

        for long_opt in self.long_opts.keys():
            if long_opt.startswith(opt):
                matching_opts.append(long_opt)

        return matching_opts

    def get_option(self, opt: str):
        """
        Gets the Option matching the long or short name specified.

        :param opt: short or long name of the Option
        :return: the option represented by opt
        """
        opt = Util.strip_leading_hyphens(opt)

        if opt in self.short_opts:
            return self.short_opts[opt]

        return self.long_opts[opt] if opt in self.long_opts else None
    
    def get_option_group(self, opt: Option):
        """
        Gets the OptionGroup the opt belongs to.

        :param opt: the option whose OptionGroup is being queried.
        :return: the OptionGroup if opt is part of an OptionGroup, otherwise return None
        """
        return self.option_groups[opt.get_key()] if opt.get_key() in self.option_groups else None
    
    def get_option_groups(self):
        """
        Gets the OptionGroups that are members of this Options instance.

        :return: a Collection of OptionGroup instances.
        """
        return list(set(self.option_groups.values()))
    
    def get_options(self):
        """
        Gets a read-only list of options in this set

        :return: read-only Collection of Option objects in this descriptor
        """
        return self.help_options()
    
    def get_required_options(self):
        """
        Gets the required options.

        :return: read-only List of required options
        """
        return self.required_opts
    
    def has_long_option(self, opt: str):
        """
        Returns whether the named Option is a member of this Options.

        :param opt: long name of the Option
        :return: true if the named Option is a member of this Options
        """
        opt = Util.strip_leading_hyphens(opt)

        return opt in self.long_opts
    
    def has_option(self, opt: str):
        """
        Returns whether the named Option is a member of this Options.
        
        :param opt: short or long name of the Option
        :return: true if the named Option is a member of this Options
        """
        opt = Util.strip_leading_hyphens(opt)

        return opt in self.short_opts or opt in self.long_opts
    
    def has_short_option(self, opt: str):
        """
        Returns whether the named Option is a member of this Options.

        :param opt: short name of the Option
        :return: true if the named Option is a member of this Options
        """
        opt = Util.strip_leading_hyphens(opt)

        return opt in self.short_opts
    
    def help_options(self):
        """
        Returns the Options for use by the HelpFormatter.

        :return: the List of Options
        """
        return list(self.short_opts.values())
    
    def __str__(self):
        """
        Dump state, suitable for debugging.

        :return: Stringified form of this object
        """
        buf = []

        buf.append("[ Options: [ short ")
        buf.append(str(self.short_opts))
        buf.append(" ] [ long ")
        buf.append(str(self.long_opts))
        buf.append(" ]")

        return ''.join(buf)

    def to_string(self):
        """
        Keeping for compatibility with other translated code.
        This can eventually be removed.
        """
        return self.__str__()
