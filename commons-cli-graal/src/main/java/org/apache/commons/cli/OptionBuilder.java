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

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;
/**
 * OptionBuilder allows the user to create Options using descriptive methods.
 * <p>
 * Details on the Builder pattern can be found at
 * <a href="http://c2.com/cgi-bin/wiki?BuilderPattern">http://c2.com/cgi-bin/wiki?BuilderPattern</a>.
 * <p>
 * This class is NOT thread safe. See <a href="https://issues.apache.org/jira/browse/CLI-209">CLI-209</a>
 *
 * @since 1.0
 * @deprecated since 1.3, use {@link Option#builder(String)} instead
 */
@Deprecated
public final class OptionBuilder {

    /** Option builder instance */
    private static final OptionBuilder INSTANCE = new OptionBuilder();

    /** A reference to the python class */
    private static Value clz = ContextInitializer.getPythonClass("option_builder.py", "OptionBuilder");

    /**
     * Creates an Option using the current settings
     *
     * @return the Option instance
     * @throws IllegalArgumentException if {@code longOpt} has not been set.
     */
    public static Option create() throws IllegalArgumentException {
        try {
            Value obj = clz.invokeMember("create");
            return Option.create(obj);
        } catch (PolyglotException e) {
            throw new IllegalArgumentException(e.getMessage());
        }
    }

    /**
     * Creates an Option using the current settings and with the specified Option {@code char}.
     *
     * @param opt the character representation of the Option
     * @return the Option instance
     * @throws IllegalArgumentException if {@code opt} is not a valid character. See Option.
     */
    public static Option create(final char opt) throws IllegalArgumentException {
        return create(String.valueOf(opt));
    }

    /**
     * Creates an Option using the current settings and with the specified Option {@code char}.
     *
     * @param opt the {@code java.lang.String} representation of the Option
     * @return the Option instance
     * @throws IllegalArgumentException if {@code opt} is not a valid character. See Option.
     */
    public static Option create(final String opt) throws IllegalArgumentException {
        try {
            Value obj = clz.invokeMember("create", opt);
            return Option.create(obj);
        } catch (PolyglotException e) {
            throw new IllegalArgumentException(e.getMessage());
        }
    }

    /**
     * The next Option created will require an argument value.
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasArg() {
        clz.invokeMember("has_arg");

        return INSTANCE;
    }

    /**
     * The next Option created will require an argument value if {@code hasArg} is true.
     *
     * @param hasArg if true then the Option has an argument value
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasArg(final boolean hasArg) {
        clz.invokeMember("has_arg", hasArg);

        return INSTANCE;
    }

    /**
     * The next Option created can have unlimited argument values.
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasArgs() {
        clz.invokeMember("has_args");

        return INSTANCE;
    }

    /**
     * The next Option created can have {@code num} argument values.
     *
     * @param num the number of args that the option can have
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasArgs(final int num) {
        clz.invokeMember("has_args", num);

        return INSTANCE;
    }

    /**
     * The next Option can have an optional argument.
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasOptionalArg() {
        clz.invokeMember("has_optional_arg");

        return INSTANCE;
    }

    /**
     * The next Option can have an unlimited number of optional arguments.
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasOptionalArgs() {
        clz.invokeMember("has_optional_args");

        return INSTANCE;
    }

    /**
     * The next Option can have the specified number of optional arguments.
     *
     * @param numArgs - the maximum number of optional arguments the next Option created can have.
     * @return the OptionBuilder instance
     */
    public static OptionBuilder hasOptionalArgs(final int numArgs) {
        clz.invokeMember("has_optional_args", numArgs);

        return INSTANCE;
    }

    /**
     * The next Option created will be required.
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder isRequired() {
        clz.invokeMember("is_required");

        return INSTANCE;
    }

    /**
     * The next Option created will be required if {@code required} is true.
     *
     * @param newRequired if true then the Option is required
     * @return the OptionBuilder instance
     */
    public static OptionBuilder isRequired(final boolean newRequired) {
        clz.invokeMember("is_required", newRequired);

        return INSTANCE;
    }

    /**
     * The next Option created will have the specified argument value name.
     *
     * @param name the name for the argument value
     * @return the OptionBuilder instance
     */
    public static OptionBuilder withArgName(final String name) {
        clz.invokeMember("with_arg_name", name);

        return INSTANCE;
    }

    /**
     * The next Option created will have the specified description
     *
     * @param newDescription a description of the Option's purpose
     * @return the OptionBuilder instance
     */
    public static OptionBuilder withDescription(final String newDescription) {
        clz.invokeMember("with_description", newDescription);

        return INSTANCE;
    }

    /**
     * The next Option created will have the following long option value.
     *
     * @param newLongopt the long option value
     * @return the OptionBuilder instance
     */
    public static OptionBuilder withLongOpt(final String newLongopt) {
        clz.invokeMember("with_long_opt", newLongopt);

        return INSTANCE;
    }

    /**
     * The next Option created will have a value that will be an instance of {@code type}.
     *
     * @param newType the type of the Options argument value
     * @return the OptionBuilder instance
     * @since 1.3
     */
    public static OptionBuilder withType(final Class<?> newType) {
        clz.invokeMember("with_type", newType);

        return INSTANCE;
    }

    /**
     * The next Option created will have a value that will be an instance of {@code type}.
     * <p>
     * <b>Note:</b> this method is kept for binary compatibility and the input type is supposed to be a {@link Class}
     * object.
     *
     * @param newType the type of the Options argument value
     * @return the OptionBuilder instance
     * @deprecated since 1.3, use {@link #withType(Class)} instead
     */
    @Deprecated
    public static OptionBuilder withType(final Object newType) {
        return withType((Class<?>) newType);
    }

    /**
     * The next Option created uses '{@code =}' as a means to separate argument values.
     *
     * <b>Example:</b>
     *
     * <pre>
     * Option opt = OptionBuilder.withValueSeparator().create('D');
     *
     * CommandLine line = parser.parse(args);
     * String propertyName = opt.getValue(0);
     * String propertyValue = opt.getValue(1);
     * </pre>
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder withValueSeparator() {
        clz.invokeMember("with_value_separator");

        return INSTANCE;
    }

    /**
     * The next Option created uses {@code sep} as a means to separate argument values.
     * <p>
     * <b>Example:</b>
     *
     * <pre>
     * Option opt = OptionBuilder.withValueSeparator('=').create('D');
     *
     * String args = "-Dkey=value";
     * CommandLine line = parser.parse(args);
     * String propertyName = opt.getValue(0); // will be "key"
     * String propertyValue = opt.getValue(1); // will be "value"
     * </pre>
     *
     * @param sep The value separator to be used for the argument values.
     *
     * @return the OptionBuilder instance
     */
    public static OptionBuilder withValueSeparator(final char sep) {
        clz.invokeMember("with_value_separator", sep);

        return INSTANCE;
    }

    /**
     * private constructor to prevent instances being created
     */
    private OptionBuilder() {
        // hide the constructor
    }
}
