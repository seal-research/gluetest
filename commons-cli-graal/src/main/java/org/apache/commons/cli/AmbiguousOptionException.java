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

import org.graalvm.polyglot.Value;

/**
 * Exception thrown when an option can't be identified from a partial name.
 *
 * @since 1.3
 */
public class AmbiguousOptionException extends UnrecognizedOptionException {
    /**
     * This exception {@code serialVersionUID}.
     */
    private static final long serialVersionUID = 5829816121277947229L;

    /**
     * Contains a reference to the Python class.
     */
    private static Value clz;

    /**
     * Contains a reference to the Python exception.
     */
    private final Value obj;

    static {
        clz = ContextInitializer.getPythonClass("ambiguous_option_exception.py", "AmbiguousOptionException");
    }

    /**
     * Build the exception message from the specified list of options.
     *
     * @param option
     * @param matchingOptions
     * @return
     */
    private static String createMessage(final String option, final Collection<String> matchingOptions) {
        return clz.getMember("_create_message").execute(option, matchingOptions).asString();
    }

    /**
     * Constructs a new AmbiguousOptionException.
     *
     * @param option the partial option name
     * @param matchingOptions the options matching the name
     */
    public AmbiguousOptionException(final String option, final Collection<String> matchingOptions) {
        super(createMessage(option, matchingOptions), option);
        obj = clz.execute(option, matchingOptions);
    }

    /**
     * Gets the options matching the partial name.
     *
     * @return a collection of options matching the name
     */
    public Collection<String> getMatchingOptions() {
        return new ArrayList<>(Arrays.asList(obj.invokeMember("get_matching_options").as(String[].class)));
    }
}
