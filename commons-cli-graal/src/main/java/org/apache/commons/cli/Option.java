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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * Describes a single command-line option. It maintains information regarding the short-name of the option, the
 * long-name, if any exists, a flag indicating if an argument is required for this option, and a self-documenting
 * description of the option.
 * <p>
 * An Option is not created independently, but is created through an instance of {@link Options}. An Option is required
 * to have at least a short or a long-name.
 * </p>
 * <p>
 * <b>Note:</b> once an {@link Option} has been added to an instance of {@link Options}, its required flag cannot be
 * changed.
 * </p>
 *
 * @see org.apache.commons.cli.Options
 * @see org.apache.commons.cli.CommandLine
 */
public class Option implements Cloneable, Serializable {

     /**
     * Contains a reference to the Python class.
     */
    private static Value clz;

    /**
     * Contains a reference to the embedded Python object.
     */
    private Value optionObj;

    static {
        clz = ContextInitializer.getPythonClass("option.py", "Option");
    }

    public Value getPythonObject() {
        return optionObj;
    }

    /** Cache for wrappers to python objects  */
    private static Map<Value, Option> cache = new HashMap<>();

    public static Option create(final Value foreignOption) {
        if (foreignOption.isNull()) {
            return null;
        }
        return cache.computeIfAbsent(foreignOption, Option::new);
    }

    /* We should not copy this method in another class */
    /* I am keeping only as a reminder for an alternative we didn't pursue */
    /* Instead of using "cache", we could have tried "equals" */
    /*
    @Override
    public boolean equals(Object o) {
        if (o == null || o.getClass() != Option.class) {
            return false;
        }
        return optionObj.equals(((Option)o).optionObj);
    }
    */

    /**
     * A nested builder class to create {@code Option} instances using descriptive methods.
     * <p>
     * Example usage:
     * </p>
     *
     * <pre>
     * Option option = Option.builder("a").required(true).longOpt("arg-name").build();
     * </pre>
     *
     * @since 1.3
     */
    public static final class Builder {
        /**
         * Contains a reference to the Builder Python class.
         * 
         */
        private static Value builderClz = ContextInitializer.getPythonClass("option.py", "Option").getMember("Builder");;

        /**
         * Contains a reference to the embedded Builder Python object.
         */
        private Value builderObj;

        /**
         * Constructs a new {@code Builder} with the minimum required parameters for an {@code Option} instance.
         *
         * @param option short representation of the option
         * @throws IllegalArgumentException if there are any non valid Option characters in {@code opt}
         */
        private Builder(final String option) throws IllegalArgumentException {
            try {
                builderObj = builderClz.execute(option);
            } catch (PolyglotException e) {
                throw new IllegalArgumentException(e);
            }
        }

        /**
         * Sets the display name for the argument value.
         *
         * @param argName the display name for the argument value.
         * @return this builder, to allow method chaining
         */
        public Builder argName(final String argName) {
            builderObj.invokeMember("arg_name", argName);
            return this;
        }

        /**
         * Constructs an Option with the values declared by this {@link Builder}.
         *
         * @return the new {@link Option}
         * @throws IllegalArgumentException if neither {@code opt} or {@code longOpt} has been set
         */
        public Option build() {
            try {
                return Option.create(builderObj.invokeMember("build"));
            } catch (PolyglotException e) {
                throw new IllegalArgumentException(e);
            }
        }

        /**
         * Sets the description for this option.
         *
         * @param description the description of the option.
         * @return this builder, to allow method chaining
         */
        public Builder desc(final String description) {
            builderObj.invokeMember("desc", description);
            return this;
        }

        /**
         * Indicates that the Option will require an argument.
         *
         * @return this builder, to allow method chaining
         */
        public Builder hasArg() {
            return hasArg(true);
        }

        /**
         * Indicates if the Option has an argument or not.
         *
         * @param hasArg specifies whether the Option takes an argument or not
         * @return this builder, to allow method chaining
         */
        public Builder hasArg(final boolean hasArg) {
            builderObj.invokeMember("has_arg", hasArg);
            return this;
        }

        /**
         * Indicates that the Option can have unlimited argument values.
         *
         * @return this builder, to allow method chaining
         */
        public Builder hasArgs() {
            builderObj.invokeMember("has_args");
            return this;
        }

        /**
         * Sets the long name of the Option.
         *
         * @param longOpt the long name of the Option
         * @return this builder, to allow method chaining
         */
        public Builder longOpt(final String longOpt) {
            builderObj.invokeMember("long_opt", longOpt);
            return this;
        }

        /**
         * Sets the number of argument values the Option can take.
         *
         * @param numberOfArgs the number of argument values
         * @return this builder, to allow method chaining
         */
        public Builder numberOfArgs(final int numberOfArgs) {
            builderObj.invokeMember("number_of_args", numberOfArgs);
            return this;
        }

        /**
         * Sets the name of the Option.
         *
         * @param option the name of the Option
         * @return this builder, to allow method chaining
         * @throws IllegalArgumentException if there are any non valid Option characters in {@code opt}
         * @since 1.5.0
         */
        public Builder option(final String option) throws IllegalArgumentException {
            try {
                builderObj.invokeMember("option", option);
                return this;
            } catch (PolyglotException e) {
                throw new IllegalArgumentException(e);
            }
        }

        /**
         * Sets whether the Option can have an optional argument.
         *
         * @param isOptional specifies whether the Option can have an optional argument.
         * @return this builder, to allow method chaining
         */
        public Builder optionalArg(final boolean isOptional) {
            builderObj.invokeMember("optional_arg", isOptional);
            return this;
        }

        /**
         * Marks this Option as required.
         *
         * @return this builder, to allow method chaining
         */
        public Builder required() {
            return required(true);
        }

        /**
         * Sets whether the Option is mandatory.
         *
         * @param required specifies whether the Option is mandatory
         * @return this builder, to allow method chaining
         */
        public Builder required(final boolean required) {
            builderObj.invokeMember("required", required);
            return this;
        }

        /**
         * Sets the type of the Option.
         *
         * @param type the type of the Option
         * @return this builder, to allow method chaining
         */
        public Builder type(final Class<?> type) {
            builderObj.invokeMember("type", type);
            return this;
        }

        /**
         * The Option will use '=' as a means to separate argument value.
         *
         * @return this builder, to allow method chaining
         */
        public Builder valueSeparator() {
            return valueSeparator('=');
        }

        /**
         * The Option will use {@code sep} as a means to separate argument values.
         * <p>
         * <b>Example:</b>
         * </p>
         *
         * <pre>
         * Option opt = Option.builder("D").hasArgs().valueSeparator('=').build();
         * Options options = new Options();
         * options.addOption(opt);
         * String[] args = {"-Dkey=value"};
         * CommandLineParser parser = new DefaultParser();
         * CommandLine line = parser.parse(options, args);
         * String propertyName = line.getOptionValues("D")[0]; // will be "key"
         * String propertyValue = line.getOptionValues("D")[1]; // will be "value"
         * </pre>
         *
         * @param sep The value separator.
         * @return this builder, to allow method chaining
         */
        public Builder valueSeparator(final char sep) {
            builderObj.invokeMember("value_separator", sep);
            return this;
        }
    }

    /** Specifies the number of argument values has not been specified */
    public static final int UNINITIALIZED = -1;

    /** Specifies the number of argument values is infinite */
    public static final int UNLIMITED_VALUES = -2;

    /** The serial version UID. */
    private static final long serialVersionUID = 1L;

    /**
     * Returns a {@link Builder} to create an {@link Option} using descriptive methods.
     *
     * @return a new {@link Builder} instance
     * @since 1.3
     */
    public static Builder builder() {
        return builder(null);
    }

    /**
     * Returns a {@link Builder} to create an {@link Option} using descriptive methods.
     *
     * @param option short representation of the option
     * @return a new {@link Builder} instance
     * @throws IllegalArgumentException if there are any non valid Option characters in {@code opt}
     * @since 1.3
     */
    public static Builder builder(final String option) {
        return new Builder(option);
    }

    /**
     * Creates an Option using the specified parameters.
     *
     * @param option short representation of the option
     * @param hasArg specifies whether the Option takes an argument or not
     * @param description describes the function of the option
     *
     * @throws IllegalArgumentException if there are any non valid Option characters in {@code opt}.
     */
    public Option(final String option, final boolean hasArg, final String description) throws IllegalArgumentException {
        this(option, null, hasArg, description);
    }

    /**
     * Creates an Option using the specified parameters. The option does not take an argument.
     *
     * @param option short representation of the option
     * @param description describes the function of the option
     *
     * @throws IllegalArgumentException if there are any non valid Option characters in {@code opt}.
     */
    public Option(final String option, final String description) throws IllegalArgumentException {
        this(option, null, false, description);
    }

    /**
     * Creates an Option using the specified parameters.
     *
     * @param option short representation of the option
     * @param longOption the long representation of the option
     * @param hasArg specifies whether the Option takes an argument or not
     * @param description describes the function of the option
     *
     * @throws IllegalArgumentException if there are any non valid Option characters in {@code opt}.
     */
    public Option(final String option, final String longOption, final boolean hasArg, final String description)
            throws IllegalArgumentException {
        try {
            optionObj = clz.execute(option, longOption, hasArg, description);
        } catch (PolyglotException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Special constructor for building {@link Option} instances with a python object.
     * 
     * @param v the python object
     * @throws IllegalArgumentException if there are any non valid Option characters
     */

    public Option(Value v) throws IllegalArgumentException {
        optionObj = v;
    }

    /**
     * Tells if the option can accept more arguments.
     *
     * @return false if the maximum number of arguments is reached
     * @since 1.3
     */
    boolean acceptsArg() {
        return optionObj.invokeMember("accepts_arg").asBoolean();
    }

    /**
     * Add the value to this Option. If the number of arguments is greater than zero and there is enough space in the list
     * then add the value. Otherwise, throw a runtime exception.
     *
     * @param value The value to be added to this Option
     *
     * @since 1.0.1
     */
    private void add(final String value) {
        try {
            optionObj.invokeMember("add", value);
        } catch (PolyglotException e) {
            throw new RuntimeException("Cannot add value, list full.");
        }
    }

    /**
     * This method is not intended to be used. It was a piece of internal API that was made public in 1.0. It currently
     * throws an UnsupportedOperationException.
     *
     * @param value the value to add
     * @return always throws an {@link UnsupportedOperationException}
     * @throws UnsupportedOperationException always
     * @deprecated Unused.
     */
    @Deprecated
    public boolean addValue(final String value) {
        throw new UnsupportedOperationException(
            "The addValue method is not intended for client use. " + "Subclasses should use the addValueForProcessing method instead. ");
    }

    /**
     * Adds the specified value to this Option.
     *
     * @param value is a/the value of this Option
     */
    void addValueForProcessing(final String value) {
        try {
            optionObj.invokeMember("add_value_for_processing", value);
        } catch (PolyglotException e) {
            throw new RuntimeException("NO_ARGS_ALLOWED");
        }
    }

    /**
     * Clear the Option values. After a parse is complete, these are left with data in them and they need clearing if
     * another parse is done.
     *
     * See: <a href="https://issues.apache.org/jira/browse/CLI-71">CLI-71</a>
     */
    void clearValues() {
        optionObj.invokeMember("clear_values");
    }

    /**
     * A rather odd clone method - due to incorrect code in 1.0 it is public and in 1.1 rather than throwing a
     * CloneNotSupportedException it throws a RuntimeException so as to maintain backwards compat at the API level.
     *
     * After calling this method, it is very likely you will want to call clearValues().
     *
     * @return a clone of this Option instance
     * @throws RuntimeException if a {@link CloneNotSupportedException} has been thrown by {@code super.clone()}
     */
    @Override
    public Object clone() {
        try {
            Option option = (Option) super.clone();
            option.optionObj = optionObj.invokeMember("clone");
            return option;
        } catch (final CloneNotSupportedException cnse) {
            throw new RuntimeException("A CloneNotSupportedException was thrown: " + cnse.getMessage());
        }
    }

    @Override
    public boolean equals(final Object obj) {
        if (obj instanceof Option) {
            return optionObj.invokeMember("equals", obj).asBoolean();
        }
        return false;
    }

    /**
     * Gets the display name for the argument value.
     *
     * @return the display name for the argument value.
     */
    public String getArgName() {
        return optionObj.invokeMember("get_arg_name").asString();
    }

    /**
     * Gets the number of argument values this Option can take.
     *
     * <p>
     * A value equal to the constant {@link #UNINITIALIZED} (= -1) indicates the number of arguments has not been specified.
     * A value equal to the constant {@link #UNLIMITED_VALUES} (= -2) indicates that this options takes an unlimited amount
     * of values.
     * </p>
     *
     * @return num the number of argument values
     * @see #UNINITIALIZED
     * @see #UNLIMITED_VALUES
     */
    public int getArgs() {
        return optionObj.invokeMember("get_args").asInt();
    }

    /**
     * Gets the self-documenting description of this Option
     *
     * @return The string description of this option
     */
    public String getDescription() {
        return optionObj.invokeMember("get_description").asString();
    }

    /**
     * Gets the id of this Option. This is only set when the Option shortOpt is a single character. This is used for
     * switch statements.
     *
     * @return the id of this Option
     */
    public int getId() {
        return optionObj.invokeMember("get_id").asString().charAt(0);
    }

    /**
     * Gets the 'unique' Option identifier.
     *
     * @return the 'unique' Option identifier
     */
    String getKey() {
        // if 'opt' is null, then it is a 'long' option
        return optionObj.invokeMember("get_key").asString();
    }

    /**
     * Gets the long name of this Option.
     *
     * @return Long name of this option, or null, if there is no long name
     */
    public String getLongOpt() {
        return optionObj.invokeMember("get_long_opt").asString();
    }

    /**
     * Gets the name of this Option.
     *
     * It is this String which can be used with {@link CommandLine#hasOption(String opt)} and
     * {@link CommandLine#getOptionValue(String opt)} to check for existence and argument.
     *
     * @return The name of this option
     */
    public String getOpt() {
        return optionObj.invokeMember("get_opt").asString();
    }

    /**
     * Gets the type of this Option.
     *
     * @return The type of this option
     */
    public Object getType() {
        return optionObj.invokeMember("get_type").as(Object.class);
    }

    /**
     * Gets the specified value of this Option or {@code null} if there is no value.
     *
     * @return the value/first value of this Option or {@code null} if there is no value.
     */
    public String getValue() {
        return optionObj.invokeMember("get_value").asString();
    }

    /**
     * Gets the specified value of this Option or {@code null} if there is no value.
     *
     * @param index The index of the value to be returned.
     *
     * @return the specified value of this Option or {@code null} if there is no value.
     *
     * @throws IndexOutOfBoundsException if index is less than 1 or greater than the number of the values for this Option.
     */
    public String getValue(final int index) throws IndexOutOfBoundsException {
        return optionObj.invokeMember("get_value", index).asString();
    }

    /**
     * Gets the value/first value of this Option or the {@code defaultValue} if there is no value.
     *
     * @param defaultValue The value to be returned if there is no value.
     *
     * @return the value/first value of this Option or the {@code defaultValue} if there are no values.
     */
    public String getValue(final String defaultValue) {
        return optionObj.invokeMember("get_value", defaultValue).asString();
    }

    /**
     * Gets the values of this Option as a String array or null if there are no values
     *
     * @return the values of this Option as a String array or null if there are no values
     */
    public String[] getValues() {
        return optionObj.invokeMember("get_values").as(String[].class);
    }

    /**
     * Gets the value separator character.
     *
     * @return the value separator character.
     */
    public char getValueSeparator() {
        String sep = optionObj.invokeMember("get_value_separator").asString();
        if (sep.isEmpty()) { 
            return '\0';
        }
        return sep.charAt(0);
    }

    /**
     * Gets the values of this Option as a List or null if there are no values.
     *
     * @return the values of this Option as a List or null if there are no values
     */
    public List<String> getValuesList() {
        return optionObj.invokeMember("get_values_list").as(List.class);
    }

    /**
     * Query to see if this Option requires an argument
     *
     * @return boolean flag indicating if an argument is required
     */
    public boolean hasArg() {
        return optionObj.invokeMember("has_arg").asBoolean();
    }

    /**
     * Returns whether the display name for the argument value has been set.
     *
     * @return if the display name for the argument value has been set.
     */
    public boolean hasArgName() {
        return optionObj.invokeMember("has_arg_name").asBoolean();
    }

    /**
     * Query to see if this Option can take many values.
     *
     * @return boolean flag indicating if multiple values are allowed
     */
    public boolean hasArgs() {
        return optionObj.invokeMember("has_args").asBoolean();
    }

    @Override
    public int hashCode() {
        return (int) optionObj.invokeMember("hash_code").asLong();
    }

    /**
     * Query to see if this Option has a long name
     *
     * @return boolean flag indicating existence of a long name
     */
    public boolean hasLongOpt() {
        return optionObj.invokeMember("has_long_opt").asBoolean();
    }

    /**
     * Returns whether this Option has any values.
     *
     * @return whether this Option has any values.
     */
    private boolean hasNoValues() {
        return optionObj.invokeMember("has_no_values").asBoolean();
    }

    /**
     * @return whether this Option can have an optional argument
     */
    public boolean hasOptionalArg() {
        return optionObj.invokeMember("has_optional_arg").asBoolean();
    }

    /**
     * Return whether this Option has specified a value separator.
     *
     * @return whether this Option has specified a value separator.
     * @since 1.1
     */
    public boolean hasValueSeparator() {
        return optionObj.invokeMember("has_value_separator").asBoolean();
    }

    /**
     * Query to see if this Option is mandatory
     *
     * @return boolean flag indicating whether this Option is mandatory
     */
    public boolean isRequired() {
        return optionObj.invokeMember("is_required").asBoolean();
    }

    /**
     * Processes the value. If this Option has a value separator the value will have to be parsed into individual tokens.
     * When n-1 tokens have been processed and there are more value separators in the value, parsing is ceased and the
     * remaining characters are added as a single token.
     *
     * @param value The String to be processed.
     *
     * @since 1.0.1
     */
    private void processValue(String value) {
        optionObj.invokeMember("process_value", value);
    }

    /**
     * Tells if the option requires more arguments to be valid.
     *
     * @return false if the option doesn't require more arguments
     * @since 1.3
     */
    boolean requiresArg() {
        return optionObj.invokeMember("requires_arg").asBoolean();
    }

    /**
     * Sets the display name for the argument value.
     *
     * @param argName the display name for the argument value.
     */
    public void setArgName(final String argName) {
        optionObj.invokeMember("set_arg_name", argName);
    }

    /**
     * Sets the number of argument values this Option can take.
     *
     * @param num the number of argument values
     */
    public void setArgs(final int num) {
        optionObj.invokeMember("set_args", num);
    }

    /**
     * Sets the self-documenting description of this Option
     *
     * @param description The description of this option
     * @since 1.1
     */
    public void setDescription(final String description) {
        optionObj.invokeMember("set_description", description);
    }

    /**
     * Sets the long name of this Option.
     *
     * @param longOpt the long name of this Option
     */
    public void setLongOpt(final String longOpt) {
        optionObj.invokeMember("set_long_opt", longOpt);
    }

    /**
     * Sets whether this Option can have an optional argument.
     *
     * @param optionalArg specifies whether the Option can have an optional argument.
     */
    public void setOptionalArg(final boolean optionalArg) {
        optionObj.invokeMember("set_optional_arg", optionalArg);
    }

    /**
     * Sets whether this Option is mandatory.
     *
     * @param required specifies whether this Option is mandatory
     */
    public void setRequired(final boolean required) {
        optionObj.invokeMember("set_required", required);
    }

    /**
     * Sets the type of this Option.
     *
     * @param type the type of this Option
     * @since 1.3
     */
    public void setType(final Class<?> type) {
        optionObj.invokeMember("set_type", type);
    }

    /**
     * Sets the type of this Option.
     * <p>
     * <b>Note:</b> this method is kept for binary compatibility and the input type is supposed to be a {@link Class}
     * object.
     * </p>
     *
     * @param type the type of this Option
     * @deprecated since 1.3, use {@link #setType(Class)} instead
     */
    @Deprecated
    public void setType(final Object type) {
        setType((Class<?>) type);
    }

    /**
     * Sets the value separator. For example if the argument value was a Java property, the value separator would be '='.
     *
     * @param sep The value separator.
     */
    public void setValueSeparator(final char sep) {
        optionObj.invokeMember("set_value_separator", sep);
    }

    /**
     * Dump state, suitable for debugging.
     *
     * @return Stringified form of this object
     */
    @Override
    public String toString() {
        return optionObj.invokeMember("to_string").asString();
    }
}
