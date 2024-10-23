package com.research.graalglue;

import com.github.javaparser.ast.CompilationUnit;

public class App {
    public static void main(String[] args) {
        final String FILE_NAME = "PUT_FILE_PATH_HERE";

        ASTManager astManager = new ASTManager(FILE_NAME);
        CodeModifier codeModifier = new CodeModifier();

        // Read the AST
        CompilationUnit ast = astManager.readAST();

        // Apply the rules
        codeModifier.applyAllRules(ast);

        // Write back the modified AST
        astManager.writeAST(ast, "generated/" + FILE_NAME);
    }
}
