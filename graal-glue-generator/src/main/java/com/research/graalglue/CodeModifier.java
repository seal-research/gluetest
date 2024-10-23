package com.research.graalglue;

import com.github.javaparser.ast.CompilationUnit;

import java.util.ArrayList;
import java.util.List;

import com.research.graalglue.rule.AddGraalImports;
import com.research.graalglue.rule.AddHelperMembers;
import com.research.graalglue.rule.RemovePrivateMembers;
import com.research.graalglue.rule.ReplaceMethodBody;
import com.research.graalglue.rule.Rule;

public class CodeModifier {

    private final List<Rule> rules;

    public CodeModifier() {
        this.rules = new ArrayList<>();
        rules.add(new RemovePrivateMembers());
        rules.add(new AddGraalImports());
        rules.add(new ReplaceMethodBody());
        rules.add(new AddHelperMembers());
        // Add more visitors as needed
    }

    public void applyAllRules(CompilationUnit ast) {
        for (Rule r : rules) {
            try {
                r.applyRule(ast);
            } catch (AssertionError e) { }
        }
    }
}
