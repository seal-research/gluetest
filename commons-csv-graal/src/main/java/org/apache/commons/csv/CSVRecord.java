/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.apache.commons.csv;

import java.io.Serializable;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.TypeLiteral;
import org.graalvm.polyglot.Value;

/**
 * A CSV record parsed from a CSV file.
 */
public final class CSVRecord implements Serializable, Iterable<String> {

    /** glue code attributes */
    private static Value clz = ContextInitializer.getPythonClass("csv_record.py", "CSVRecord"); 
    private Value obj;

    private static final long serialVersionUID = 1L;

    CSVRecord(final String[] values, final Map<String, Integer> mapping, final String comment, final long recordNumber,
            final long characterPosition) {
        obj = clz.newInstance(
            values,
            mapping,
            comment,
            recordNumber,
            characterPosition
        );
    }

    /**
     * Construct a CSVRecord using a Python object.
     * @param v a Python Value object
     */
    CSVRecord(Value v) { obj = v; }

    public Value getPythonObject() {
        return obj;
    }

    /**
     * Returns a value by {@link Enum}.
     *
     * @param e
     *            an enum
     * @return the String at the given enum String
     */
    public String get(final Enum<?> e) {
        return get(e.toString());
    }

    /**
     * Returns a value by index.
     *
     * @param i
     *            a column index (0-based)
     * @return the String at the given index
     */
    public String get(final int i) {
        try {
            return obj.invokeMember("get", i).asString();
        } catch (final PolyglotException e) {
            String msg = e.getMessage();
            if (msg.contains("IndexError")) {
                throw new ArrayIndexOutOfBoundsException(msg);
            }
            throw new IllegalArgumentException();
        }
    }

    /**
     * Returns a value by name.
     *
     * @param name
     *            the name of the column to be retrieved.
     * @return the column value, maybe null depending on {@link CSVFormat#getNullString()}.
     * @throws IllegalStateException
     *             if no header mapping was provided
     * @throws IllegalArgumentException
     *             if {@code name} is not mapped or if the record is inconsistent
     * @see #isConsistent()
     * @see CSVFormat#withNullString(String)
     */
    public String get(final String name) {
        try {
            return obj.invokeMember("get", name).asString();
        } catch (final PolyglotException e) {
            String msg = e.getMessage();
            if (msg.contains("Mapping for")) {
                throw new IllegalArgumentException(msg);
            }
            if (msg.contains("Index for header")) {
                throw new IllegalArgumentException(msg);
            }

            if (msg.contains("CSVRecord only has")) {
                throw new IllegalArgumentException(msg);
            }

            if (msg.contains("No header mapping was specified")) {
                throw new IllegalStateException(msg);
            }
            throw new IllegalArgumentException();
        }
    }

    /**
     * Returns the start position of this record as a character position in the source stream. This may or may not
     * correspond to the byte position depending on the character set.
     *
     * @return the position of this record in the source stream.
     */
    public long getCharacterPosition() {
        return obj.invokeMember("get_character_position").asLong();
    }

    /**
     * Returns the comment for this record, if any.
     * Note that comments are attached to the following record.
     * If there is no following record (i.e. the comment is at EOF)
     * the comment will be ignored.
     *
     * @return the comment for this record, or null if no comment for this record is available.
     */
    public String getComment() {
        return obj.invokeMember("get_comment").asString();
    }

    /**
     * Returns the number of this record in the parsed CSV file.
     *
     * <p>
     * <strong>ATTENTION:</strong> If your CSV input has multi-line values, the returned number does not correspond to
     * the current line number of the parser that created this record.
     * </p>
     *
     * @return the number of this record.
     * @see CSVParser#getCurrentLineNumber()
     */
    public long getRecordNumber() {
        return obj.invokeMember("get_record_number").asLong();
    }

    /**
     * Tells whether the record size matches the header size.
     *
     * <p>
     * Returns true if the sizes for this record match and false if not. Some programs can export files that fail this
     * test but still produce parsable files.
     * </p>
     *
     * @return true of this record is valid, false if not
     */
    public boolean isConsistent() {
        return obj.invokeMember("is_consistent").asBoolean();
    }

    /**
     * Checks whether this record has a comment, false otherwise.
     * Note that comments are attached to the following record.
     * If there is no following record (i.e. the comment is at EOF)
     * the comment will be ignored.
     *
     * @return true if this record has a comment, false otherwise
     * @since 1.3
     */
    public boolean hasComment() {
        return obj.invokeMember("has_comment").asBoolean();
    }

    /**
     * Checks whether a given column is mapped, i.e. its name has been defined to the parser.
     *
     * @param name
     *            the name of the column to be retrieved.
     * @return whether a given column is mapped.
     */
    public boolean isMapped(final String name) {
        return obj.invokeMember("is_mapped", name).asBoolean();
    }

    /**
     * Checks whether a given columns is mapped and has a value.
     *
     * @param name
     *            the name of the column to be retrieved.
     * @return whether a given columns is mapped and has a value
     */
    public boolean isSet(final String name) {
        return obj.invokeMember("is_set", name).asBoolean();
    }

    /**
     * Returns an iterator over the values of this record.
     *
     * @return an iterator over the values of this record.
     */
    @Override
    public Iterator<String> iterator() {
        return toList().iterator();
    }

    /**
     * Puts all values of this record into the given Map.
     *
     * @param map
     *            The Map to populate.
     * @return the given map.
     */
    public <M extends Map<String, String>> M putIn(final M map) {
        Value map2 = obj.invokeMember("put_in", map);
        // cast to M considering class erasure
        return (M) map2.as(Map.class);
    }

    /**
     * Returns the number of values in this record.
     *
     * @return the number of values.
     */
    public int size() {
        return obj.invokeMember("size").asInt();
    }

    /**
     * Converts the values to a List.
     *
     * TODO: Maybe make this public?
     *
     * @return a new List
     */
    private List<String> toList() {
        return Arrays.asList(obj.getMember("_values").as(String[].class));
    }

    /**
     * Copies this record into a new Map. The new map is not connect
     *
     * @return A new Map. The map is empty if the record has no headers.
     */
    public Map<String, String> toMap() {
        return putIn(new HashMap<String, String>(size()));
    }

    /**
     * Returns a string representation of the contents of this record. The result is constructed by comment, mapping,
     * recordNumber and by passing the internal values array to {@link Arrays#toString(Object[])}.
     *
     * @return a String representation of this record.
     */
    @Override
    public String toString() {
        return obj.invokeMember("__str__").asString();
    }

    String[] values() {
        return obj.getMember("_values").as(String[].class);
    }

}
