package com.research.graalglue.rule;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.ConstructorDeclaration;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.InitializerDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.VariableDeclarator;
import com.github.javaparser.ast.expr.AssignExpr;
import com.github.javaparser.ast.expr.NameExpr;
import com.github.javaparser.ast.expr.AssignExpr.Operator;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class AddHelperMembers extends VoidVisitorAdapter<Void> implements Rule {

    @Override
    public void visit(ClassOrInterfaceDeclaration n, Void arg) {
        String className = n.getNameAsString();
        String pythonFileName = toSnakeCase(className) + ".py";

        // Add Constructor
        n.addMember(new ConstructorDeclaration()
                .setModifier(Modifier.Keyword.PUBLIC, true)
                .setName(className)
                .addParameter("Value", "foreign" + className)
                .setBody(new BlockStmt()
                        .addStatement(new AssignExpr(
                                new NameExpr(pascalToCamelCase(className) + "Obj"),
                                new NameExpr("foreign" + className),
                                Operator.ASSIGN))));
        n.addMember(new ConstructorDeclaration()
                .setModifier(Modifier.Keyword.PUBLIC, true)
                .setName(className)
                .setBody(new BlockStmt()
                        .addStatement(new AssignExpr(
                                new NameExpr(pascalToCamelCase(className) + "Obj"),
                                new NameExpr(pascalToCamelCase(className) + "Clz.execute()"),
                                Operator.ASSIGN))));

        // Add fields
        n.addMember(new FieldDeclaration()
                .setModifier(Modifier.Keyword.PRIVATE, true)
                .setModifier(Modifier.Keyword.STATIC, true)
                .addVariable(new VariableDeclarator().setType("Value").setName(pascalToCamelCase(className) + "Clz"))
                .setJavadocComment("Contains a reference to the Python class."));
        n.addMember(new FieldDeclaration()
                .setModifier(Modifier.Keyword.PRIVATE, true)
                .addVariable(new VariableDeclarator().setType("Value").setName(pascalToCamelCase(className) + "Obj"))
                .setJavadocComment("Contains a reference to the embedded Python object."));
        n.addMember(new FieldDeclaration()
                .setModifier(Modifier.Keyword.PRIVATE, true)
                .setModifier(Modifier.Keyword.STATIC, true)
                .addVariable(new VariableDeclarator().setType("Map<Value, " + className + ">").setName("cache")
                        .setInitializer("new HashMap<>()"))
                .setJavadocComment("Cache for wrappers to python objects"));

        // Add static block
        n.addMember(new InitializerDeclaration()
                .setStatic(true)
                .setBody(new BlockStmt()
                        .addStatement(pascalToCamelCase(className) + "Clz = ContextInitializer.getPythonClass(\""
                                + pythonFileName + "\", \"" + className + "\");")));

        // Add methods
        n.addMember(new MethodDeclaration()
                .setModifier(Modifier.Keyword.PUBLIC, true)
                .setType("Value")
                .setName("getPythonObject")
                .setBody(new BlockStmt().addStatement("return " + pascalToCamelCase(className) + "Obj;")));
        n.addMember(new MethodDeclaration()
                .setModifier(Modifier.Keyword.PUBLIC, true)
                .setModifier(Modifier.Keyword.STATIC, true)
                .setType(className)
                .setName("create")
                .addParameter("Value", "foreign" + className)
                .setBody(new BlockStmt()
                        .addStatement("if (foreign" + className + ".isNull()) { return null; }")
                        .addStatement(
                                "return cache.computeIfAbsent(foreign" + className + ", " + className + "::new);")));

        super.visit(n, arg);
    }

    @Override
    public void applyRule(CompilationUnit ast) {
        ast.accept(this, null);
    }

    /**
    * Converts a given string, which may be in PascalCase or camelCase, to snake_case.
    *
    * @param str The input string in either PascalCase or camelCase format.
    * @return The string converted to snake_case. If the input is null or empty, the original string is returned.
    */
    private static String toSnakeCase(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }

        StringBuilder snakeCase = new StringBuilder();

        // Convert the first character to lowercase for consistency
        snakeCase.append(Character.toLowerCase(str.charAt(0)));

        for (int i = 1; i < str.length(); i++) {
            char currentChar = str.charAt(i);

            // If the current character is uppercase, append underscore
            if (Character.isUpperCase(currentChar)) {
                snakeCase.append('_');
                snakeCase.append(Character.toLowerCase(currentChar));
            } else {
                snakeCase.append(currentChar);
            }
        }

        return snakeCase.toString();
    }

    /**
     * Converts a string from PascleCase to camelCase
     * 
     * @param str The input string in PascalCase format.
     * @return The string converted to camelCase. If the input is null or empty, the original string is returned.
     */
    private static String pascalToCamelCase(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }

        return str.substring(0, 1).toLowerCase() + str.substring(1);
    }
}
