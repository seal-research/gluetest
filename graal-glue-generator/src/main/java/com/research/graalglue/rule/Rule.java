package com.research.graalglue.rule;

import com.github.javaparser.ast.CompilationUnit;

public interface Rule {
    void applyRule(CompilationUnit ast);
}
