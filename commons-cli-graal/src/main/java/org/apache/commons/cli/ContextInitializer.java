package org.apache.commons.cli;

import java.io.File;

import org.graalvm.polyglot.Engine;
import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.Source;
import org.graalvm.polyglot.Value;

/**
 * Provides a shared GraalVM engine and a method to get Python classes.
 */
final class ContextInitializer {
    /**
     * The shared GraalVM engine.
     */
    private static Engine sharedEngine;

    /**
     * Directory containing the Python source code.
     */
    private static String codeDirectory = "../commons-cli-python/src/main/python";

    /**
     * Directory containing the Python package.
     */
    private static String packageDirectory = "../commons-cli-python/src";

    /** Polyglot context for evaluating Python */
    private static Context context;

    static {
        try {
            sharedEngine = Engine.create();
            context = Context.newBuilder("python")
                    .allowAllAccess(true)
                    .option("python.PythonPath", packageDirectory)
                    .engine(sharedEngine)
                    .build();
        } catch (Exception e) {
            System.out.println("[-] " + e);
        }
    }

    public static Value[] getPythonClasses(String fileName, String... classNames) {
        try {
            File file = new File(codeDirectory, fileName);
            Source source = Source.newBuilder("python", file).build();
            assert source != null;

            context.eval(source);

            Value[] result = new Value[classNames.length];
            for (int i = 0; i < classNames.length; i++) {
                result[i] = context.getBindings("python").getMember(classNames[i]);
            }
            return result;
        } catch (Exception e) {
            System.out.println("[-] " + e);
            return null; // ??
        }
    }

    public static Value getPythonClass(String fileName, String className) {
        return getPythonClasses(fileName, className)[0];
    }
}
