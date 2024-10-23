package com.research.graalglue.rule;

import java.util.HashMap;
import java.util.Map;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Modifier;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.NodeList;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.ReturnStmt;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.stmt.TryStmt;
import com.github.javaparser.ast.type.*;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class ReplaceMethodBody extends VoidVisitorAdapter<Void> implements Rule {

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        String methodName = n.getNameAsString();
        Type returnType = n.getType();

        Expression newBodyExpression = determineNewBodyExpression(returnType, methodName, n);

        BlockStmt newBody = new BlockStmt();

        if (n.getThrownExceptions().isNonEmpty()) {
            handleMethodWithException(n, newBody, newBodyExpression);
        } else {
            // If the return type is the same as the class name, add 'return this;' 
            if (isSameAsClassName(n, returnType)) {
                newBody.addStatement(new ExpressionStmt(newBodyExpression));
                newBody.addStatement(new ReturnStmt(new ThisExpr()));
            } else if (returnType.isVoidType()) {
                newBody.addStatement(new ExpressionStmt(newBodyExpression));
            } else {
                newBody.addStatement(new ReturnStmt(newBodyExpression));
            }
        }

        n.setBody(newBody);

        super.visit(n, arg);
    }

    private void handleMethodWithException(MethodDeclaration n, BlockStmt newBody, Expression newBodyExpression) {
        // Wrap in try-catch block
        TryStmt tryStmt = new TryStmt();
        tryStmt.setTryBlock(new BlockStmt().addStatement(new ExpressionStmt(newBodyExpression)));

        Map<String, NodeList<Expression>> returnParameters = new HashMap<>();
        returnParameters.put("AlreadySelectedException", new NodeList<>(new ThisExpr(), new NameExpr("option")));
        returnParameters.put("IllegalArgumentException", new NodeList<>(new NameExpr("e")));

        // Assuming there's only one thrown exception, otherwise, you'll need a loop here
        CatchClause catchClause = new CatchClause(
                new Parameter(new ClassOrInterfaceType("PolyglotException"), "e"),
                new BlockStmt().addStatement(
                        new ThrowStmt(
                                new ObjectCreationExpr(
                                        null,
                                        new ClassOrInterfaceType(n.getThrownExceptions().get(0).asString()),
                                        returnParameters.getOrDefault(n.getThrownExceptions().get(0).asString(), new NodeList<>(new NameExpr("e")))))));
        tryStmt.getCatchClauses().add(catchClause);
        newBody.addStatement(tryStmt);
    }

    private boolean isSameAsClassName(MethodDeclaration n, Type returnType) {
        return getParentClassName(n).equals(returnType.asString());
    }

    private String getParentClassName(MethodDeclaration n) {
        if (n.getParentNode().isPresent() && n.getParentNode().get() instanceof ClassOrInterfaceDeclaration) {
            ClassOrInterfaceDeclaration parentDecl = (ClassOrInterfaceDeclaration) n.getParentNode().get();
            return parentDecl.getNameAsString();
        }
        return "";
    }

    private Expression determineNewBodyExpression(Type returnType, String methodName, MethodDeclaration n) {
        StringLiteralExpr methodToInvoke = new StringLiteralExpr(toSnakeCase(methodName));

        NodeList<Expression> invokeArgs = new NodeList<>(methodToInvoke);

        // Add all method parameters to the invoke arguments
        for (Parameter param : n.getParameters()) {
            invokeArgs.add(new NameExpr(param.getName()));
        }

        Expression basicInvoke = createBasicInvoke(invokeArgs, getParentClassName(n), n.isStatic());

        if (returnType.isVoidType()) {
            return basicInvoke;
        } else if (returnType.isPrimitiveType()) {
            return handlePrimitiveType(returnType, basicInvoke);
        } else if (returnType.isClassOrInterfaceType()) {
            return handleClassOrInterfaceType(returnType, basicInvoke, n);
        }
        return null;
    }

    private Expression handlePrimitiveType(Type returnType, Expression basicInvoke) {
        PrimitiveType primitiveType = returnType.asPrimitiveType();
        String asTypeMethod = "as" + primitiveType.asString().substring(0, 1).toUpperCase()
                + primitiveType.asString().substring(1);
        return new MethodCallExpr(basicInvoke, asTypeMethod);
    }

    private Expression handleClassOrInterfaceType(Type returnType, Expression basicInvoke, MethodDeclaration n) {
        ClassOrInterfaceType classType = returnType.asClassOrInterfaceType();
        if ("String".equals(classType.getNameAsString())) {
            return new MethodCallExpr(basicInvoke, "asString");
        } else if (classType.getNameAsString().startsWith("Collection")) {
            // Get the generic type of the Collection (like String or Option)
            Type genericType = classType.getTypeArguments().get().get(0);

            // If the generic type is String, use the .as(List.class) transformation
            if ("String".equals(genericType.asString())) {
                return new MethodCallExpr(basicInvoke, "as",
                        new NodeList<>(new ClassExpr(new ClassOrInterfaceType("List"))));
            } else {
                // If it's any other type, use the valueArrayToCollection transformation
                // But pass the ClassName.class as a parameter
                return new MethodCallExpr(
                        new NameExpr("IntegrationUtil"),
                        "valueArrayToCollection",
                        new NodeList<>(basicInvoke, new ClassExpr(genericType),
                                new ClassExpr(new ClassOrInterfaceType("ArrayList"))));
            }
        } else if (isSameAsClassName(n, returnType)) {
            return basicInvoke;
        } else {
            return new MethodCallExpr(basicInvoke, "as", new NodeList<>(new ClassExpr(classType)));
        }
    }

    private MethodCallExpr createBasicInvoke(NodeList<Expression> invokeArgs, String className, boolean isStatic) {
        String suffix = isStatic ? "Clz" : "Obj";
        return new MethodCallExpr(new NameExpr(pascalToCamelCase(className) + suffix), "invokeMember", invokeArgs);
    }

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
