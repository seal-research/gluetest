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
import static org.apache.commons.csv.Constants.END_OF_STREAM;
import static org.apache.commons.csv.Constants.LF;
import static org.apache.commons.csv.Constants.UNDEFINED;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.Reader;

import org.graalvm.polyglot.Value;

/**
 * A special buffered reader which supports sophisticated read access.
 * <p>
 * In particular the reader supports a look-ahead option, which allows you to see the next char returned by
 * {@link #read()}. This reader also tracks how many characters have been read with {@link #getPosition()}.
 * </p>
 */
final class ExtendedBufferedReader extends BufferedReader {

    /** glue code attributes */
    private static Value clz = ContextInitializer.getPythonClass("extended_buffered_reader.py", "ExtendedBufferedReader"); 
    private Value obj;

    public Value getPythonObject() {
        return obj;
    }

    /**
     * Created extended buffered reader using default buffer-size
     */
    ExtendedBufferedReader(final Reader reader) {
        super(reader);
        obj = clz.newInstance(reader, true);
    }

    /**
     * Converts a Python character to an integer value.
     * If value is a string, it invokes the "_ord" method in Python.
     * If the given value is not a string, it directly coerces to an integer value.
     *
     * @param v the value to be converted
     * @return the integer representation of the Python character
     */
    private int convertPythonCharToInt(Value v) {
        if (v.isString())
            return (int) v.asString().charAt(0);
        else
            return v.asInt();
    }

    @Override
    public int read() throws IOException {
       return convertPythonCharToInt(obj.invokeMember("read"));
    }

    /**
     * Returns the last character that was read as an integer (0 to 65535). This will be the last character returned by
     * any of the read methods. This will not include a character read using the {@link #lookAhead()} method. If no
     * character has been read then this will return {@link Constants#UNDEFINED}. If the end of the stream was reached
     * on the last read then this will return {@link Constants#END_OF_STREAM}.
     *
     * @return the last character that was read
     */
    int getLastChar() {
        // return lastChar;
        return convertPythonCharToInt(obj.invokeMember("get_last_char"));
    }

    @Override
    public int read(final char[] buf, final int offset, final int length) throws IOException {
        return convertPythonCharToInt(obj.invokeMember("read", buf, offset, length));
    }

    /**
     * Calls {@link BufferedReader#readLine()} which drops the line terminator(s). This method should only be called
     * when processing a comment, otherwise information can be lost.
     * <p>
     * Increments {@link #eolCounter}
     * <p>
     * Sets {@link #lastChar} to {@link Constants#END_OF_STREAM} at EOF, otherwise to LF
     *
     * @return the line that was read, or null if reached EOF.
     */
    @Override
    public String readLine() throws IOException {
        return obj.invokeMember("read_line").asString();
    }

    /**
     * Returns the next character in the current reader without consuming it. So the next call to {@link #read()} will
     * still return this value. Does not affect line number or last character.
     *
     * @return the next character
     *
     * @throws IOException
     *             if there is an error in reading
     */
    int lookAhead() throws IOException {
        return convertPythonCharToInt(obj.invokeMember("look_ahead"));
    }

    /**
     * Returns the current line number
     *
     * @return the current line number
     */
    long getCurrentLineNumber() {
        return obj.invokeMember("get_current_line_number").asLong();
    }

    /**
     * Gets the character position in the reader.
     *
     * @return the current position in the reader (counting characters, not bytes since this is a Reader)
     */
    long getPosition() {
        return obj.invokeMember("get_position").asLong();
    }

    public boolean isClosed() {
        return obj.invokeMember("is_closed").asBoolean();
    }

    /**
     * Closes the stream.
     *
     * @throws IOException
     *             If an I/O error occurs
     */
    @Override
    public void close() throws IOException {
        obj.invokeMember("close");
    }

}
