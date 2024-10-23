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

import java.util.HashMap;
import java.util.Map;

import org.graalvm.polyglot.Value;

/**
 * The class PosixParser provides an implementation of the {@link Parser#flatten(Options,String[],boolean) flatten}
 * method.
 *
 * @deprecated since 1.3, use the {@link DefaultParser} instead
 */
@Deprecated
public class PosixParser extends Parser {

    private static Value clz = ContextInitializer.getPythonClass("posix_parser.py", "PosixParser");

    public PosixParser() {
        parserObj = clz.execute();
    }

    public PosixParser(Value v) {
        parserObj = v;
    }

    /** Cache for wrappers to python objects  */
    private static Map<Value, PosixParser> cache = new HashMap<>();

    public static PosixParser create(final Value foreignPosixParser) {
        if (foreignPosixParser.isNull()) {
            return null;
        }
        return cache.computeIfAbsent(foreignPosixParser, PosixParser::new);
    }

    /**
     * <p>
     * An implementation of {@link Parser}'s abstract {@link Parser#flatten(Options,String[],boolean) flatten} method.
     * </p>
     *
     * <p>
     * The following are the rules used by this flatten method.
     * </p>
     * <ol>
     * <li>if {@code stopAtNonOption} is <b>true</b> then do not burst anymore of {@code arguments} entries, just
     * add each successive entry without further processing. Otherwise, ignore {@code stopAtNonOption}.</li>
     * <li>if the current {@code arguments} entry is "<b>--</b>" just add the entry to the list of processed
     * tokens</li>
     * <li>if the current {@code arguments} entry is "<b>-</b>" just add the entry to the list of processed tokens</li>
     * <li>if the current {@code arguments} entry is two characters in length and the first character is "<b>-</b>"
     * then check if this is a valid {@link Option} id. If it is a valid id, then add the entry to the list of processed
     * tokens and set the current {@link Option} member. If it is not a valid id and {@code stopAtNonOption} is true,
     * then the remaining entries are copied to the list of processed tokens. Otherwise, the current entry is ignored.</li>
     * <li>if the current {@code arguments} entry is more than two characters in length and the first character is
     * "<b>-</b>" then we need to burst the entry to determine its constituents. For more information on the bursting
     * algorithm see {@link PosixParser#burstToken(String, boolean) burstToken}.</li>
     * <li>if the current {@code arguments} entry is not handled by any of the previous rules, then the entry is added
     * to the list of processed tokens.</li>
     * </ol>
     *
     * @param options The command line {@link Options}
     * @param arguments The command line arguments to be parsed
     * @param stopAtNonOption Specifies whether to stop flattening when an non option is found.
     * @return The flattened {@code arguments} String array.
     */
    @Override
    protected String[] flatten(final Options options, final String[] arguments, final boolean stopAtNonOption) throws ParseException {
        return parserObj.invokeMember("flatten", options, arguments, stopAtNonOption).as(String[].class);
    }
}
