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
import java.util.List;
import java.util.Properties;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * {@code Parser} creates {@link CommandLine}s.
 *
 * @deprecated since 1.3, the two-pass parsing with the flatten method is not enough flexible to handle complex cases
 */
@Deprecated
public abstract class Parser implements CommandLineParser {

    private static Value clz = ContextInitializer.getPythonClass("gnu_parser.py", "GnuParser");

    public static Value parserObj;

    public Parser() {
        parserObj = clz.execute();
    }

    public Parser(Value v) {
        parserObj = v;
    }

    public Value getPythonObject() {
        return parserObj;
    }

    /** CommandLine instance */
    protected CommandLine cmd;

    /**
     * Throws a {@link MissingOptionException} if all of the required options are not present.
     *
     * @throws MissingOptionException if any of the required Options are not present.
     */
    protected void checkRequiredOptions() throws MissingOptionException {
        // if there are required options that have not been processed
        try {
            parserObj.invokeMember("check_required_options");
        } catch (PolyglotException e) {
            throw new MissingOptionException(e.getMessage());
        }
    }

    /**
     * Subclasses must implement this method to reduce the {@code arguments} that have been passed to the parse method.
     *
     * @param opts The Options to parse the arguments by.
     * @param arguments The arguments that have to be flattened.
     * @param stopAtNonOption specifies whether to stop flattening when a non option has been encountered
     * @return a String array of the flattened arguments
     * @throws ParseException if there are any problems encountered while parsing the command line tokens.
     */
    protected abstract String[] flatten(Options opts, String[] arguments, boolean stopAtNonOption) throws ParseException;

    protected Options getOptions() {
        return Options.create(parserObj.invokeMember("getOptions"));
    }

    protected List getRequiredOptions() {
        return IntegrationUtil.valueArrayToCollection(parserObj.invokeMember("get_required_options"), String.class, List.class);
    }

    /**
     * Parses the specified {@code arguments} based on the specified {@link Options}.
     *
     * @param options the {@code Options}
     * @param arguments the {@code arguments}
     * @return the {@code CommandLine}
     * @throws ParseException if there are any problems encountered while parsing the command line tokens.
     */
    @Override
    public CommandLine parse(final Options options, final String[] arguments) throws ParseException {
        return parse(options, arguments, null, false);
    }

    /**
     * Parses the specified {@code arguments} based on the specified {@link Options}.
     *
     * @param options the {@code Options}
     * @param arguments the {@code arguments}
     * @param stopAtNonOption if {@code true} an unrecognized argument stops the parsing and the remaining arguments
     *        are added to the {@link CommandLine}s args list. If {@code false} an unrecognized argument triggers a
     *        ParseException.
     * @return the {@code CommandLine}
     * @throws ParseException if an error occurs when parsing the arguments.
     */
    @Override
    public CommandLine parse(final Options options, final String[] arguments, final boolean stopAtNonOption) throws ParseException {
        return parse(options, arguments, null, stopAtNonOption);
    }

    /**
     * Parse the arguments according to the specified options and properties.
     *
     * @param options the specified Options
     * @param arguments the command line arguments
     * @param properties command line option name-value pairs
     * @return the list of atomic option and value tokens
     * @throws ParseException if there are any problems encountered while parsing the command line tokens.
     *
     * @since 1.1
     */
    public CommandLine parse(final Options options, final String[] arguments, final Properties properties) throws ParseException {
        return parse(options, arguments, properties, false);
    }

    /**
     * Parse the arguments according to the specified options and properties.
     *
     * @param options the specified Options
     * @param arguments the command line arguments
     * @param properties command line option name-value pairs
     * @param stopAtNonOption if {@code true} an unrecognized argument stops the parsing and the remaining arguments
     *        are added to the {@link CommandLine}s args list. If {@code false} an unrecognized argument triggers a
     *        ParseException.
     *
     * @return the list of atomic option and value tokens
     *
     * @throws ParseException if there are any problems encountered while parsing the command line tokens.
     *
     * @since 1.1
     */
    public CommandLine parse(final Options options, String[] arguments, final Properties properties, final boolean stopAtNonOption) throws ParseException {
        try {
            return CommandLine.create(parserObj.invokeMember("parse", options, arguments, properties, stopAtNonOption));
        } catch (PolyglotException e) {
            String exceptionType = e.getGuestObject().getMember("__class__").getMember("__name__").asString();
            if (exceptionType.equals("MissingArgumentException")) {
                throw new MissingArgumentException(Option.create(e.getGuestObject().invokeMember("get_option")));
            } else if (exceptionType.equals("MissingOptionException")) {
                List missingOptionsList = IntegrationUtil.valueArrayToCollection(e.getGuestObject().invokeMember("get_missing_options"), ArrayList.class, v -> {
                    if (v.isString()) {
                        return v.asString();
                    } else {
                        return OptionGroup.create(v);
                    }
                });
                throw new MissingOptionException(missingOptionsList);
            } else if (exceptionType.equals("UnrecognizedOptionException")) {
                throw new UnrecognizedOptionException(e.getMessage(), e.getGuestObject().invokeMember("get_option").asString());
            } else if (exceptionType.equals("AlreadySelectedException")) {
                throw new AlreadySelectedException(OptionGroup.create(e.getGuestObject().invokeMember("get_option_group")), Option.create(e.getGuestObject().invokeMember("get_option")));
            } else if (exceptionType.equals("AmbiguousOptionException")) {
                String opt = e.getGuestObject().getMember("option").asString();
                Collection<String> missingOptions = new ArrayList<>(Arrays.asList(e.getGuestObject().invokeMember("get_matching_options").as(String[].class)));
                throw new AmbiguousOptionException(opt, missingOptions);
            }
            throw new ParseException(e.getMessage());
        }
    }

    protected void setOptions(final Options options) {
        parserObj.invokeMember("set_options", options);
    }
}
