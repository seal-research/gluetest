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

import static org.apache.commons.csv.Constants.BACKSPACE;
import static org.apache.commons.csv.Constants.CR;
import static org.apache.commons.csv.Constants.END_OF_STREAM;
import static org.apache.commons.csv.Constants.FF;
import static org.apache.commons.csv.Constants.LF;
import static org.apache.commons.csv.Constants.TAB;
import static org.apache.commons.csv.Constants.UNDEFINED;
import static org.apache.commons.csv.Token.Type.COMMENT;
import static org.apache.commons.csv.Token.Type.EOF;
import static org.apache.commons.csv.Token.Type.EORECORD;
import static org.apache.commons.csv.Token.Type.INVALID;
import static org.apache.commons.csv.Token.Type.TOKEN;

import java.io.Closeable;
import java.io.IOException;

import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;

/**
 * Lexical analyzer.
 */
final class Lexer implements Closeable {

    private static Value clz = ContextInitializer.getPythonClass("lexer.py", "Lexer");
    private transient Value obj;

    public Value getPythonObject() {
        return obj;
    }

    String getFirstEol(){
        return obj.getMember("first_eol").asString();
    }

    Lexer(final CSVFormat format, final ExtendedBufferedReader reader) {
        this.obj = clz.newInstance(format, reader.getPythonObject());
    }

    /**
     * Returns the next token.
     * <p>
     * A token corresponds to a term, a record change or an end-of-file indicator.
     * </p>
     *
     * @param token
     *            an existing Token object to reuse. The caller is responsible to initialize the Token.
     * @return the next token found
     * @throws java.io.IOException
     *             on stream access error
     */
    Token nextToken(final Token token) throws IOException {
        try{
            token.setPythonObject(obj.invokeMember("next_token", token.getPythonObject()));
            return token;
        } catch (PolyglotException e) {
            // if polyglot exception is OSError (IOError), throw IOException
            String exceptionType = e.getMessage().split(":")[0];
            String msg = e.getMessage().split(":")[1];
            System.out.println(e.getMessage());
            if (exceptionType.equals("OSError")) {
                throw new IOException(msg);
            }
            throw new RuntimeException(e);
        }
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
     * Returns the current character position
     *
     * @return the current character position
     */
    long getCharacterPosition() {
        return obj.invokeMember("get_character_position").asLong();
    }

    // TODO escape handling needs more work
    /**
     * Handle an escape sequence.
     * The current character must be the escape character.
     * On return, the next character is available by calling {@link ExtendedBufferedReader#getLastChar()}
     * on the input stream.
     *
     * @return the unescaped character (as an int) or {@link Constants#END_OF_STREAM} if char following the escape is
     *      invalid.
     * @throws IOException if there is a problem reading the stream or the end of stream is detected:
     *      the escape character is not allowed at end of stream
     */
    int readEscape() throws IOException {
        return obj.invokeMember("read_escape").asInt();
    }

    /**
     * Greedily accepts \n, \r and \r\n This checker consumes silently the second control-character...
     *
     * @return true if the given or next character is a line-terminator
     */
    boolean readEndOfLine(int ch) throws IOException {
        return obj.invokeMember("read_end_of_line", ch).asBoolean();
    }

    boolean isClosed() {
        return obj.invokeMember("is_closed").asBoolean();
    }

    /**
     * @return true if the given char is a whitespace character
     */
    boolean isWhitespace(final int ch) {
        return obj.invokeMember("is_whitespace", ch).asBoolean();
    }

    /**
     * Checks if the current character represents the start of a line: a CR, LF or is at the start of the file.
     *
     * @param ch the character to check
     * @return true if the character is at the start of a line.
     */
    boolean isStartOfLine(final int ch) {
        return obj.invokeMember("is_start_of_line", ch).asBoolean();
    }

    /**
     * @return true if the given character indicates end of file
     */
    boolean isEndOfFile(final int ch) {
        return obj.invokeMember("is_end_of_file", ch).asBoolean();
    }

    boolean isDelimiter(final int ch) {
        return obj.invokeMember("is_delimiter", ch).asBoolean();
    }

    boolean isEscape(final int ch) {
        return obj.invokeMember("is_escape", ch).asBoolean();
    }

    boolean isQuoteChar(final int ch) {
        return obj.invokeMember("is_quote_char", ch).asBoolean();
    }

    boolean isCommentStart(final int ch) {
        return obj.invokeMember("is_comment_start", ch).asBoolean();
    }

    private boolean isMetaChar(final int ch) {
        return obj.invokeMember("is_meta_char", ch).asBoolean();
    }

    /**
     * Closes resources.
     *
     * @throws IOException
     *             If an I/O error occurs
     */
    @Override
    public void close() throws IOException {
        obj.invokeMember("close");
    }
}
