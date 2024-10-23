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

import static org.apache.commons.csv.Constants.BACKSLASH;
import static org.apache.commons.csv.Constants.COMMA;
import static org.apache.commons.csv.Constants.COMMENT;
import static org.apache.commons.csv.Constants.EMPTY;
import static org.apache.commons.csv.Constants.CR;
import static org.apache.commons.csv.Constants.CRLF;
import static org.apache.commons.csv.Constants.DOUBLE_QUOTE_CHAR;
import static org.apache.commons.csv.Constants.LF;
import static org.apache.commons.csv.Constants.PIPE;
import static org.apache.commons.csv.Constants.SP;
import static org.apache.commons.csv.Constants.TAB;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.io.Serializable;
import java.io.StringWriter;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * Specifies the format of a CSV file and parses input.
 *
 * <h2>Using predefined formats</h2>
 *
 * <p>
 * You can use one of the predefined formats:
 * </p>
 *
 * <ul>
 * <li>{@link #DEFAULT}</li>
 * <li>{@link #EXCEL}</li>
 * <li>{@link #MYSQL}</li>
 * <li>{@link #RFC4180}</li>
 * <li>{@link #TDF}</li>
 * </ul>
 *
 * <p>
 * For example:
 * </p>
 *
 * <pre>
 * CSVParser parser = CSVFormat.EXCEL.parse(reader);
 * </pre>
 *
 * <p>
 * The {@link CSVParser} provides static methods to parse other input types, for example:
 * </p>
 *
 * <pre>
 * CSVParser parser = CSVParser.parse(file, StandardCharsets.US_ASCII, CSVFormat.EXCEL);
 * </pre>
 *
 * <h2>Defining formats</h2>
 *
 * <p>
 * You can extend a format by calling the {@code with} methods. For example:
 * </p>
 *
 * <pre>
 * CSVFormat.EXCEL.withNullString(&quot;N/A&quot;).withIgnoreSurroundingSpaces(true);
 * </pre>
 *
 * <h2>Defining column names</h2>
 *
 * <p>
 * To define the column names you want to use to access records, write:
 * </p>
 *
 * <pre>
 * CSVFormat.EXCEL.withHeader(&quot;Col1&quot;, &quot;Col2&quot;, &quot;Col3&quot;);
 * </pre>
 *
 * <p>
 * Calling {@link #withHeader(String...)} let's you use the given names to address values in a {@link CSVRecord}, and
 * assumes that your CSV source does not contain a first record that also defines column names.
 *
 * If it does, then you are overriding this metadata with your names and you should skip the first record by calling
 * {@link #withSkipHeaderRecord(boolean)} with {@code true}.
 * </p>
 *
 * <h2>Parsing</h2>
 *
 * <p>
 * You can use a format directly to parse a reader. For example, to parse an Excel file with columns header, write:
 * </p>
 *
 * <pre>
 * Reader in = ...;
 * CSVFormat.EXCEL.withHeader(&quot;Col1&quot;, &quot;Col2&quot;, &quot;Col3&quot;).parse(in);
 * </pre>
 *
 * <p>
 * For other input types, like resources, files, and URLs, use the static methods on {@link CSVParser}.
 * </p>
 *
 * <h2>Referencing columns safely</h2>
 *
 * <p>
 * If your source contains a header record, you can simplify your code and safely reference columns, by using
 * {@link #withHeader(String...)} with no arguments:
 * </p>
 *
 * <pre>
 * CSVFormat.EXCEL.withHeader();
 * </pre>
 *
 * <p>
 * This causes the parser to read the first record and use its values as column names.
 *
 * Then, call one of the {@link CSVRecord} get method that takes a String column name argument:
 * </p>
 *
 * <pre>
 * String value = record.get(&quot;Col1&quot;);
 * </pre>
 *
 * <p>
 * This makes your code impervious to changes in column order in the CSV file.
 * </p>
 *
 * <h2>Notes</h2>
 *
 * <p>
 * This class is immutable.
 * </p>
 */
public final class CSVFormat implements Serializable {

    private static Value clz = ContextInitializer.getPythonClass("csv_format.py", "CSVFormat");
    private transient Value obj;
 

    /**
     * Predefines formats.
     *
     * @since 1.2
     */
    public enum Predefined {

        /**
         * @see CSVFormat#DEFAULT
         */
        Default(CSVFormat.DEFAULT),

        /**
         * @see CSVFormat#EXCEL
         */
        Excel(CSVFormat.EXCEL),

        /**
         * @see CSVFormat#INFORMIX_UNLOAD
         * @since 1.3
         */
        InformixUnload(CSVFormat.INFORMIX_UNLOAD),

        /**
         * @see CSVFormat#INFORMIX_UNLOAD_CSV
         * @since 1.3
         */
        InformixUnloadCsv(CSVFormat.INFORMIX_UNLOAD_CSV),

        /**
         * @see CSVFormat#MYSQL
         */
        MySQL(CSVFormat.MYSQL),

        /**
         * @see CSVFormat#ORACLE
         */
        Oracle(CSVFormat.ORACLE),

        /**
         * @see CSVFormat#POSTGRESQL_CSV
         * @since 1.5
         */
        PostgreSQLCsv(CSVFormat.POSTGRESQL_CSV),

        /**
         * @see CSVFormat#POSTGRESQL_CSV
         */
        PostgreSQLText(CSVFormat.POSTGRESQL_TEXT),

        /**
         * @see CSVFormat#RFC4180
         */
        RFC4180(CSVFormat.RFC4180),

        /**
         * @see CSVFormat#TDF
         */
        TDF(CSVFormat.TDF);

        private final CSVFormat format;

        Predefined(final CSVFormat format) {
            this.format = format;
        }

        /**
         * Gets the format.
         *
         * @return the format.
         */
        public CSVFormat getFormat() {
            return format;
        }
    }

    /**
     * Standard Comma Separated Value format, as for {@link #RFC4180} but allowing empty lines.
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter(',')</li>
     * <li>withQuote('"')</li>
     * <li>withRecordSeparator("\r\n")</li>
     * <li>withIgnoreEmptyLines(true)</li>
     * </ul>
     *
     * @see Predefined#Default
     */
    public static final CSVFormat DEFAULT = new CSVFormat(COMMA, DOUBLE_QUOTE_CHAR, null, null, null, false, true, CRLF,
            null, null, null, false, false, false, false, false, false);

    /**
     * Excel file format (using a comma as the value delimiter). Note that the actual value delimiter used by Excel is
     * locale dependent, it might be necessary to customize this format to accommodate to your regional settings.
     *
     * <p>
     * For example for parsing or generating a CSV file on a French system the following format will be used:
     * </p>
     *
     * <pre>
     * CSVFormat fmt = CSVFormat.EXCEL.withDelimiter(';');
     * </pre>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>{@link #withDelimiter(char) withDelimiter(',')}</li>
     * <li>{@link #withQuote(char) withQuote('"')}</li>
     * <li>{@link #withRecordSeparator(String) withRecordSeparator("\r\n")}</li>
     * <li>{@link #withIgnoreEmptyLines(boolean) withIgnoreEmptyLines(false)}</li>
     * <li>{@link #withAllowMissingColumnNames(boolean) withAllowMissingColumnNames(true)}</li>
     * </ul>
     * <p>
     * Note: This is currently like {@link #RFC4180} plus {@link #withAllowMissingColumnNames(boolean)
     * withAllowMissingColumnNames(true)} and {@link #withIgnoreEmptyLines(boolean) withIgnoreEmptyLines(false)}.
     * </p>
     *
     * @see Predefined#Excel
     */
    // @formatter:off
    public static final CSVFormat EXCEL = DEFAULT
            .withIgnoreEmptyLines(false)
            .withAllowMissingColumnNames();
    // @formatter:on

    /**
     * Default Informix CSV UNLOAD format used by the {@code UNLOAD TO file_name} operation.
     *
     * <p>
     * This is a comma-delimited format with a LF character as the line separator. Values are not quoted and special
     * characters are escaped with {@code '\'}. The default NULL string is {@code "\\N"}.
     * </p>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter(',')</li>
     * <li>withQuote("\"")</li>
     * <li>withRecordSeparator('\n')</li>
     * <li>withEscape('\\')</li>
     * </ul>
     *
     * @see Predefined#MySQL
     * @see <a href=
     *      "http://www.ibm.com/support/knowledgecenter/SSBJG3_2.5.0/com.ibm.gen_busug.doc/c_fgl_InOutSql_UNLOAD.htm">
     *      http://www.ibm.com/support/knowledgecenter/SSBJG3_2.5.0/com.ibm.gen_busug.doc/c_fgl_InOutSql_UNLOAD.htm</a>
     * @since 1.3
     */
    // @formatter:off
    public static final CSVFormat INFORMIX_UNLOAD = DEFAULT
            .withDelimiter(PIPE)
            .withEscape(BACKSLASH)
            .withQuote(DOUBLE_QUOTE_CHAR)
            .withRecordSeparator(LF);
    // @formatter:on

    /**
     * Default Informix CSV UNLOAD format used by the {@code UNLOAD TO file_name} operation (escaping is disabled.)
     *
     * <p>
     * This is a comma-delimited format with a LF character as the line separator. Values are not quoted and special
     * characters are escaped with {@code '\'}. The default NULL string is {@code "\\N"}.
     * </p>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter(',')</li>
     * <li>withQuote("\"")</li>
     * <li>withRecordSeparator('\n')</li>
     * </ul>
     *
     * @see Predefined#MySQL
     * @see <a href=
     *      "http://www.ibm.com/support/knowledgecenter/SSBJG3_2.5.0/com.ibm.gen_busug.doc/c_fgl_InOutSql_UNLOAD.htm">
     *      http://www.ibm.com/support/knowledgecenter/SSBJG3_2.5.0/com.ibm.gen_busug.doc/c_fgl_InOutSql_UNLOAD.htm</a>
     * @since 1.3
     */
    // @formatter:off
    public static final CSVFormat INFORMIX_UNLOAD_CSV = DEFAULT
            .withDelimiter(COMMA)
            .withQuote(DOUBLE_QUOTE_CHAR)
            .withRecordSeparator(LF);
    // @formatter:on

    /**
     * Default MySQL format used by the {@code SELECT INTO OUTFILE} and {@code LOAD DATA INFILE} operations.
     *
     * <p>
     * This is a tab-delimited format with a LF character as the line separator. Values are not quoted and special
     * characters are escaped with {@code '\'}. The default NULL string is {@code "\\N"}.
     * </p>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter('\t')</li>
     * <li>withQuote(null)</li>
     * <li>withRecordSeparator('\n')</li>
     * <li>withIgnoreEmptyLines(false)</li>
     * <li>withEscape('\\')</li>
     * <li>withNullString("\\N")</li>
     * <li>withQuoteMode(QuoteMode.ALL_NON_NULL)</li>
     * </ul>
     *
     * @see Predefined#MySQL
     * @see <a href="http://dev.mysql.com/doc/refman/5.1/en/load-data.html"> http://dev.mysql.com/doc/refman/5.1/en/load
     *      -data.html</a>
     */
    // @formatter:off
    public static final CSVFormat MYSQL = DEFAULT
            .withDelimiter(TAB)
            .withEscape(BACKSLASH)
            .withIgnoreEmptyLines(false)
            .withQuote(null)
            .withRecordSeparator(LF)
            .withNullString("\\N")
            .withQuoteMode(QuoteMode.ALL_NON_NULL);
    // @formatter:off

    /**
     * Default Oracle format used by the SQL*Loader utility.
     *
     * <p>
     * This is a comma-delimited format with the system line separator character as the record separator. Values are double quoted when needed and special
     * characters are escaped with {@code '"'}. The default NULL string is {@code ""}. Values are trimmed.
     * </p>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter(',') // default is {@code FIELDS TERMINATED BY ','}</li>
     * <li>withQuote('"')  // default is {@code OPTIONALLY ENCLOSED BY '"'}</li>
     * <li>withSystemRecordSeparator()</li>
     * <li>withTrim()</li>
     * <li>withIgnoreEmptyLines(false)</li>
     * <li>withEscape('\\')</li>
     * <li>withNullString("\\N")</li>
     * <li>withQuoteMode(QuoteMode.MINIMAL)</li>
     * </ul>
     *
     * @see Predefined#Oracle
     * @see <a href="https://docs.oracle.com/database/121/SUTIL/GUID-D1762699-8154-40F6-90DE-EFB8EB6A9AB0.htm#SUTIL4217">https://docs.oracle.com/database/121/SUTIL/GUID-D1762699-8154-40F6-90DE-EFB8EB6A9AB0.htm#SUTIL4217</a>
     * @since 1.6
     */
    // @formatter:off
    public static final CSVFormat ORACLE = DEFAULT
            .withDelimiter(COMMA)
            .withEscape(BACKSLASH)
            .withIgnoreEmptyLines(false)
            .withQuote(DOUBLE_QUOTE_CHAR)
            .withNullString("\\N")
            .withTrim()
            .withSystemRecordSeparator()
            .withQuoteMode(QuoteMode.MINIMAL);
    // @formatter:off

    /**
     * Default PostgreSQL CSV format used by the {@code COPY} operation.
     *
     * <p>
     * This is a comma-delimited format with a LF character as the line separator. Values are double quoted and special
     * characters are escaped with {@code '"'}. The default NULL string is {@code ""}.
     * </p>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter(',')</li>
     * <li>withQuote('"')</li>
     * <li>withRecordSeparator('\n')</li>
     * <li>withIgnoreEmptyLines(false)</li>
     * <li>withEscape('\\')</li>
     * <li>withNullString("")</li>
     * <li>withQuoteMode(QuoteMode.ALL_NON_NULL)</li>
     * </ul>
     *
     * @see Predefined#MySQL
     * @see <a href="https://www.postgresql.org/docs/current/static/sql-copy.html"> https://www.postgresql.org/docs/current/static/sql-copy.html
     *      -data.html</a>
     * @since 1.5
     */
    // @formatter:off
    public static final CSVFormat POSTGRESQL_CSV = DEFAULT
            .withDelimiter(COMMA)
            .withEscape(DOUBLE_QUOTE_CHAR)
            .withIgnoreEmptyLines(false)
            .withQuote(DOUBLE_QUOTE_CHAR)
            .withRecordSeparator(LF)
            .withNullString(EMPTY)
            .withQuoteMode(QuoteMode.ALL_NON_NULL);
    // @formatter:off

    /**
     * Default PostgreSQL text format used by the {@code COPY} operation.
     *
     * <p>
     * This is a tab-delimited format with a LF character as the line separator. Values are double quoted and special
     * characters are escaped with {@code '"'}. The default NULL string is {@code "\\N"}.
     * </p>
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter('\t')</li>
     * <li>withQuote('"')</li>
     * <li>withRecordSeparator('\n')</li>
     * <li>withIgnoreEmptyLines(false)</li>
     * <li>withEscape('\\')</li>
     * <li>withNullString("\\N")</li>
     * <li>withQuoteMode(QuoteMode.ALL_NON_NULL)</li>
     * </ul>
     *
     * @see Predefined#MySQL
     * @see <a href="https://www.postgresql.org/docs/current/static/sql-copy.html"> https://www.postgresql.org/docs/current/static/sql-copy.html</a>
     * @since 1.5
     */
    // @formatter:off
    public static final CSVFormat POSTGRESQL_TEXT = DEFAULT
            .withDelimiter(TAB)
            .withEscape(DOUBLE_QUOTE_CHAR)
            .withIgnoreEmptyLines(false)
            .withQuote(DOUBLE_QUOTE_CHAR)
            .withRecordSeparator(LF)
            .withNullString("\\N")
            .withQuoteMode(QuoteMode.ALL_NON_NULL);
    // @formatter:off

    /**
     * Comma separated format as defined by <a href="http://tools.ietf.org/html/rfc4180">RFC 4180</a>.
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter(',')</li>
     * <li>withQuote('"')</li>
     * <li>withRecordSeparator("\r\n")</li>
     * <li>withIgnoreEmptyLines(false)</li>
     * </ul>
     *
     * @see Predefined#RFC4180
     */
    public static final CSVFormat RFC4180 = DEFAULT.withIgnoreEmptyLines(false);

    private static final long serialVersionUID = 1L;

    /**
     * Tab-delimited format.
     *
     * <p>
     * Settings are:
     * </p>
     * <ul>
     * <li>withDelimiter('\t')</li>
     * <li>withQuote('"')</li>
     * <li>withRecordSeparator("\r\n")</li>
     * <li>withIgnoreSurroundingSpaces(true)</li>
     * </ul>
     *
     * @see Predefined#TDF
     */
    // @formatter:off
    public static final CSVFormat TDF = DEFAULT
            .withDelimiter(TAB)
            .withIgnoreSurroundingSpaces();
    // @formatter:on

    /**
     * Returns true if the given character is a line break character.
     *
     * @param c
     *            the character to check
     *
     * @return true if <code>c</code> is a line break character
     */
    private static boolean isLineBreak(final char c) {
        return c == LF || c == CR;
    }

    /**
     * Returns true if the given character is a line break character.
     *
     * @param c
     *            the character to check, may be null
     *
     * @return true if <code>c</code> is a line break character (and not null)
     */
    private static boolean isLineBreak(final Character c) {
        return clz.invokeMember("is_line_break", c).asBoolean();
    }

    /**
     * Creates a new CSV format with the specified delimiter.
     *
     * <p>
     * Use this method if you want to create a CSVFormat from scratch. All fields but the delimiter will be initialized
     * with null/false.
     * </p>
     *
     * @param delimiter
     *            the char used for value separation, must not be a line break character
     * @return a new CSV format.
     * @throws IllegalArgumentException
     *             if the delimiter is a line break character
     *
     * @see #DEFAULT
     * @see #RFC4180
     * @see #MYSQL
     * @see #EXCEL
     * @see #TDF
     */
    public static CSVFormat newFormat(final char delimiter) {
        return new CSVFormat(delimiter, null, null, null, null, false, false, null, null, null, null, false, false,
                false, false, false, false);
    }

    /**
     * Gets one of the predefined formats from {@link CSVFormat.Predefined}.
     *
     * @param format
     *            name
     * @return one of the predefined formats
     * @since 1.2
     */
    public static CSVFormat valueOf(final String format) {
        return CSVFormat.Predefined.valueOf(format).getFormat();
    }

    public Value getPythonObject() {
        return obj;
    }

    // manual serialization to save the data for the Value object
    private void writeObject(java.io.ObjectOutputStream out) throws IOException {
        // fetch nullable values first
        Value quoteCharVal = obj.invokeMember("get_quote_character");
        Value commentMarkerVal = obj.invokeMember("get_comment_marker");
        Value escapeCharVal = obj.invokeMember("get_escape_character");

        // write all attributes from the Value object
        out.writeObject(obj.getMember("delimiter").asString().charAt(0));
        out.writeObject(quoteCharVal.isNull() ? null : quoteCharVal.asString().charAt(0));
        out.writeObject(obj.getMember("quote_mode").as(QuoteMode.class));
        out.writeObject(commentMarkerVal.isNull() ? null : commentMarkerVal.asString().charAt(0));
        out.writeObject(escapeCharVal.isNull() ? null : escapeCharVal.asString().charAt(0));
        out.writeObject(obj.getMember("ignore_surrounding_spaces").asBoolean());
        out.writeObject(obj.getMember("ignore_empty_lines").asBoolean());
        out.writeObject(obj.getMember("record_separator").asString());
        out.writeObject(obj.getMember("null_string").asString());
        out.writeObject(obj.getMember("header_comments").as(String[].class));
        out.writeObject(obj.getMember("header").as(String[].class));
        out.writeObject(obj.getMember("skip_header_record").asBoolean());
        out.writeObject(obj.getMember("allow_missing_column_names").asBoolean());
        out.writeObject(obj.getMember("ignore_header_case").asBoolean());
        out.writeObject(obj.getMember("trim").asBoolean());
        out.writeObject(obj.getMember("trailing_delimiter").asBoolean());
        out.writeObject(obj.getMember("auto_flush").asBoolean());
    }

    // manual deserialization to load the data for the Value object
    private void readObject(java.io.ObjectInputStream in) throws IOException, ClassNotFoundException {
        char delimiter = (char) in.readObject();
        Character quoteChar = (Character) in.readObject();
        QuoteMode quoteMode = (QuoteMode) in.readObject();
        Character commentStart = (Character) in.readObject();
        Character escape = (Character) in.readObject();
        boolean ignoreSurroundingSpaces = (boolean) in.readObject();
        boolean ignoreEmptyLines = (boolean) in.readObject();
        String recordSeparator = (String) in.readObject();
        String nullString = (String) in.readObject();
        String[] headerComments = (String[]) in.readObject();
        String[] header = (String[]) in.readObject();
        boolean skipHeaderRecord = (boolean) in.readObject();
        boolean allowMissingColumnNames = (boolean) in.readObject();
        boolean ignoreHeaderCase = (boolean) in.readObject();
        boolean trim = (boolean) in.readObject();
        boolean trailingDelimiter = (boolean) in.readObject();
        boolean autoFlush = (boolean) in.readObject();
        obj = clz.newInstance(
                delimiter,
                quoteChar,
                quoteMode,
                commentStart,
                escape,
                ignoreSurroundingSpaces,
                ignoreEmptyLines,
                recordSeparator,
                nullString,
                headerComments,
                header,
                skipHeaderRecord,
                allowMissingColumnNames,
                ignoreHeaderCase,
                trim,
                trailingDelimiter,
                autoFlush);
    }

    /**
     * Creates a customized CSV format.
     *
     * @param delimiter
     *            the char used for value separation, must not be a line break character
     * @param quoteChar
     *            the Character used as value encapsulation marker, may be {@code null} to disable
     * @param quoteMode
     *            the quote mode
     * @param commentStart
     *            the Character used for comment identification, may be {@code null} to disable
     * @param escape
     *            the Character used to escape special characters in values, may be {@code null} to disable
     * @param ignoreSurroundingSpaces
     *            {@code true} when whitespaces enclosing values should be ignored
     * @param ignoreEmptyLines
     *            {@code true} when the parser should skip empty lines
     * @param recordSeparator
     *            the line separator to use for output
     * @param nullString
     *            the line separator to use for output
     * @param headerComments
     *            the comments to be printed by the Printer before the actual CSV data
     * @param header
     *            the header
     * @param skipHeaderRecord
     *            TODO
     * @param allowMissingColumnNames
     *            TODO
     * @param ignoreHeaderCase
     *            TODO
     * @param trim
     *            TODO
     * @param trailingDelimiter
     *            TODO
     * @param autoFlush
     * @throws IllegalArgumentException
     *             if the delimiter is a line break character
     */
    private CSVFormat(final char delimiter, final Character quoteChar, final QuoteMode quoteMode,
            final Character commentStart, final Character escape, final boolean ignoreSurroundingSpaces,
            final boolean ignoreEmptyLines, final String recordSeparator, final String nullString,
            final Object[] headerComments, final String[] header, final boolean skipHeaderRecord,
            final boolean allowMissingColumnNames, final boolean ignoreHeaderCase, final boolean trim,
            final boolean trailingDelimiter, final boolean autoFlush) {
        obj = clz.newInstance(
                delimiter,
                quoteChar,
                quoteMode,
                commentStart,
                escape,
                ignoreSurroundingSpaces,
                ignoreEmptyLines,
                recordSeparator,
                nullString,
                headerComments,
                header,
                skipHeaderRecord,
                allowMissingColumnNames,
                ignoreHeaderCase,
                trim,
                trailingDelimiter,
                autoFlush);
        this.validate();

    }

    private CSVFormat(final Value v) {
        this(
                v.getMember("delimiter").asString().charAt(0),
                v.getMember("quote_character").isNull() ? null : v.getMember("quote_character").asString().charAt(0),
                v.getMember("quote_mode").as(QuoteMode.class),
                v.getMember("comment_marker").isNull() ? null : v.getMember("comment_marker").asString().charAt(0),
                v.getMember("escape_character").isNull() ? null : v.getMember("escape_character").asString().charAt(0),
                v.getMember("ignore_surrounding_spaces").asBoolean(),
                v.getMember("ignore_empty_lines").asBoolean(),
                v.getMember("record_separator").asString(),
                v.getMember("null_string").asString(),
                v.invokeMember("get_header_comments").as(String[].class),
                v.invokeMember("get_header").as(String[].class),
                v.getMember("skip_header_record").asBoolean(),
                v.getMember("allow_missing_column_names").asBoolean(),
                v.getMember("ignore_header_case").asBoolean(),
                v.getMember("trim").asBoolean(),
                v.getMember("trailing_delimiter").asBoolean(),
                v.getMember("auto_flush").asBoolean());
    }

    @Override
    public boolean equals(final Object _obj) {
        return obj.invokeMember("__eq__", _obj).asBoolean();
    }

    /**
     * Formats the specified values.
     *
     * @param values
     *            the values to format
     * @return the formatted values
     */
    public String format(final Object... values) {
        if (values == null) {
            throw new NullPointerException("Null values");
        }
        return obj.invokeMember("format", values).asString();
    }

    /**
     * Specifies whether missing column names are allowed when parsing the header line.
     *
     * @return {@code true} if missing column names are allowed when parsing the header line, {@code false} to throw an
     *         {@link IllegalArgumentException}.
     */
    public boolean getAllowMissingColumnNames() {
        return obj.invokeMember("get_allow_missing_column_names").asBoolean();
    }

    /**
     * Returns whether to flush on close.
     *
     * @return whether to flush on close.
     * @since 1.6
     */
    public boolean getAutoFlush() {
        return obj.invokeMember("get_auto_flush").asBoolean();  
    }

    /**
     * Returns the character marking the start of a line comment.
     *
     * @return the comment start marker, may be {@code null}
     */
    public Character getCommentMarker() {
        Value v = obj.invokeMember("get_comment_marker");
        return v.isNull() ? null : v.asString().charAt(0);
    }

    /**
     * Returns the character delimiting the values (typically ';', ',' or '\t').
     *
     * @return the delimiter character
     */
    public char getDelimiter() {
        Value v = obj.invokeMember("get_delimiter");
        return v.isNull() ? null : v.asString().charAt(0);
    }

    /**
     * Returns the escape character.
     *
     * @return the escape character, may be {@code null}
     */
    public Character getEscapeCharacter() {
        Value v = obj.invokeMember("get_escape_character");
        return v.isNull() ? null : v.asString().charAt(0);
    }

    /**
     * Returns a copy of the header array.
     *
     * @return a copy of the header array; {@code null} if disabled, the empty array if to be read from the file
     */
    public String[] getHeader() {
        return obj.invokeMember("get_header").as(String[].class);
    }

    /**
     * Returns a copy of the header comment array.
     *
     * @return a copy of the header comment array; {@code null} if disabled.
     */
    public String[] getHeaderComments() {
        return obj.invokeMember("get_header_comments").as(String[].class);
    }

    /**
     * Specifies whether empty lines between records are ignored when parsing input.
     *
     * @return {@code true} if empty lines between records are ignored, {@code false} if they are turned into empty
     *         records.
     */
    public boolean getIgnoreEmptyLines() {
        return obj.invokeMember("get_ignore_empty_lines").asBoolean();
    }

    /**
     * Specifies whether header names will be accessed ignoring case.
     *
     * @return {@code true} if header names cases are ignored, {@code false} if they are case sensitive.
     * @since 1.3
     */
    public boolean getIgnoreHeaderCase() {
        return obj.invokeMember("get_ignore_header_case").asBoolean();
    }

    /**
     * Specifies whether spaces around values are ignored when parsing input.
     *
     * @return {@code true} if spaces around values are ignored, {@code false} if they are treated as part of the value.
     */
    public boolean getIgnoreSurroundingSpaces() {
        return obj.invokeMember("get_ignore_surrounding_spaces").asBoolean();
    }

    /**
     * Gets the String to convert to and from {@code null}.
     * <ul>
     * <li><strong>Reading:</strong> Converts strings equal to the given {@code nullString} to {@code null} when reading
     * records.</li>
     * <li><strong>Writing:</strong> Writes {@code null} as the given {@code nullString} when writing records.</li>
     * </ul>
     *
     * @return the String to convert to and from {@code null}. No substitution occurs if {@code null}
     */
    public String getNullString() {
        return obj.invokeMember("get_null_string").asString();
    }

    /**
     * Returns the character used to encapsulate values containing special characters.
     *
     * @return the quoteChar character, may be {@code null}
     */
    public Character getQuoteCharacter() {
        Value v = obj.invokeMember("get_quote_character");
        return v.isNull() ? null : v.asString().charAt(0);
    }

    /**
     * Returns the quote policy output fields.
     *
     * @return the quote policy
     */
    public QuoteMode getQuoteMode() {
        return obj.invokeMember("get_quote_mode").as(QuoteMode.class);
    }

    /**
     * Returns the record separator delimiting output records.
     *
     * @return the record separator
     */
    public String getRecordSeparator() {
        return obj.invokeMember("get_record_separator").asString();
    }

    /**
     * Returns whether to skip the header record.
     *
     * @return whether to skip the header record.
     */
    public boolean getSkipHeaderRecord() {
        return obj.invokeMember("get_skip_header_record").asBoolean();
    }

    /**
     * Returns whether to add a trailing delimiter.
     *
     * @return whether to add a trailing delimiter.
     * @since 1.3
     */
    public boolean getTrailingDelimiter() {
        return obj.invokeMember("get_trailing_delimiter").asBoolean();
    }

    /**
     * Returns whether to trim leading and trailing blanks.
     *
     * @return whether to trim leading and trailing blanks.
     */
    public boolean getTrim() {
        return obj.invokeMember("get_trim").asBoolean();
    }

    @Override
    public int hashCode() {
        return (int) obj.invokeMember("__hash__").asLong();
    }

    /**
     * Specifies whether comments are supported by this format.
     *
     * Note that the comment introducer character is only recognized at the start of a line.
     *
     * @return {@code true} is comments are supported, {@code false} otherwise
     */
    public boolean isCommentMarkerSet() {
        return obj.invokeMember("is_comment_marker_set").asBoolean();
    }

    /**
     * Returns whether escape are being processed.
     *
     * @return {@code true} if escapes are processed
     */
    public boolean isEscapeCharacterSet() {
        return obj.invokeMember("is_escape_character_set").asBoolean();
    }

    /**
     * Returns whether a nullString has been defined.
     *
     * @return {@code true} if a nullString is defined
     */
    public boolean isNullStringSet() {
        return obj.invokeMember("is_null_string_set").asBoolean();
    }

    /**
     * Returns whether a quoteChar has been defined.
     *
     * @return {@code true} if a quoteChar is defined
     */
    public boolean isQuoteCharacterSet() {
        return obj.invokeMember("is_quote_character_set").asBoolean();
    }

    /**
     * Parses the specified content.
     *
     * <p>
     * See also the various static parse methods on {@link CSVParser}.
     * </p>
     *
     * @param in
     *            the input stream
     * @return a parser over a stream of {@link CSVRecord}s.
     * @throws IOException
     *             If an I/O error occurs
     */
    public CSVParser parse(final Reader in) throws IOException {
        return new CSVParser(in, this);
    }

    /**
     * Prints to the specified output.
     *
     * <p>
     * See also {@link CSVPrinter}.
     * </p>
     *
     * @param out
     *            the output.
     * @return a printer to an output.
     * @throws IOException
     *             thrown if the optional header cannot be printed.
     */
    public CSVPrinter print(final Appendable out) throws IOException {
        return new CSVPrinter(out, this);
    }

    /**
     * Prints to the specified output.
     *
     * <p>
     * See also {@link CSVPrinter}.
     * </p>
     *
     * @param out
     *            the output.
     * @param charset
     *            A charset.
     * @return a printer to an output.
     * @throws IOException
     *             thrown if the optional header cannot be printed.
     * @since 1.5
     */
    @SuppressWarnings("resource")
    public CSVPrinter print(final File out, final Charset charset) throws IOException {
        // The writer will be closed when close() is called.
        return new CSVPrinter(new OutputStreamWriter(new FileOutputStream(out), charset), this);
    }

    /**
     * Prints the {@code value} as the next value on the line to {@code out}. The value will be escaped or encapsulated
     * as needed. Useful when one wants to avoid creating CSVPrinters.
     *
     * @param value
     *            value to output.
     * @param out
     *            where to print the value.
     * @param newRecord
     *            if this a new record.
     * @throws IOException
     *             If an I/O error occurs.
     * @since 1.4
     */
    public void print(final Object value, final Appendable out, final boolean newRecord) throws IOException {
        obj.invokeMember("print", value, out, newRecord);
    }


    /**
     * Prints to the specified output.
     *
     * <p>
     * See also {@link CSVPrinter}.
     * </p>
     *
     * @param out
     *            the output.
     * @param charset
     *            A charset.
     * @return a printer to an output.
     * @throws IOException
     *             thrown if the optional header cannot be printed.
     * @since 1.5
     */
    public CSVPrinter print(final Path out, final Charset charset) throws IOException {
        return print(Files.newBufferedWriter(out, charset));
    }

    /**
     * Prints to the {@link System#out}.
     *
     * <p>
     * See also {@link CSVPrinter}.
     * </p>
     *
     * @return a printer to {@link System#out}.
     * @throws IOException
     *             thrown if the optional header cannot be printed.
     * @since 1.5
     */
    public CSVPrinter printer() throws IOException {
        return new CSVPrinter(System.out, this);
    }

    /**
     * Outputs the trailing delimiter (if set) followed by the record separator (if set).
     *
     * @param out
     *            where to write
     * @throws IOException
     *             If an I/O error occurs
     * @since 1.4
     */
    public void println(final Appendable out) throws IOException {
        obj.invokeMember("println", out);
    }

    /**
     * Prints the given {@code values} to {@code out} as a single record of delimiter separated values followed by the
     * record separator.
     *
     * <p>
     * The values will be quoted if needed. Quotes and new-line characters will be escaped. This method adds the record
     * separator to the output after printing the record, so there is no need to call {@link #println(Appendable)}.
     * </p>
     *
     * @param out
     *            where to write.
     * @param values
     *            values to output.
     * @throws IOException
     *             If an I/O error occurs.
     * @since 1.4
     */
    public void printRecord(final Appendable out, final Object... values) throws IOException {
        obj.invokeMember("print_record", out, values);
    }

    @Override
    public String toString() {
        return obj.invokeMember("__str__").asString();
    }

    private String[] toStringArray(final Object[] values) {
        return obj.invokeMember("to_string_array", values).as(String[].class);
    }

    private CharSequence trim(final CharSequence charSequence) {
        if (charSequence instanceof String) {
            return ((String) charSequence).trim();
        }
        final int count = charSequence.length();
        int len = count;
        int pos = 0;

        while (pos < len && charSequence.charAt(pos) <= SP) {
            pos++;
        }
        while (pos < len && charSequence.charAt(len - 1) <= SP) {
            len--;
        }
        return pos > 0 || len < count ? charSequence.subSequence(pos, len) : charSequence;
    }

    /**
     * Verifies the consistency of the parameters and throws an IllegalArgumentException if necessary.
     *
     * @throws IllegalArgumentException
     */
    private void validate() throws IllegalArgumentException {
        try {
            obj.invokeMember("validate");
        } catch (PolyglotException e) {
            // if polyglot exception is ValueError, throw IllegalArgumentException
            String exceptionType = e.getMessage().split(":")[0];
            String msg = e.getMessage().split(":")[1];
            if (exceptionType.equals("ValueError")) {
                throw new IllegalArgumentException(msg);
            }
            throw new RuntimeException(e);
        }
    }

    /**
     * Returns a new {@code CSVFormat} with the missing column names behavior of the format set to {@code true}
     *
     * @return A new CSVFormat that is equal to this but with the specified missing column names behavior.
     * @see #withAllowMissingColumnNames(boolean)
     * @since 1.1
     */
    public CSVFormat withAllowMissingColumnNames() {
        return this.withAllowMissingColumnNames(true);
    }

    /**
     * Returns a new {@code CSVFormat} with the missing column names behavior of the format set to the given value.
     *
     * @param allowMissingColumnNames
     *            the missing column names behavior, {@code true} to allow missing column names in the header line,
     *            {@code false} to cause an {@link IllegalArgumentException} to be thrown.
     * @return A new CSVFormat that is equal to this but with the specified missing column names behavior.
     */
    public CSVFormat withAllowMissingColumnNames(final boolean allowMissingColumnNames) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("allow_missing_column_names", allowMissingColumnNames);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with whether to flush on close.
     *
     * @param autoFlush
     *            whether to flush on close.
     *
     * @return A new CSVFormat that is equal to this but with the specified autoFlush setting.
     * @since 1.6
     */
    public CSVFormat withAutoFlush(final boolean autoFlush) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("auto_flush", autoFlush);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the comment start marker of the format set to the specified character.
     *
     * Note that the comment start character is only recognized at the start of a line.
     *
     * @param commentMarker
     *            the comment start marker
     * @return A new CSVFormat that is equal to this one but with the specified character as the comment start marker
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withCommentMarker(final char commentMarker) {
        return withCommentMarker(Character.valueOf(commentMarker));
    }

    /**
     * Returns a new {@code CSVFormat} with the comment start marker of the format set to the specified character.
     *
     * Note that the comment start character is only recognized at the start of a line.
     *
     * @param commentMarker
     *            the comment start marker, use {@code null} to disable
     * @return A new CSVFormat that is equal to this one but with the specified character as the comment start marker
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withCommentMarker(final Character commentMarker) {
        if (isLineBreak(commentMarker)) {
            throw new IllegalArgumentException("The comment start marker character cannot be a line break");
        }
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("comment_marker", commentMarker);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the delimiter of the format set to the specified character.
     *
     * @param delimiter
     *            the delimiter character
     * @return A new CSVFormat that is equal to this with the specified character as delimiter
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withDelimiter(final char delimiter) {
        if (isLineBreak(delimiter)) {
            throw new IllegalArgumentException("The delimiter cannot be a line break");
        }

       CSVFormat newFormat = new CSVFormat(obj);
       newFormat.obj.putMember("delimiter", delimiter);
       newFormat.validate();
       return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the escape character of the format set to the specified character.
     *
     * @param escape
     *            the escape character
     * @return A new CSVFormat that is equal to his but with the specified character as the escape character
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withEscape(final char escape) {
        return withEscape(Character.valueOf(escape));
    }

    /**
     * Returns a new {@code CSVFormat} with the escape character of the format set to the specified character.
     *
     * @param escape
     *            the escape character, use {@code null} to disable
     * @return A new CSVFormat that is equal to this but with the specified character as the escape character
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withEscape(final Character escape) {
        if (isLineBreak(escape)) {
            throw new IllegalArgumentException("The escape character cannot be a line break");
        }
        CSVFormat newFormat = new CSVFormat(obj);
       newFormat.obj.putMember("escape_character", escape);
       newFormat.validate();
       return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} using the first record as header.
     *
     * <p>
     * Calling this method is equivalent to calling:
     * </p>
     *
     * <pre>
     * CSVFormat format = aFormat.withHeader().withSkipHeaderRecord();
     * </pre>
     *
     * @return A new CSVFormat that is equal to this but using the first record as header.
     * @see #withSkipHeaderRecord(boolean)
     * @see #withHeader(String...)
     * @since 1.3
     */
    public CSVFormat withFirstRecordAsHeader() {
        return withHeader().withSkipHeaderRecord();
    }

    /**
     * Returns a new {@code CSVFormat} with the header of the format defined by the enum class.
     *
     * <p>
     * Example:
     * </p>
     * <pre>
     * public enum Header {
     *     Name, Email, Phone
     * }
     *
     * CSVFormat format = aformat.withHeader(Header.class);
     * </pre>
     * <p>
     * The header is also used by the {@link CSVPrinter}.
     * </p>
     *
     * @param headerEnum
     *            the enum defining the header, {@code null} if disabled, empty if parsed automatically, user specified
     *            otherwise.
     *
     * @return A new CSVFormat that is equal to this but with the specified header
     * @see #withHeader(String...)
     * @see #withSkipHeaderRecord(boolean)
     * @since 1.3
     */
    public CSVFormat withHeader(final Class<? extends Enum<?>> headerEnum) {
        String[] header = null;
        if (headerEnum != null) {
            final Enum<?>[] enumValues = headerEnum.getEnumConstants();
            header = new String[enumValues.length];
            for (int i = 0; i < enumValues.length; i++) {
                header[i] = enumValues[i].name();
            }
        }
        return withHeader(header);
    }

    /**
     * Returns a new {@code CSVFormat} with the header of the format set from the result set metadata. The header can
     * either be parsed automatically from the input file with:
     *
     * <pre>
     * CSVFormat format = aformat.withHeader();
     * </pre>
     *
     * or specified manually with:
     *
     * <pre>
     * CSVFormat format = aformat.withHeader(resultSet);
     * </pre>
     * <p>
     * The header is also used by the {@link CSVPrinter}.
     * </p>
     *
     * @param resultSet
     *            the resultSet for the header, {@code null} if disabled, empty if parsed automatically, user specified
     *            otherwise.
     *
     * @return A new CSVFormat that is equal to this but with the specified header
     * @throws SQLException
     *             SQLException if a database access error occurs or this method is called on a closed result set.
     * @since 1.1
     */
    public CSVFormat withHeader(final ResultSet resultSet) throws SQLException {
        return withHeader(resultSet != null ? resultSet.getMetaData() : null);
    }

    /**
     * Returns a new {@code CSVFormat} with the header of the format set from the result set metadata. The header can
     * either be parsed automatically from the input file with:
     *
     * <pre>
     * CSVFormat format = aformat.withHeader();
     * </pre>
     *
     * or specified manually with:
     *
     * <pre>
     * CSVFormat format = aformat.withHeader(metaData);
     * </pre>
     * <p>
     * The header is also used by the {@link CSVPrinter}.
     * </p>
     *
     * @param metaData
     *            the metaData for the header, {@code null} if disabled, empty if parsed automatically, user specified
     *            otherwise.
     *
     * @return A new CSVFormat that is equal to this but with the specified header
     * @throws SQLException
     *             SQLException if a database access error occurs or this method is called on a closed result set.
     * @since 1.1
     */
    public CSVFormat withHeader(final ResultSetMetaData metaData) throws SQLException {
        String[] labels = null;
        if (metaData != null) {
            final int columnCount = metaData.getColumnCount();
            labels = new String[columnCount];
            for (int i = 0; i < columnCount; i++) {
                labels[i] = metaData.getColumnLabel(i + 1);
            }
        }
        return withHeader(labels);
    }

    /**
     * Returns a new {@code CSVFormat} with the header of the format set to the given values. The header can either be
     * parsed automatically from the input file with:
     *
     * <pre>
     * CSVFormat format = aformat.withHeader();
     * </pre>
     *
     * or specified manually with:
     *
     * <pre>
     * CSVFormat format = aformat.withHeader(&quot;name&quot;, &quot;email&quot;, &quot;phone&quot;);
     * </pre>
     * <p>
     * The header is also used by the {@link CSVPrinter}.
     * </p>
     *
     * @param header
     *            the header, {@code null} if disabled, empty if parsed automatically, user specified otherwise.
     *
     * @return A new CSVFormat that is equal to this but with the specified header
     * @see #withSkipHeaderRecord(boolean)
     */
    public CSVFormat withHeader(final String... header) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("header", header);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the header comments of the format set to the given values. The comments will
     * be printed first, before the headers. This setting is ignored by the parser.
     *
     * <pre>
     * CSVFormat format = aformat.withHeaderComments(&quot;Generated by Apache Commons CSV 1.1.&quot;, new Date());
     * </pre>
     *
     * @param headerComments
     *            the headerComments which will be printed by the Printer before the actual CSV data.
     *
     * @return A new CSVFormat that is equal to this but with the specified header
     * @see #withSkipHeaderRecord(boolean)
     * @since 1.1
     */
    public CSVFormat withHeaderComments(final Object... headerComments) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("header_comments", toStringArray(headerComments));
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the empty line skipping behavior of the format set to {@code true}.
     *
     * @return A new CSVFormat that is equal to this but with the specified empty line skipping behavior.
     * @since {@link #withIgnoreEmptyLines(boolean)}
     * @since 1.1
     */
    public CSVFormat withIgnoreEmptyLines() {
        return this.withIgnoreEmptyLines(true);
    }

    /**
     * Returns a new {@code CSVFormat} with the empty line skipping behavior of the format set to the given value.
     *
     * @param ignoreEmptyLines
     *            the empty line skipping behavior, {@code true} to ignore the empty lines between the records,
     *            {@code false} to translate empty lines to empty records.
     * @return A new CSVFormat that is equal to this but with the specified empty line skipping behavior.
     */
    public CSVFormat withIgnoreEmptyLines(final boolean ignoreEmptyLines) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("ignore_empty_lines", ignoreEmptyLines);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the header ignore case behavior set to {@code true}.
     *
     * @return A new CSVFormat that will ignore case header name.
     * @see #withIgnoreHeaderCase(boolean)
     * @since 1.3
     */
    public CSVFormat withIgnoreHeaderCase() {
        return this.withIgnoreHeaderCase(true);
    }

    /**
     * Returns a new {@code CSVFormat} with whether header names should be accessed ignoring case.
     *
     * @param ignoreHeaderCase
     *            the case mapping behavior, {@code true} to access name/values, {@code false} to leave the mapping as
     *            is.
     * @return A new CSVFormat that will ignore case header name if specified as {@code true}
     * @since 1.3
     */
    public CSVFormat withIgnoreHeaderCase(final boolean ignoreHeaderCase) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("ignore_header_case", ignoreHeaderCase);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the trimming behavior of the format set to {@code true}.
     *
     * @return A new CSVFormat that is equal to this but with the specified trimming behavior.
     * @see #withIgnoreSurroundingSpaces(boolean)
     * @since 1.1
     */
    public CSVFormat withIgnoreSurroundingSpaces() {
        return this.withIgnoreSurroundingSpaces(true);
    }

    /**
     * Returns a new {@code CSVFormat} with the trimming behavior of the format set to the given value.
     *
     * @param ignoreSurroundingSpaces
     *            the trimming behavior, {@code true} to remove the surrounding spaces, {@code false} to leave the
     *            spaces as is.
     * @return A new CSVFormat that is equal to this but with the specified trimming behavior.
     */
    public CSVFormat withIgnoreSurroundingSpaces(final boolean ignoreSurroundingSpaces) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("ignore_surrounding_spaces", ignoreSurroundingSpaces);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with conversions to and from null for strings on input and output.
     * <ul>
     * <li><strong>Reading:</strong> Converts strings equal to the given {@code nullString} to {@code null} when reading
     * records.</li>
     * <li><strong>Writing:</strong> Writes {@code null} as the given {@code nullString} when writing records.</li>
     * </ul>
     *
     * @param nullString
     *            the String to convert to and from {@code null}. No substitution occurs if {@code null}
     *
     * @return A new CSVFormat that is equal to this but with the specified null conversion string.
     */
    public CSVFormat withNullString(final String nullString) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("null_string", nullString);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the quoteChar of the format set to the specified character.
     *
     * @param quoteChar
     *            the quoteChar character
     * @return A new CSVFormat that is equal to this but with the specified character as quoteChar
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withQuote(final char quoteChar) {
        return withQuote(Character.valueOf(quoteChar));
    }

    /**
     * Returns a new {@code CSVFormat} with the quoteChar of the format set to the specified character.
     *
     * @param quoteChar
     *            the quoteChar character, use {@code null} to disable
     * @return A new CSVFormat that is equal to this but with the specified character as quoteChar
     * @throws IllegalArgumentException
     *             thrown if the specified character is a line break
     */
    public CSVFormat withQuote(final Character quoteChar) {
        if (isLineBreak(quoteChar)) {
            throw new IllegalArgumentException("The quoteChar cannot be a line break");
        }
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("quote_character", quoteChar);
        // newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the output quote policy of the format set to the specified value.
     *
     * @param quoteModePolicy
     *            the quote policy to use for output.
     *
     * @return A new CSVFormat that is equal to this but with the specified quote policy
     */
    public CSVFormat withQuoteMode(final QuoteMode quoteModePolicy) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("quote_mode", quoteModePolicy);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the record separator of the format set to the specified character.
     *
     * <p>
     * <strong>Note:</strong> This setting is only used during printing and does not affect parsing. Parsing currently
     * only works for inputs with '\n', '\r' and "\r\n"
     * </p>
     *
     * @param recordSeparator
     *            the record separator to use for output.
     *
     * @return A new CSVFormat that is equal to this but with the specified output record separator
     */
    public CSVFormat withRecordSeparator(final char recordSeparator) {
        return withRecordSeparator(String.valueOf(recordSeparator));
    }

    /**
     * Returns a new {@code CSVFormat} with the record separator of the format set to the specified String.
     *
     * <p>
     * <strong>Note:</strong> This setting is only used during printing and does not affect parsing. Parsing currently
     * only works for inputs with '\n', '\r' and "\r\n"
     * </p>
     *
     * @param recordSeparator
     *            the record separator to use for output.
     *
     * @return A new CSVFormat that is equal to this but with the specified output record separator
     * @throws IllegalArgumentException
     *             if recordSeparator is none of CR, LF or CRLF
     */
    public CSVFormat withRecordSeparator(final String recordSeparator) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("record_separator", recordSeparator);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with skipping the header record set to {@code true}.
     *
     * @return A new CSVFormat that is equal to this but with the the specified skipHeaderRecord setting.
     * @see #withSkipHeaderRecord(boolean)
     * @see #withHeader(String...)
     * @since 1.1
     */
    public CSVFormat withSkipHeaderRecord() {
        return this.withSkipHeaderRecord(true);
    }

    /**
     * Returns a new {@code CSVFormat} with whether to skip the header record.
     *
     * @param skipHeaderRecord
     *            whether to skip the header record.
     *
     * @return A new CSVFormat that is equal to this but with the the specified skipHeaderRecord setting.
     * @see #withHeader(String...)
     */
    public CSVFormat withSkipHeaderRecord(final boolean skipHeaderRecord) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("skip_header_record", skipHeaderRecord);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} with the record separator of the format set to the operating system's line
     * separator string, typically CR+LF on Windows and LF on Linux.
     *
     * <p>
     * <strong>Note:</strong> This setting is only used during printing and does not affect parsing. Parsing currently
     * only works for inputs with '\n', '\r' and "\r\n"
     * </p>
     *
     * @return A new CSVFormat that is equal to this but with the operating system's line separator string.
     * @since 1.6
     */
    public CSVFormat withSystemRecordSeparator() {
        return withRecordSeparator(System.getProperty("line.separator"));
    }

    /**
     * Returns a new {@code CSVFormat} to add a trailing delimiter.
     *
     * @return A new CSVFormat that is equal to this but with the trailing delimiter setting.
     * @since 1.3
     */
    public CSVFormat withTrailingDelimiter() {
        return withTrailingDelimiter(true);
    }

    /**
     * Returns a new {@code CSVFormat} with whether to add a trailing delimiter.
     *
     * @param trailingDelimiter
     *            whether to add a trailing delimiter.
     *
     * @return A new CSVFormat that is equal to this but with the specified trailing delimiter setting.
     * @since 1.3
     */
    public CSVFormat withTrailingDelimiter(final boolean trailingDelimiter) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("trailing_delimiter", trailingDelimiter);
        newFormat.validate();
        return newFormat;
    }

    /**
     * Returns a new {@code CSVFormat} to trim leading and trailing blanks.
     *
     * @return A new CSVFormat that is equal to this but with the trim setting on.
     * @since 1.3
     */
    public CSVFormat withTrim() {
        return withTrim(true);
    }

    /**
     * Returns a new {@code CSVFormat} with whether to trim leading and trailing blanks.
     *
     * @param trim
     *            whether to trim leading and trailing blanks.
     *
     * @return A new CSVFormat that is equal to this but with the specified trim setting.
     * @since 1.3
     */
    public CSVFormat withTrim(final boolean trim) {
        CSVFormat newFormat = new CSVFormat(obj);
        newFormat.obj.putMember("trim", trim);
        newFormat.validate();
        return newFormat;
    }
}
