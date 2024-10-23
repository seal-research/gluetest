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

import static org.apache.commons.csv.Token.Type.INVALID;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Value;
/**
 * Internal token representation.
 * <p/>
 * It is used as contract between the lexer and the parser.
 */
final class Token {

    enum Type {
        /** Token has no valid content, i.e. is in its initialized state. */
        INVALID,

        /** Token with content, at beginning or in the middle of a line. */
        TOKEN,

        /** Token (which can have content) when the end of file is reached. */
        EOF,

        /** Token with content when the end of a line is reached. */
        EORECORD,

        /** Token is a comment line. */
        COMMENT
    }

    private static Value clz;
    private static Value pythonObj;


    /** Token ready flag: indicates a valid token with content (ready for the parser). */
    boolean isReady;
    
    static {
        clz = ContextInitializer.getPythonClass("token.py", "Token");
    }

    public Value getPythonObject() {
        return pythonObj;
    }
    
    public Token() {
        pythonObj = clz.newInstance();
    }
    
    public Token(Value obj) {
        pythonObj = obj;
    }

    /** Most places assume direct access to attributes - we allow that behavior
     * here by exposing the python object directly.
     */
    public void setPythonObject(Value obj) {
        pythonObj = obj;
    }

    void reset() {
        pythonObj.invokeMember("reset");
    }

    /**
     * Eases IDE debugging.
     *
     * @return a string helpful for debugging.
     */
    @Override
    public String toString() {
        return pythonObj.invokeMember("to_string").asString();
    }

    /**
     * Fetches the type of the token from the python object.
     *
     * @return the type of the token.
     */
    Token.Type getType() {
        // setType already stores a Java object in python, we can simply cast it back here
        Value typeValue =  pythonObj.invokeMember("get_type");
        if (typeValue.isHostObject())
            return typeValue.as(Token.Type.class);
        
        // check if python type, if so, convert to Java type
        return Token.Type.valueOf(typeValue.getMember("name").asString());
    }

    /**
     * Returns the ready flag of the token.
     *
     * @return the ready flag of the token.
     */
    boolean isReady() {
        return pythonObj.getMember("is_ready").asBoolean();
    }

    /**
     * Sets the type of the token.
     * @param type the type of the token.
     */
    void setType(final Token.Type type) {
        pythonObj.invokeMember("set_type", type);
    }

    /**
     * Sets the token ready flag.
     * @param isReady the token ready flag.
     */
    void setReady(final boolean isReady) {
        pythonObj.invokeMember("set_ready", isReady);
    }

    /**
     * Returns the content of the token.
     *
     * @return the content of the token.
     */
    String getContent() {
        return pythonObj.getMember("content").asString();
    }

    /**
     * Sets the content of the token.
     * @param content the content of the token.
     */
    void setContent(final String content) {
        pythonObj.invokeMember("set_content", content);
    }

    /**
     * Appends a string to the content of the token.
     * @param str the string to append.
     */
    void append(final String str) {
        pythonObj.invokeMember("append", str);
    }

}
