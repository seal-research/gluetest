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
 * This is a temporary implementation. TypeHandler will handle the pluggableness of OptionTypes and it will direct all
 * of these types of conversion functionalities to ConvertUtils component in Commons already. BeanUtils I think.
 */
public class TypeHandler {

    private static Value clz = ContextInitializer.getPythonClass("type_handler.py", "TypeHandler");

    /**
     * Returns the {@code Object} of type {@code clazz} with the value of {@code str}.
     *
     * @param str the command line value
     * @param clazz the class representing the type of argument
     * @param <T> type of argument
     * @return The instance of {@code clazz} initialized with the value of {@code str}.
     * @throws ParseException if the value creation for the given class failed
     */
    @SuppressWarnings("unchecked") // returned value will have type T because it is fixed by clazz
    public static <T> T createValue(final String str, final Class<T> clazz) throws ParseException {
        try {
            Value value = clz.invokeMember("create_value", str, clazz);
            if (clazz == Number.class && !(value.as(Number.class) instanceof Double)) {
                return (T) value.as(Long.class);
            }
            return value.as(clazz);
        } catch (PolyglotException e) {
            String exceptionType = e.getMessage().split(":")[0];
            if (exceptionType.equals("ValueError")) {
                throw new UnsupportedOperationException("Not yet implemented");
            }
            throw new ParseException("Unable to handle the class: " + clazz);
        }
    }

    /**
     * Returns the {@code Object} of type {@code obj} with the value of {@code str}.
     *
     * @param str the command line value
     * @param obj the type of argument
     * @return The instance of {@code obj} initialized with the value of {@code str}.
     * @throws ParseException if the value creation for the given object type failed
     */
    public static Object createValue(final String str, final Object obj) throws ParseException {
        try {
            Object value = clz.invokeMember("create_value", str, obj).as(Object.class);
            if (value instanceof Number && !(value instanceof Double)) {
                return ((Number) value).longValue();
            }
            return value;
        } catch (PolyglotException e) {
            String exceptionType = e.getMessage().split(":")[0];
            if (exceptionType.equals("ValueError")) {
                throw new UnsupportedOperationException("Not yet implemented");
            }
            throw new ParseException(e.getMessage());
        }
    }
}
