package com.research.graalglue;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;

class ASTManager {

    private String filePath;

    public ASTManager(String filePath) {
        this.filePath = filePath;
    }

    public CompilationUnit readAST() {
        File file = new File(filePath);
        if (!file.exists()) {
            System.out.println("File not found: " + filePath);
            System.exit(1);
        }

        try {
            ParseResult<CompilationUnit> parseResult = new JavaParser().parse(file);
            if (parseResult.isSuccessful()) {
                Optional<CompilationUnit> compilationUnit = parseResult.getResult();
                return compilationUnit.orElse(null);
            } else {
                System.out.println("Failed to parse: " + filePath);
                return null;
            }
        } catch (IOException e) {
            e.printStackTrace();
            return null;
        }
    }

    public void writeAST(CompilationUnit ast, String outputPath) {
        Path path = Paths.get(outputPath);

        // Create directories if they don't exist
        path.getParent().toFile().mkdirs();

        try {
            Files.write(path, ast.toString().getBytes(StandardCharsets.UTF_8));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
