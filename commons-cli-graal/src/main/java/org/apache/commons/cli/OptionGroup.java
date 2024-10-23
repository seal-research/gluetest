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
import java.util.List;
import java.util.Map;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * A group of mutually exclusive options.
 */
public class OptionGroup implements Serializable {
    /** The serial version UID. */
    private static final long serialVersionUID = 1L;

    /** handle to the Python class */
    private static Value clz = ContextInitializer.getPythonClass("option_group.py", "OptionGroup");

    /** handle to the Python object */
    private Value obj;

    /**
     * Create an option group.
     */
    public OptionGroup() {
        obj = clz.execute();
    }

    /**
     * (Re)create an option group with the python object.
     *
     * @param foreignOptionGroup the option to add to this group
     */
    public OptionGroup(final Value foreignOptionGroup) {
        obj = foreignOptionGroup;
    }

    /** Cache for wrappers to python objects  */
    private static Map<Value, OptionGroup> cache = new HashMap<>();

    public static OptionGroup create(final Value foreignOptionGroup) {
        if (foreignOptionGroup.isNull()) {
            return null;
        }
        return cache.computeIfAbsent(foreignOptionGroup, OptionGroup::new);
    }

    public Value getPythonObject() {
        return obj;
    }

    /**
     * Add the specified {@code Option} to this group.
     *
     * @param option the option to add to this group
     * @return this option group with the option added
     */
    public OptionGroup addOption(final Option option) {
        obj.invokeMember("add_option", option);
        return this;
    }

    /**
     * @return the names of the options in this group as a {@code Collection}
     */
    public Collection<String> getNames() {
        // the key set is the collection of names
        return obj.invokeMember("get_names").as(List.class);
    }

    /**
     * @return the options in this group as a {@code Collection}
     */
    public Collection<Option> getOptions() {
        // the values are the collection of python objects
        return IntegrationUtil.valueArrayToCollection(obj.invokeMember("get_options"), Option.class, ArrayList.class);
    }

    /**
     * @return the selected option name
     */
    public String getSelected() {
        return obj.getMember("selected").asString();
    }

    /**
     * Tests whether this option group is required.
     *
     * @return whether this option group is required
     */
    public boolean isRequired() {
        return obj.getMember("required").asBoolean();
    }

    /**
     * @param required specifies if this group is required
     */
    public void setRequired(final boolean required) {
        obj.invokeMember("set_required", required);
    }

    /**
     * Set the selected option of this group to {@code name}.
     *
     * @param option the option that is selected
     * @throws AlreadySelectedException if an option from this group has already been selected.
     */
    public void setSelected(final Option option) throws AlreadySelectedException {
        try {
            obj.invokeMember("set_selected", option);
        } catch (PolyglotException e) {
            throw new AlreadySelectedException(this, option);
        }
    }

    /**
     * Returns the stringified version of this OptionGroup.
     *
     * @return the stringified representation of this group
     */
    @Override
    public String toString() {
        return obj.invokeMember("to_string").asString();
    }
}
