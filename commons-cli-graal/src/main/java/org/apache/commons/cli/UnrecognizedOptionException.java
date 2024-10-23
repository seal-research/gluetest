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

import org.graalvm.polyglot.Value;

/**
 * Thrown during parsing signaling an unrecognized option.
 */
public class UnrecognizedOptionException extends ParseException {

    /**
     * This exception {@code serialVersionUID}.
     */
    private static final long serialVersionUID = -252504690284625623L;

    /**
     * Contains a reference to the Python class.
     */
    private static Value clz;


    /**
     * Contains a reference to the Python exception.
     */
    private final Value obj;


    static {
        clz = ContextInitializer.getPythonClass("unrecognized_option_exception.py", "UnrecognizedOptionException");
    }

    /**
     * Constructs a new {@code UnrecognizedArgumentException} with the specified detail message.
     *
     * @param message the detail message
     */
    public UnrecognizedOptionException(final String message) {
        this(message, null);
    }

    /**
     * Constructs a new {@code UnrecognizedArgumentException} with the specified option and detail message.
     *
     * @param message the detail message
     * @param option the unrecognized option
     * @since 1.2
     */
    public UnrecognizedOptionException(final String message, final String option) {
        super(message);
        obj = clz.execute(message, option);
    }

    /**
     * Gets the unrecognized option.
     *
     * @return the related option
     * @since 1.2
     */
    public String getOption() {
        return obj.invokeMember("get_option").asString();
    }
}
