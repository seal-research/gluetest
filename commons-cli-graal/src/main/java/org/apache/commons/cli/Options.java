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
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import org.graalvm.polyglot.Value;

/**
 * Main entry-point into the library.
 * <p>
 * Options represents a collection of {@link Option} objects, which describe the possible options for a command-line.
 * <p>
 * It may flexibly parse long and short options, with or without values. Additionally, it may parse only a portion of a
 * commandline, allowing for flexible multi-stage parsing.
 *
 * @see org.apache.commons.cli.CommandLine
 */
public class Options implements Serializable {

    /**
     * Contains a reference to the Python class.
     */
    private static Value clz = ContextInitializer.getPythonClass("options.py", "Options");

    /**
     * Contains a reference to the embedded Python object.
     */
    private Value optionsObj;

    /** The serial version UID. */
    private static final long serialVersionUID = 1L;

    /**
     * Special constructor for building {@link Options} instances with a python object.
     * 
     * @param v the python object
     */
    public Options(Value v) {
        optionsObj = v;
    }

    public Options() {
        optionsObj = clz.execute();
    }

    /** Cache for wrappers to python objects  */
    private static Map<Value, Options> cache = new HashMap<>();

    public static Options create(final Value foreignOptions) {
        if (foreignOptions.isNull()) {
            return null;
        }
        return cache.computeIfAbsent(foreignOptions, Options::new);
    }

    public Value getPythonObject() {
        return optionsObj;
    }

    /**
     * Adds an option instance
     *
     * @param opt the option that is to be added
     * @return the resulting Options instance
     */
    public Options addOption(final Option opt) {
        optionsObj.invokeMember("add_option", opt);
        return this;
    }

    /**
     * Add an option that only contains a short-name.
     *
     * <p>
     * It may be specified as requiring an argument.
     * </p>
     *
     * @param opt Short single-character name of the option.
     * @param hasArg flag signalling if an argument is required after this option
     * @param description Self-documenting description
     * @return the resulting Options instance
     */
    public Options addOption(final String opt, final boolean hasArg, final String description) {
        addOption(opt, null, hasArg, description);
        return this;
    }

    /**
     * Add an option that only contains a short name.
     *
     * <p>
     * The option does not take an argument.
     * </p>
     *
     * @param opt Short single-character name of the option.
     * @param description Self-documenting description
     * @return the resulting Options instance
     * @since 1.3
     */
    public Options addOption(final String opt, final String description) {
        addOption(opt, null, false, description);
        return this;
    }

    /**
     * Add an option that contains a short-name and a long-name.
     *
     * <p>
     * It may be specified as requiring an argument.
     * </p>
     *
     * @param opt Short single-character name of the option.
     * @param longOpt Long multi-character name of the option.
     * @param hasArg flag signalling if an argument is required after this option
     * @param description Self-documenting description
     * @return the resulting Options instance
     */
    public Options addOption(final String opt, final String longOpt, final boolean hasArg, final String description) {
        addOption(new Option(opt, longOpt, hasArg, description));
        return this;
    }

    /**
     * Add the specified option group.
     *
     * @param group the OptionGroup that is to be added
     * @return the resulting Options instance
     */
    public Options addOptionGroup(final OptionGroup group) {
        optionsObj.invokeMember("add_option_group", group);
        return this;
    }

    /**
     * Add an option that contains a short-name and a long-name.
     *
     * <p>
     * The added option is set as required. It may be specified as requiring an argument. This method is a shortcut for:
     * </p>
     *
     * <pre>
     * <code>
     * Options option = new Option(opt, longOpt, hasArg, description);
     * option.setRequired(true);
     * options.add(option);
     * </code>
     * </pre>
     *
     * @param opt Short single-character name of the option.
     * @param longOpt Long multi-character name of the option.
     * @param hasArg flag signalling if an argument is required after this option
     * @param description Self-documenting description
     * @return the resulting Options instance
     * @since 1.4
     */
    public Options addRequiredOption(final String opt, final String longOpt, final boolean hasArg, final String description) {
        optionsObj.invokeMember("add_required_option", opt, longOpt, hasArg, description);
        return this;
    }

    /**
     * Gets the options with a long name starting with the name specified.
     *
     * @param opt the partial name of the option
     * @return the options matching the partial name specified, or an empty list if none matches
     * @since 1.3
     */
    public List<String> getMatchingOptions(String opt) {
        return optionsObj.invokeMember("get_matching_options", opt).as(List.class);
    }

    /**
     * Gets the {@link Option} matching the long or short name specified.
     *
     * <p>
     * The leading hyphens in the name are ignored (up to 2).
     * </p>
     *
     * @param opt short or long name of the {@link Option}
     * @return the option represented by opt
     */
    public Option getOption(String opt) {
        Value optionObj = optionsObj.invokeMember("get_option", opt);
        if (optionObj.isNull()) {
            return null;
        }
        return Option.create(optionObj);
    }

    /**
     * Gets the OptionGroup the {@code opt} belongs to.
     *
     * @param opt the option whose OptionGroup is being queried.
     * @return the OptionGroup if {@code opt} is part of an OptionGroup, otherwise return null
     */
    public OptionGroup getOptionGroup(final Option opt) {
        return OptionGroup.create(optionsObj.invokeMember("get_option_group", opt));
    }

    /**
     * Gets the OptionGroups that are members of this Options instance.
     *
     * @return a Collection of OptionGroup instances.
     */
    Collection<OptionGroup> getOptionGroups() {
        return IntegrationUtil.valueArrayToCollection(optionsObj.invokeMember("get_option_groups"), OptionGroup.class, HashSet.class);
    }

    /**
     * Gets a read-only list of options in this set
     *
     * @return read-only Collection of {@link Option} objects in this descriptor
     */
    public Collection<Option> getOptions() {
        return IntegrationUtil.valueArrayToCollection(optionsObj.invokeMember("get_options"), Option.class, ArrayList.class);
    }

    /**
     * Gets the required options.
     *
     * @return read-only List of required options
     */
    public List getRequiredOptions() {
        return IntegrationUtil.valueArrayToCollection(optionsObj.invokeMember("get_required_options"), ArrayList.class, v -> {
            if (v.isString()) {
                return v.asString();
            } else {
                return OptionGroup.create(v);
            }
        });
    }

    /**
     * Returns whether the named {@link Option} is a member of this {@link Options}.
     *
     * @param opt long name of the {@link Option}
     * @return true if the named {@link Option} is a member of this {@link Options}
     * @since 1.3
     */
    public boolean hasLongOption(String opt) {
        return optionsObj.invokeMember("has_long_option", opt).asBoolean();
    }

    /**
     * Returns whether the named {@link Option} is a member of this {@link Options}.
     *
     * @param opt short or long name of the {@link Option}
     * @return true if the named {@link Option} is a member of this {@link Options}
     */
    public boolean hasOption(String opt) {
        return optionsObj.invokeMember("has_option", opt).asBoolean();
    }

    /**
     * Returns whether the named {@link Option} is a member of this {@link Options}.
     *
     * @param opt short name of the {@link Option}
     * @return true if the named {@link Option} is a member of this {@link Options}
     * @since 1.3
     */
    public boolean hasShortOption(String opt) {
        return optionsObj.invokeMember("has_short_option", opt).asBoolean();
    }

    /**
     * Returns the Options for use by the HelpFormatter.
     *
     * @return the List of Options
     */
    List<Option> helpOptions() {
        return IntegrationUtil.valueArrayToCollection(optionsObj.invokeMember("help_options"), Option.class, ArrayList.class);
    }

    /**
     * Dump state, suitable for debugging.
     *
     * @return Stringified form of this object
     */
    @Override
    public String toString() {
        return optionsObj.invokeMember("to_string").asString();
    }
}
