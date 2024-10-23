package com.research.graalglue.rule;

import java.util.ArrayList;
import java.util.List;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.Node;
import com.github.javaparser.ast.body.FieldDeclaration;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class RemovePrivateMembers extends VoidVisitorAdapter<Void> implements Rule {

    private final List<Node> nodesToRemove = new ArrayList<>();
    private final String[] exceptionalVariables = { "serialVersionUID" };
    private final String[] exceptionalMethods = { "isValidChar", "isValidOpt" };

    @Override
    public void visit(FieldDeclaration n, Void arg) {
        if (n.isPrivate()) {
            boolean isExceptional = false;
            for (String exceptionalVariable : exceptionalVariables) {
                if (n.getVariable(0).getNameAsString().equals(exceptionalVariable)) {
                    isExceptional = true;
                    break;
                }
            }

            if (!isExceptional) {
                nodesToRemove.add(n);
            }
        }
        super.visit(n, arg);
    }

    @Override
    public void visit(MethodDeclaration n, Void arg) {
        if (n.isPrivate()) {
            boolean isExceptional = false;
            for (String exceptionalMethod : exceptionalMethods) {
                if (n.getNameAsString().equals(exceptionalMethod)) {
                    isExceptional = true;
                    break;
                }
            }

            if (!isExceptional) {
                nodesToRemove.add(n);
            }
        }
        super.visit(n, arg);
    }

    public void applyRule(CompilationUnit ast) {
        ast.accept(this, null);

        // After the traversal is complete, remove the accumulated nodes
        for (Node node : nodesToRemove) {
            node.remove();
        }
        nodesToRemove.clear();
    }
}
