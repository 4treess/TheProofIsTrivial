from __future__ import annotations
import symbols as sym
import re

class PropositionTreeNode:

    def __init__(self, data: str, left: PropositionTreeNode = None, right: PropositionTreeNode = None, parent: PropositionTreeNode = None) -> None:

        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

    def __str__(self) -> str:

        return f'{self.data}'
    
    def __repr__(self) -> str:
        return str(self)

class PropositionTree:

    def __init__(self, proposition: str) -> None:

        self.root = PropositionTree.propToTree(proposition)
        self.operands = self.getOperands(self.root, set())
        self.wildcards = set()
        self.trees = self.removeOrNodes(self.root)

    @staticmethod
    def propToTree(proposition: str) -> PropositionTreeNode:

        stack = []

        for char in proposition:

            if char.isalnum():
                stack.append(PropositionTreeNode(char))

            elif char in sym.unaryOps:
                right = stack.pop()
                left = None

                stack.append(PropositionTreeNode(char, left, right))
                right.parent = stack[-1]
                
            else:
                right = stack.pop()
                left = stack.pop()

                stack.append(PropositionTreeNode(char, left, right))
                left.parent = right.parent = stack[-1]

        return stack[-1]

    @staticmethod
    def inOrder(root: PropositionTreeNode, word: str) -> str:

        lhs = ''
        rhs = ''
        if(root.left):
            lhs = PropositionTree.inOrder(root.left, word)

        if(root.right):
            rhs = PropositionTree.inOrder(root.right, word)
        word = root.data
        return lhs + word + rhs

    def getOperands(self, node: PropositionTreeNode, vars: set) -> set:

        if node.left:
            vars | self.getOperands(node.left, vars)
        if node.right:
            vars | self.getOperands(node.right, vars)

        if not node.left and not node.right:
            vars.add(node.data)

        return vars

    def newOperand(self, alphabet: chr) -> str:

        pattern = '[a-zA-Z]'
        if re.match(pattern, alphabet):
            operand = chr(ord(max(self.operands)) + 1)
            self.operands.add(operand)
        else:
            if not self.wildcards:
                operand = 'α'
            else:
                operand = chr(ord(max(self.wildcards)) + 1)
            self.wildcards.add(operand)

        return operand

    def removeOrNodes(self, node) -> list:

        if node is None:
            return [None]

        if node.data == sym._or:

            leftTree = self.removeOrNodes(node.left)
            rightTree = self.removeOrNodes(node.right)
            return leftTree + rightTree

        left = self.removeOrNodes(node.left)
        right = self.removeOrNodes(node.right)

        result = []

        for l in left:
            for r in right:
                newNode = PropositionTreeNode(node.data, l, r)
                result.append(newNode)

        return result


if __name__ == '__main__':

    pass
