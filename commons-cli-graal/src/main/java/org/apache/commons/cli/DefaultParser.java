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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * Default parser.
 *
 * @since 1.3
 */
public class DefaultParser implements CommandLineParser {

    /**
     * Contains a reference to the python class
     */
    private static Value clz = ContextInitializer.getPythonClass("default_parser.py", "DefaultParser");;

    /**
     * Contains a reference to the embedded Python Object
     */
    private Value defaultParserObj;

    public Value getPythonObject() {
        return defaultParserObj;
    }

    /** Cache for wrappers to python objects  */
    private static Map<Value, DefaultParser> cache = new HashMap<>();

    public static DefaultParser create(final Value foreignDefaultParser) {
        if (foreignDefaultParser.isNull()) {
            return null;
        }
        return cache.computeIfAbsent(foreignDefaultParser, DefaultParser::new);
    }

    /**
     * A nested builder class to create {@code DefaultParser} instances
     * using descriptive methods.
     *
     * Example usage:
     * <pre>
     * DefaultParser parser = Option.builder()
     *     .setAllowPartialMatching(false)
     *     .setStripLeadingAndTrailingQuotes(false)
     *     .build();
     * </pre>
     *
     * @since 1.5.0
     */
    public static final class Builder {
        /**
         * Contains a reference to the Builder Python class.
         * 
         */
        private static Value builderClz = ContextInitializer.getPythonClass("default_parser.py", "DefaultParser").getMember("Builder");;

        /**
         * Contains a reference to the embedded Builder Python object.
         */
        private Value builderObj;

        /**
         * Constructs a new {@code Builder} for a {@code DefaultParser} instance.
         *
         * Both allowPartialMatching and stripLeadingAndTrailingQuotes are true by default,
         * mimicking the argument-less constructor.
         */
        private Builder() {
            builderObj = builderClz.execute();
        }

        /**
         * Builds an DefaultParser with the values declared by this {@link Builder}.
         *
         * @return the new {@link DefaultParser}
         * @since 1.5.0
         */
        public DefaultParser build() {
            Value defaultParserObj = builderObj.invokeMember("build");
            return DefaultParser.create(defaultParserObj);
        }

        /**
         * Sets if partial matching of long options is supported.
         *
         * By "partial matching" we mean that given the following code:
         *
         * <pre>
         * {
         *     &#64;code
         *     final Options options = new Options();
         *     options.addOption(new Option("d", "debug", false, "Turn on debug."));
         *     options.addOption(new Option("e", "extract", false, "Turn on extract."));
         *     options.addOption(new Option("o", "option", true, "Turn on option with argument."));
         * }
         * </pre>
         *
         * If "partial matching" is turned on, {@code -de} only matches the {@code "debug"} option. However, with
         * "partial matching" disabled, {@code -de} would enable both {@code debug} as well as {@code extract}
         *
         * @param allowPartialMatching whether to allow partial matching of long options
         * @return this builder, to allow method chaining
         * @since 1.5.0
         */
        public Builder setAllowPartialMatching(final boolean allowPartialMatching) {
            builderObj.invokeMember("set_allow_partial_matching", allowPartialMatching);
            return this;
        }

        /**
         * Sets if balanced leading and trailing double quotes should be stripped from option arguments.
         *
         * If "stripping of balanced leading and trailing double quotes from option arguments" is true,
         * the outermost balanced double quotes of option arguments values will be removed.
         * For example, {@code -o '"x"'} getValue() will return {@code x}, instead of {@code "x"}
         *
         * If "stripping of balanced leading and trailing double quotes from option arguments" is null,
         * then quotes will be stripped from option values separated by space from the option, but
         * kept in other cases, which is the historic behaviour.
         *
         * @param stripLeadingAndTrailingQuotes whether balanced leading and trailing double quotes should be stripped from option arguments.
         * @return this builder, to allow method chaining
         * @since 1.5.0
         */
        public Builder setStripLeadingAndTrailingQuotes(final Boolean stripLeadingAndTrailingQuotes) {
            builderObj.invokeMember("set_strip_leading_and_trailing_quotes", stripLeadingAndTrailingQuotes);
            return this;
        }
    }

    /**
     * Creates a new {@link Builder} to create an {@link DefaultParser} using descriptive
     * methods.
     *
     * @return a new {@link Builder} instance
     * @since 1.5.0
     */
    public static Builder builder() {
        return new Builder();
    }

    /** The command-line instance. */
    protected CommandLine cmd;

    /** The current options. */
    protected Options options;

    /**
     * Flag indicating how unrecognized tokens are handled. {@code true} to stop the parsing and add the remaining
     * tokens to the args list. {@code false} to throw an exception.
     */
    protected boolean stopAtNonOption;

    /**
     * Creates a new DefaultParser instance with partial matching enabled.
     *
     * By "partial matching" we mean that given the following code:
     *
     * <pre>
     * {
     *     &#64;code
     *     final Options options = new Options();
     *     options.addOption(new Option("d", "debug", false, "Turn on debug."));
     *     options.addOption(new Option("e", "extract", false, "Turn on extract."));
     *     options.addOption(new Option("o", "option", true, "Turn on option with argument."));
     * }
     * </pre>
     *
     * with "partial matching" turned on, {@code -de} only matches the {@code "debug"} option. However, with
     * "partial matching" disabled, {@code -de} would enable both {@code debug} as well as {@code extract}
     * options.
     */
    public DefaultParser() {
        defaultParserObj = clz.newInstance();
    }

    public DefaultParser(Value v) {
        defaultParserObj = v;
    }

    /**
     * Create a new DefaultParser instance with the specified partial matching policy.
     *
     * By "partial matching" we mean that given the following code:
     *
     * <pre>
     * {
     *     &#64;code
     *     final Options options = new Options();
     *     options.addOption(new Option("d", "debug", false, "Turn on debug."));
     *     options.addOption(new Option("e", "extract", false, "Turn on extract."));
     *     options.addOption(new Option("o", "option", true, "Turn on option with argument."));
     * }
     * </pre>
     *
     * with "partial matching" turned on, {@code -de} only matches the {@code "debug"} option. However, with
     * "partial matching" disabled, {@code -de} would enable both {@code debug} as well as {@code extract}
     * options.
     *
     * @param allowPartialMatching if partial matching of long options shall be enabled
     */
    public DefaultParser(final boolean allowPartialMatching) {
        defaultParserObj = clz.newInstance(allowPartialMatching);
    }

    /**
     * Throws a {@link MissingOptionException} if all of the required options are not present.
     *
     * @throws MissingOptionException if any of the required Options are not present.
     */
    protected void checkRequiredOptions() throws MissingOptionException {
        // if there are required options that have not been processed
        try {
            defaultParserObj.invokeMember("check_required_options");
        } catch (PolyglotException e) {
            throw new MissingOptionException(e.getMessage());
        }
    }

    /**
     * Breaks {@code token} into its constituent parts using the following algorithm.
     *
     * <ul>
     * <li>ignore the first character ("<b>-</b>")</li>
     * <li>for each remaining character check if an {@link Option} exists with that id.</li>
     * <li>if an {@link Option} does exist then add that character prepended with "<b>-</b>" to the list of processed
     * tokens.</li>
     * <li>if the {@link Option} can have an argument value and there are remaining characters in the token then add the
     * remaining characters as a token to the list of processed tokens.</li>
     * <li>if an {@link Option} does <b>NOT</b> exist <b>AND</b> {@code stopAtNonOption} <b>IS</b> set then add the
     * special token "<b>--</b>" followed by the remaining characters and also the remaining tokens directly to the
     * processed tokens list.</li>
     * <li>if an {@link Option} does <b>NOT</b> exist <b>AND</b> {@code stopAtNonOption} <b>IS NOT</b> set then add
     * that character prepended with "<b>-</b>".</li>
     * </ul>
     *
     * @param token The current token to be <b>burst</b> at the first non-Option encountered.
     * @throws ParseException if there are any problems encountered while parsing the command line token.
     */
    protected void handleConcatenatedOptions(final String token) throws ParseException {
        try {
            defaultParserObj.invokeMember("handle_concatenated_options", token);
        } catch (PolyglotException e) {
            throw new ParseException(e.getMessage());
        }
    }

    @Override
    public CommandLine parse(final Options options, final String[] arguments) throws ParseException {
        return parse(options, arguments, null);
    }

    @Override
    public CommandLine parse(final Options options, final String[] arguments, final boolean stopAtNonOption) throws ParseException {
        return parse(options, arguments, null, stopAtNonOption);
    }

    /**
     * Parses the arguments according to the specified options and properties.
     *
     * @param options the specified Options
     * @param arguments the command line arguments
     * @param properties command line option name-value pairs
     * @return the list of atomic option and value tokens
     *
     * @throws ParseException if there are any problems encountered while parsing the command line tokens.
     */
    public CommandLine parse(final Options options, final String[] arguments, final Properties properties) throws ParseException {
        return parse(options, arguments, properties, false);
    }

    /**
     * Parses the arguments according to the specified options and properties.
     *
     * @param options the specified Options
     * @param arguments the command line arguments
     * @param properties command line option name-value pairs
     * @param stopAtNonOption if {@code true} an unrecognized argument stops the parsing and the remaining arguments
     *        are added to the {@link CommandLine}s args list. If {@code false} an unrecognized argument triggers a
     *        ParseException.
     *
     * @return the list of atomic option and value tokens
     * @throws ParseException if there are any problems encountered while parsing the command line tokens.
     */
    public CommandLine parse(final Options options, final String[] arguments, final Properties properties,
            final boolean stopAtNonOption)
            throws ParseException {
        try {
            return CommandLine
                    .create(defaultParserObj.invokeMember("parse", options, arguments, properties, stopAtNonOption));
        } catch (PolyglotException e) {
            String exceptionType = e.getGuestObject().getMember("__class__").getMember("__name__").asString();
            if (exceptionType.equals("MissingArgumentException")) {
                throw new MissingArgumentException(Option.create(e.getGuestObject().invokeMember("get_option")));
            } else if (exceptionType.equals("MissingOptionException")) {
                List missingOptionsList = IntegrationUtil.valueArrayToCollection(
                        e.getGuestObject().invokeMember("get_missing_options"), ArrayList.class, v -> {
                            if (v.isString()) {
                                return v.asString();
                            } else {
                                return OptionGroup.create(v);
                            }
                        });
                throw new MissingOptionException(missingOptionsList);
            } else if (exceptionType.equals("UnrecognizedOptionException")) {
                throw new UnrecognizedOptionException(e.getMessage(),
                        e.getGuestObject().invokeMember("get_option").asString());
            } else if (exceptionType.equals("AlreadySelectedException")) {
                throw new AlreadySelectedException(
                        OptionGroup.create(e.getGuestObject().invokeMember("get_option_group")),
                        Option.create(e.getGuestObject().invokeMember("get_option")));
            } else if (exceptionType.equals("AmbiguousOptionException")) {
                String opt = e.getGuestObject().getMember("option").asString();
                Collection<String> missingOptions = new ArrayList<>(
                        Arrays.asList(e.getGuestObject().invokeMember("get_matching_options").as(String[].class)));
                throw new AmbiguousOptionException(opt, missingOptions);
            }
            throw new ParseException(e.getMessage());
        }
    }
}
