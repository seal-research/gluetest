package com.research.graalglue.rule;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

import java.util.Arrays;
import java.util.List;

public class AddGraalImports extends VoidVisitorAdapter<Void> implements Rule {

    private final List<String> REQUIRED_IMPORTS = Arrays.asList(
            "org.graalvm.polyglot.PolyglotException",
            "org.graalvm.polyglot.Value",
            "java.util.HashMap",
            "java.util.Map",
            "java.util.List",
            "java.util.ArrayList"
            );

    @Override
    public void visit(CompilationUnit n, Void arg) {
        for (String requiredImport : REQUIRED_IMPORTS) {
            addImportIfAbsent(n, requiredImport);
        }

        super.visit(n, arg);
    }

    private void addImportIfAbsent(CompilationUnit n, String importName) {
        boolean hasImport = n.getImports().stream()
                .anyMatch(importDeclaration -> importDeclaration.getNameAsString().equals(importName));

        if (!hasImport) {
            n.addImport(importName);
        }
    }

    @Override
    public void applyRule(CompilationUnit ast) {
        ast.accept(this, null);
    }
}
