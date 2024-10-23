/*
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 */

package org.apache.commons.cli;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * Represents list of arguments parsed against a {@link Options} descriptor.
 * <p>
 * It allows querying of a boolean {@link #hasOption(String opt)}, in addition
 * to retrieving the
 * {@link #getOptionValue(String opt)} for options requiring arguments.
 * <p>
 * Additionally, any left-over or unrecognized arguments, are available for
 * further processing.
 */
public class CommandLine implements Serializable {
    /**
     * Contains a reference to the python class
     */
    private static Value clz = ContextInitializer.getPythonClass("command_line.py", "CommandLine");;

    /**
     * Contains a reference to the embedded Python Object
     */
    private Value cmdLineObj;

    /**
     * A nested builder class to create {@code CommandLine} instance using
     * descriptive methods.
     *
     * @since 1.4
     */
    public static final class Builder {
        /**
         * Contains reference to Builder python class.
         */
        private static Value builderClz = ContextInitializer.getPythonClass("command_line.py", "CommandLine").getMember("Builder");

        /**
         * Contains a reference to the embedded Python Object
         */
        private Value builderObj;

        public Builder() {
            builderObj = builderClz.newInstance();
        }

        public Value getPythonObject() {
            return builderObj;
        }

        /**
         * Add left-over unrecognized option/argument.
         *
         * @param arg the unrecognized option/argument.
         *
         * @return this Builder instance for method chaining.
         */
        public Builder addArg(final String arg) throws IllegalArgumentException {
            try {
                builderObj.invokeMember("add_arg", arg);
            } catch (PolyglotException e) {
                throw new IllegalArgumentException(e);
            }
            return this;
        }

        /**
         * Add an option to the command line. The values of the option are stored.
         *
         * @param opt the processed option.
         *
         * @return this Builder instance for method chaining.
         */
        public Builder addOption(final Option opt) {
            builderObj.invokeMember("add_option", opt);
            return this;
        }

        public CommandLine build() {
            Value cmdLineObj;
            cmdLineObj = builderObj.invokeMember("build");

            return CommandLine.create(cmdLineObj);
        }
    }

    /**
     * Creates a command line.
     */
    protected CommandLine() {
        cmdLineObj = clz.newInstance();
    }

    /**
     * Creates a CommandLine with Python's object value
     * 
     * @param v
     * @throws IllegalArgumentException
     */
    public CommandLine(Value v) throws IllegalArgumentException {
        cmdLineObj = v;
    }

    /**
     * Equivalent instance of Python's Value object
     * 
     * @return Value
     */
    public Value getPythonObject() {
        return cmdLineObj;
    }

    /**
     * Cache for wrappers to python objects
     */
    private static Map<Value, CommandLine> cache = new HashMap<>();

    /**
     * @param foreignCmdLine
     * @return
     */
    public static CommandLine create(final Value foreignCmdLine) {
        if (foreignCmdLine.isNull()) {
            return null;
        }

        return cache.computeIfAbsent(foreignCmdLine, CommandLine::new);
    }

    /**
     * Add left-over unrecognized option/argument.
     *
     * @param arg the unrecognized option/argument.
     */
    protected void addArg(final String arg) {
        cmdLineObj.invokeMember("add_arg", arg);

    }

    /**
     * Add an option to the command line. The values of the option are stored.
     *
     * @param opt the processed option.
     */
    protected void addOption(final Option opt) {
        cmdLineObj.invokeMember("add_option", opt);

    }

    /**
     * Retrieve any left-over non-recognized options and arguments
     *
     * @return remaining items passed in but not parsed as a {@code List}.
     */
    public List<String> getArgList() {
        return cmdLineObj.invokeMember("get_arg_list").as(List.class);
    }

    /**
     * Retrieve any left-over non-recognized options and arguments
     *
     * @return remaining items passed in but not parsed as an array.
     */
    public String[] getArgs() {
        return cmdLineObj.invokeMember("get_args").as(String[].class);
    }

    /**
     * Return the {@code Object} type of this {@code Option}.
     *
     * @deprecated due to System.err message. Instead use getParsedOptionValue(char)
     * @param opt the name of the option.
     * @return the type of opt.
     */
    @Deprecated
    public Object getOptionObject(final char opt) {
        return getOptionObject(String.valueOf(opt));
    }

    /**
     * Return the {@code Object} type of this {@code Option}.
     *
     * @param opt the name of the option.
     * @return the type of this {@code Option}.
     * @deprecated due to System.err message. Instead use
     *             getParsedOptionValue(String)
     */
    @Deprecated
    public Object getOptionObject(final String opt) {
        try {
            Object value = cmdLineObj.invokeMember("get_option_object", opt).as(Object.class);
            if (value instanceof Number && !(value instanceof Double)) {
                return ((Number) value).longValue();
            }
            return value;
        } catch (PolyglotException e) {
            String exceptionType = e.getGuestObject().getMember("__class__").getMember("__name__").asString();
            if (exceptionType.equals("ValueError")) {
                throw new UnsupportedOperationException(e.getMessage());
            }
            return null;
        }
    }

    /**
     * Retrieve the map of values associated to the option. This is convenient for
     * options specifying Java properties like
     * <code>-Dparam1=value1
     * -Dparam2=value2</code>. The first argument of the option is the key, and the
     * 2nd argument is the value. If the option
     * has only one argument ({@code -Dfoo}) it is considered as a boolean flag and
     * the value is {@code "true"}.
     *
     * @param option name of the option.
     * @return The Properties mapped by the option, never {@code null} even if the
     *         option doesn't exists.
     * @since 1.5.0
     */
    public Properties getOptionProperties(final Option option) {
        return IntegrationUtil.valueHashToProperties(cmdLineObj.invokeMember("get_option_properties", option));
    }

    /**
     * Retrieve the map of values associated to the option. This is convenient for
     * options specifying Java properties like
     * <code>-Dparam1=value1
     * -Dparam2=value2</code>. The first argument of the option is the key, and the
     * 2nd argument is the value. If the option
     * has only one argument ({@code -Dfoo}) it is considered as a boolean flag and
     * the value is {@code "true"}.
     *
     * @param opt name of the option.
     * @return The Properties mapped by the option, never {@code null} even if the
     *         option doesn't exists.
     * @since 1.2
     */
    public Properties getOptionProperties(final String opt) {
        return IntegrationUtil.valueHashToProperties(cmdLineObj.invokeMember("get_option_properties", opt));
    }

    /**
     * Gets an array of the processed {@link Option}s.
     *
     * @return an array of the processed {@link Option}s.
     */
    public Option[] getOptions() {
        return IntegrationUtil.valueArrayToArray(cmdLineObj.invokeMember("get_options"), Option.class);
    }

    /**
     * Retrieve the first argument, if any, of this option.
     *
     * @param opt the character name of the option.
     * @return Value of the argument if option is set, and has an argument,
     *         otherwise null.
     */
    public String getOptionValue(final char opt) {
        return cmdLineObj.invokeMember("get_option_value", String.valueOf(opt)).asString();
    }

    /**
     * Retrieve the argument, if any, of an option.
     *
     * @param opt          character name of the option
     * @param defaultValue is the default value to be returned if the option is not
     *                     specified.
     * @return Value of the argument if option is set, and has an argument,
     *         otherwise {@code defaultValue}.
     */
    public String getOptionValue(final char opt, final String defaultValue) {
        return cmdLineObj.invokeMember("get_option_value", String.valueOf(opt), defaultValue).asString();
    }

    /**
     * Retrieve the first argument, if any, of this option.
     *
     * @param option the name of the option.
     * @return Value of the argument if option is set, and has an argument,
     *         otherwise null.
     * @since 1.5.0
     */
    public String getOptionValue(final Option option) {
        return cmdLineObj.invokeMember("get_option_value", option).asString();
    }

    /**
     * Retrieve the first argument, if any, of an option.
     *
     * @param option       name of the option.
     * @param defaultValue is the default value to be returned if the option is not
     *                     specified.
     * @return Value of the argument if option is set, and has an argument,
     *         otherwise {@code defaultValue}.
     * @since 1.5.0
     */
    public String getOptionValue(final Option option, final String defaultValue) {
        return cmdLineObj.invokeMember("get_option_value", option).asString();
    }

    /**
     * Retrieve the first argument, if any, of this option.
     *
     * @param opt the name of the option.
     * @return Value of the argument if option is set, and has an argument,
     *         otherwise null.
     */
    public String getOptionValue(final String opt) {
        return cmdLineObj.invokeMember("get_option_value", opt).asString();
    }

    /**
     * Retrieve the first argument, if any, of an option.
     *
     * @param opt          name of the option.
     * @param defaultValue is the default value to be returned if the option is not
     *                     specified.
     * @return Value of the argument if option is set, and has an argument,
     *         otherwise {@code defaultValue}.
     */
    public String getOptionValue(final String opt, final String defaultValue) {
        return cmdLineObj.invokeMember("get_option_value", opt, defaultValue).asString();
    }

    /**
     * Retrieves the array of values, if any, of an option.
     *
     * @param opt character name of the option.
     * @return Values of the argument if option is set, and has an argument,
     *         otherwise null.
     */
    public String[] getOptionValues(final char opt) {
        return cmdLineObj.invokeMember("get_option_values", String.valueOf(opt)).as(String[].class);
    }

    /**
     * Retrieves the array of values, if any, of an option.
     *
     * @param option string name of the option.
     * @return Values of the argument if option is set, and has an argument,
     *         otherwise null.
     * @since 1.5.0
     */
    public String[] getOptionValues(final Option option) {
        return cmdLineObj.invokeMember("get_option_values", option).as(String[].class);
    }

    /**
     * Retrieves the array of values, if any, of an option.
     *
     * @param opt string name of the option.
     * @return Values of the argument if option is set, and has an argument,
     *         otherwise null.
     */
    public String[] getOptionValues(final String opt) {
        return cmdLineObj.invokeMember("get_option_values", opt).as(String[].class);
    }

    /**
     * Return a version of this {@code Option} converted to a particular type.
     *
     * @param opt the name of the option.
     * @return the value parsed into a particular object.
     * @throws ParseException if there are problems turning the option value into
     *                        the desired type
     * @see PatternOptionBuilder
     * @since 1.5.0
     */
    public Object getParsedOptionValue(final char opt) throws ParseException {
        try {
            return cmdLineObj.invokeMember("get_parsed_option_value", String.valueOf(opt)).as(Object.class);
        } catch (PolyglotException e) {
            throw new ParseException(e.getMessage());
        }
    }

    /**
     * Return a version of this {@code Option} converted to a particular type.
     *
     * @param option the name of the option.
     * @return the value parsed into a particular object.
     * @throws ParseException if there are problems turning the option value into
     *                        the desired type
     * @see PatternOptionBuilder
     * @since 1.5.0
     */
    public Object getParsedOptionValue(final Option option) throws ParseException {
        try {
            return cmdLineObj.invokeMember("get_parsed_option_value", option).as(Object.class);
        } catch (PolyglotException e) {
            throw new ParseException(e.getMessage());
        }
    }

    /**
     * Return a version of this {@code Option} converted to a particular type.
     *
     * @param opt the name of the option.
     * @return the value parsed into a particular object.
     * @throws ParseException if there are problems turning the option value into
     *                        the desired type
     * @see PatternOptionBuilder
     * @since 1.2
     */
    public Object getParsedOptionValue(final String opt) throws ParseException {
        try {
            return cmdLineObj.invokeMember("get_parsed_option_value", opt).as(Object.class);
        } catch (PolyglotException e) {
            throw new ParseException(e.getMessage());
        }
    }

    /**
     * jkeyes - commented out until it is implemented properly
     * <p>
     * Dump state, suitable for debugging.
     * </p>
     *
     * @return Stringified form of this object.
     */

    /*
     * public String toString() { StringBuilder buf = new StringBuilder();
     *
     * buf.append("[ CommandLine: [ options: "); buf.append(options.toString());
     * buf.append(" ] [ args: ");
     * buf.append(args.toString()); buf.append(" ] ]");
     *
     * return buf.toString(); }
     */

    /**
     * Tests to see if an option has been set.
     *
     * @param opt character name of the option.
     * @return true if set, false if not.
     */
    public boolean hasOption(final char opt) {
        return cmdLineObj.invokeMember("has_option", opt).asBoolean();
    }

    /**
     * Tests to see if an option has been set.
     *
     * @param opt the option to check.
     * @return true if set, false if not.
     * @since 1.5.0
     */
    public boolean hasOption(final Option opt) {
        return cmdLineObj.invokeMember("has_option", opt).asBoolean();
    }

    /**
     * Tests to see if an option has been set.
     *
     * @param opt Short name of the option.
     * @return true if set, false if not.
     */
    public boolean hasOption(final String opt) {
        return cmdLineObj.invokeMember("has_option", opt).asBoolean();
    }

    /**
     * Returns an iterator over the Option members of CommandLine.
     *
     * @return an {@code Iterator} over the processed {@link Option} members of this
     *         {@link CommandLine}.
     */
    public Iterator<Option> iterator() {
        Value iterObj = cmdLineObj.invokeMember("iterator");
        List<Option> optionList = new ArrayList<>();
        try {
            while (true) {
                optionList.add(Option.create(iterObj.invokeMember("__next__")));
            }
        } catch (PolyglotException e) {
            return optionList.iterator();
        }
    }
}
