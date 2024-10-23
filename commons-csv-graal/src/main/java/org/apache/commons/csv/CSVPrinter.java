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

import static org.apache.commons.csv.Constants.CR;
import static org.apache.commons.csv.Constants.LF;
import static org.apache.commons.csv.Constants.SP;

import java.io.Closeable;
import java.io.Flushable;
import java.io.IOException;
import java.sql.ResultSet;
import java.sql.SQLException;

import org.graalvm.polyglot.Value;

/**
 * Prints values in a CSV format.
 */
public final class CSVPrinter implements Flushable, Closeable {

    /** glue code attributes */
    private static Value clz = ContextInitializer.getPythonClass("csv_printer.py", "CSVPrinter"); 
    private Value obj;

    /**
     * Creates a printer that will print values to the given stream following the CSVFormat.
     * <p>
     * Currently, only a pure encapsulation format or a pure escaping format is supported. Hybrid formats (encapsulation
     * and escaping with a different character) are not supported.
     * </p>
     *
     * @param out
     *            stream to which to print. Must not be null.
     * @param format
     *            the CSV format. Must not be null.
     * @throws IOException
     *             thrown if the optional header cannot be printed.
     * @throws IllegalArgumentException
     *             thrown if the parameters of the format are inconsistent or if either out or format are null.
     */
    public CSVPrinter(final Appendable out, final CSVFormat format) throws IOException {
        Assertions.notNull(out, "out");
        Assertions.notNull(format, "format");

        obj = clz.newInstance(out, format);
    }

    /**
     * @return the Python guest CSVPrinter associated with this printer.
     */
    public Value getPythonObject() {
        return obj;
    }

    // ======================================================
    // printing implementation
    // ======================================================

    @Override
    public void close() throws IOException {
        close(false);
    }

    /**
     * Closes the underlying stream with an optional flush first.
     * @param flush whether to flush before the actual close.
     *
     * @throws IOException
     *             If an I/O error occurs
     * @since 1.6
     */
    public void close(final boolean flush) throws IOException {
        obj.invokeMember("close", flush);
    }

    /**
     * Flushes the underlying stream.
     *
     * @throws IOException
     *             If an I/O error occurs
     */
    @Override
    public void flush() throws IOException {
        obj.invokeMember("flush");
    }

    /**
     * Gets the target Appendable.
     *
     * @return the target Appendable.
     */
    public Appendable getOut() {
        return obj.invokeMember("get_out").as(Appendable.class);
    }

    /**
     * Prints the string as the next value on the line. The value will be escaped or encapsulated as needed.
     *
     * @param value
     *            value to be output.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void print(final Object value) throws IOException {
        obj.invokeMember("print", value);
    }

    /**
     * Prints a comment on a new line among the delimiter separated values.
     *
     * <p>
     * Comments will always begin on a new line and occupy a least one full line. The character specified to start
     * comments and a space will be inserted at the beginning of each new line in the comment.
     * </p>
     *
     * If comments are disabled in the current CSV format this method does nothing.
     *
     * @param comment
     *            the comment to output
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printComment(final String comment) throws IOException {
        obj.invokeMember("print_comment", comment);
    }

    /**
     * Outputs the record separator.
     *
     * @throws IOException
     *             If an I/O error occurs
     */
    public void println() throws IOException {
        obj.invokeMember("println");
    }

    /**
     * Prints the given values a single record of delimiter separated values followed by the record separator.
     *
     * <p>
     * The values will be quoted if needed. Quotes and newLine characters will be escaped. This method adds the record
     * separator to the output after printing the record, so there is no need to call {@link #println()}.
     * </p>
     *
     * @param values
     *            values to output.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printRecord(final Iterable<?> values) throws IOException {
        obj.invokeMember("print_record", values);
    }

    /**
     * Prints the given values a single record of delimiter separated values followed by the record separator.
     *
     * <p>
     * The values will be quoted if needed. Quotes and newLine characters will be escaped. This method adds the record
     * separator to the output after printing the record, so there is no need to call {@link #println()}.
     * </p>
     *
     * @param values
     *            values to output.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printRecord(final Object... values) throws IOException {
        obj.invokeMember("print_record", values);
    }

    /**
     * Prints all the objects in the given collection handling nested collections/arrays as records.
     *
     * <p>
     * If the given collection only contains simple objects, this method will print a single record like
     * {@link #printRecord(Iterable)}. If the given collections contains nested collections/arrays those nested elements
     * will each be printed as records using {@link #printRecord(Object...)}.
     * </p>
     *
     * <p>
     * Given the following data structure:
     * </p>
     *
     * <pre>
     * <code>
     * List&lt;String[]&gt; data = ...
     * data.add(new String[]{ "A", "B", "C" });
     * data.add(new String[]{ "1", "2", "3" });
     * data.add(new String[]{ "A1", "B2", "C3" });
     * </code>
     * </pre>
     *
     * <p>
     * Calling this method will print:
     * </p>
     *
     * <pre>
     * <code>
     * A, B, C
     * 1, 2, 3
     * A1, B2, C3
     * </code>
     * </pre>
     *
     * @param values
     *            the values to print.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printRecords(final Iterable<?> values) throws IOException {
        obj.invokeMember("print_records", values);
    }

    /**
     * Prints all the objects in the given array handling nested collections/arrays as records.
     *
     * <p>
     * If the given array only contains simple objects, this method will print a single record like
     * {@link #printRecord(Object...)}. If the given collections contains nested collections/arrays those nested
     * elements will each be printed as records using {@link #printRecord(Object...)}.
     * </p>
     *
     * <p>
     * Given the following data structure:
     * </p>
     *
     * <pre>
     * <code>
     * String[][] data = new String[3][]
     * data[0] = String[]{ "A", "B", "C" };
     * data[1] = new String[]{ "1", "2", "3" };
     * data[2] = new String[]{ "A1", "B2", "C3" };
     * </code>
     * </pre>
     *
     * <p>
     * Calling this method will print:
     * </p>
     *
     * <pre>
     * <code>
     * A, B, C
     * 1, 2, 3
     * A1, B2, C3
     * </code>
     * </pre>
     *
     * @param values
     *            the values to print.
     * @throws IOException
     *             If an I/O error occurs
     */
    public void printRecords(final Object... values) throws IOException {
        obj.invokeMember("print_records", values);
    }

    /**
     * Prints all the objects in the given JDBC result set.
     *
     * @param resultSet
     *            result set the values to print.
     * @throws IOException
     *             If an I/O error occurs
     * @throws SQLException
     *             if a database access error occurs
     */
    public void printRecords(final ResultSet resultSet) throws SQLException, IOException {
        obj.invokeMember("print_records", resultSet);
    }
}
