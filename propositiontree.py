from __future__ import annotations
import symbols as sym
from equivalences import World, EquivalenceClass
import re
from copy import deepcopy

class PropositionTreeNode:

    def __init__(self, data: str, left: PropositionTreeNode = None, right: PropositionTreeNode = None, parent: PropositionTreeNode = None) -> None:

        self.data = data
        self.left = left
        self.right = right
        self.parent = parent

class PropositionTree:

    def __init__(self, proposition: str) -> None:

        self.root = PropositionTree.propToTree(proposition)
        self.operands = self.getOperands(self.root, set())
        self.wildcards = set()
        self.graph = ProofGraph()
        self.source = {'result': []}
        self.known = self.resolveTree(self.root.left, 'a')
        self.want = self.resolveTree(self.root.right, 'α')
        self.combineKnown()
        self.sortKnown()
        self.matchWantNeed()

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

    def inOrder(self, root: PropositionTreeNode, word: str) -> str:

        lhs = ''
        rhs = ''
        if(root.left):
            lhs = self.inOrder(root.left, word)

        if(root.right):
            rhs = self.inOrder(root.right, word)
        word = root.data
        return lhs + word + rhs

    def resolveTreeGraph(self, node: PropositionTreeNode, alphabet: chr) -> ProofNode:

        result = None
        lhs = None
        rhs = None
        op = node.data
        pNode = None

        if op == sym._and:
            pNode = self.graph.addAndFromNodes(self.resolveTreeGraph(node.left), self.resolveTreeGraph)

        if op == sym._dvds:
            newOp = self.newOperand(alphabet)
            fact = '' + rhs + '=' + lhs + newOp
            source = lhs + op + rhs
            result.append({rhs: '' + lhs + newOp})
            if alphabet < 'α':
                self.source[fact] = [source]
                self.source[source] = ['suppose']
                parent = self.graph.addFact(source, 'idk')
                child = self.graph.addFact(fact, 'definition of divides', [parent])
                parent.children.append(child)
            else:
                self.source['result'] = [source]
                #ans = self.graph.addResult(source)
                #tail = self.graph.addFact('basda'+fact, 'definition of divides', None, [ans])
                #ans.parent.append(tail)
        if not node.data.isalnum():
            result = self.resolveOperator(node, lhs, rhs, alphabet)

        return pNode

    def resolveOperatorGraph(self, node: PropositionTreeNode, lhs, rhs, alphabet) -> ProofNode:

        op = node.data
        result = None

        if op == sym._dvds:
            newOp = self.newOperand(alphabet)
            fact = '' + rhs + '=' + lhs + newOp
            source = lhs + op + rhs
            result.append({rhs: '' + lhs + newOp})
            if alphabet < 'α':
                self.source[fact] = [source]
                self.source[source] = ['suppose']
                parent = self.graph.addFact(source, 'idk')
                child = self.graph.addFact(fact, 'definition of divides', [parent])
                parent.children.append(child)
            else:
                self.source['result'] = [source]
                tail = self.graph.addResult(source)

        elif op == sym._and:
            result = lhs * rhs
        elif op == sym._or:
            result = lhs + rhs
        elif op == sym._mul:
            result = '' + lhs + rhs
        elif op in [sym._div, sym._subt, sym._add]:
            result = '(' + lhs + op + rhs + ')'

        return result

    def resolveTree(self, node: PropositionTreeNode, alphabet: chr) -> World:

        result = World()
        lhs = World()
        rhs = World()

        if node.left:
            lhs = self.resolveTree(node.left, alphabet)

        if node.right:
            rhs = self.resolveTree(node.right, alphabet)

        if not node.data.isalnum():
            result = self.resolveOperator(node, lhs, rhs, alphabet)

        else:
            result = node.data

        return result

    def resolveOperator(self, node: PropositionTreeNode, lhs, rhs, alphabet) -> World:

        op = node.data
        result = World()

        if op == sym._dvds:
            newOp = self.newOperand(alphabet)
            fact = '' + rhs + '=' + lhs + newOp
            source = lhs + op + rhs
            result.append({rhs: '' + lhs + newOp})
            if alphabet < 'α':
                self.source[fact] = [source]
                self.source[source] = ['suppose']
                parent = self.graph.addSuppose(source)
                child = self.graph.addFact(fact, 'combine facts', [parent])
                parent.children.append(child)
            else:
                self.source['result'] = [source]
                ans = self.graph.addResult(source)
                #tail = self.graph.addFact(fact, 'definition of divides', None, [ans])
                #ans.parent.append(tail)

        elif op == sym._and:
            result = lhs * rhs
        elif op == sym._or:
            result = lhs + rhs
        elif op == sym._mul:
            result = '' + lhs + rhs
        elif op in [sym._div, sym._subt, sym._add]:
            result = '(' + lhs + op + rhs + ')'

        return result

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

    def combineKnown(self) -> None:
        for eq in self.known.data:
            add = World()
            for key, equivalents in eq.items(): 
                for targetKey, targetValues in eq.items():
                    for value in targetValues:
                        if key in value:
                            for new in equivalents:
                                if new != key:
                                    fact = value.replace(key, new)
                                    add.append({targetKey: {fact}})
                                    self.source[targetKey+'='+fact] = [key + '=' + new, targetKey + '=' + value]
                                    p1 = self.graph.getNode(key + '=' + new)
                                    p2 = self.graph.getNode(targetKey + '=' + value)
                                    newNode = self.graph.addFact(targetKey+'='+fact, 'substitution', [p1,p2])
                                    p1.children.append(newNode)
                                    p2.children.append(newNode)
            self.addFacts(add, eq)

    def addFacts(self, add: World, eq: EquivalenceClass) -> None:
                
        for newFact in add:
            for k, v in newFact.items():
                if k in eq:
                    eq[k].update(v)
                else:
                    eq[k] = v

    def matchWantNeed(self) -> list:

        result = []
        for wantCase in self.want.data:
            add = World()
            for key, value in wantCase.items():
                pattern = ''
                for eq in value:
                    for char in eq:
                        if ord(char) < ord('α'):
                            pattern = pattern + char

            
                for needCase in self.known.data:
                    if key in needCase.keys():
                        for v in needCase[key]:
                            for eq in v:
                                if all(char in eq for char in pattern):
                                    newVar = self.newOperand('a')
                                    fact = pattern + newVar
                                    add.append({key: {fact}})
                                    newEq = ''.join(lttr for lttr in v if lttr not in pattern)
                                    add.append({newVar: {newEq}})
                                    self.source[key + '=' + fact] = [key + '=' + v, 'let ' + newVar + '=' + newEq]
                                    self.source[self.inOrder(self.root.right, '')] = [key + '=' + fact]
                                    #self.graph.addResult(self.inOrder(self.root.right, ''))
                                    p1 = self.graph.getNode(key + '=' + v)
                                    p2 = self.graph.addLet(newVar + '=' + newEq)
                                    ans = self.graph.getNode(pattern+'|'+key)
                                    child = self.graph.addFact(key+'='+fact, 'substitution', [p1,p2], [ans])
                                    p1.children.append(child)
                                    p2.children.append(child)
                                    ans.parent.append(child)

                    else:
                        coefficient = ''.join(char for char in key if char not in needCase.keys())
                        base = ''.join(char for char in key if char in needCase.keys())

            self.addFacts(add, needCase)

    def sortKnown(self) -> None:
        pass
        for eq in self.known:
            for key, values in eq.items():
                eq[key] = { ''.join(sorted(v)) for v in values}




class ProofNode:

    def __init__(self, data: str, rule: str, parent = None, children: list = None) -> None:

        self.data = data
        self.rule = rule
        self.parent = parent if parent else []
        self.children = children if children else []

    def __str__(self) -> str:

        return f'{self.data}'

    def __repr__(self) -> str:

        return f'{self.data}'

class ProofGraph:

    def __init__(self) -> None:

        self.suppose = ProofNode('Suppose', 'assumptions')
        self.result = ProofNode('our result. ∎', 'goal result')
        self.lets = ProofNode('LET', 'let the value be')
        self.vertices = [self.suppose, self.result, self.lets]

    def __str__(self) -> str:

        output = 'Vertices:\n'
        for v in self.vertices:
            output += str(v) + '\n'

        return output
    
    def __repr__(self) -> str:
        return self.__str__()

    def addFact(self, data: str, rule: str, parent = None, children = None) -> ProofNode:

        newNode = ProofNode(data, rule, parent, children)
        self.vertices.append(newNode)

        return newNode

    def addSuppose(self, data, children = None) -> ProofNode:

        newNode = self.addFact(data, 'suppose', [self.suppose], children)
        self.suppose.children.append(newNode)

        return newNode

    def addResult(self, data) -> ProofNode:

        newNode = self.addFact(data, '', None, [self.result])
        self.result.parent.append(newNode)

        return newNode

    def addAnd(self, fact1, rule1, children1, fact2, rule2, children2, parent) -> ProofNode:

        if parent in self.suppose:
            andNode = self.addSuppose('AND', [])
        else:
            andNode = self.addFact('AND', 'logical and', [parent])
        newNode1 = self.addFact(fact1, rule1, [andNode], children1)
        newNode2 = self.addFact(fact2, rule2, [andNode], children2)
        andNode.children = [newNode1, newNode2]

    def addAndFromNode(self, node1: ProofNode, node2: ProofNode) -> ProofNode:

        andNode = self.addFact('AND', 'logical and', None, [node1, node2])
        node1.parent.append(andNode)
        node2.parent.append(andNode)

        return andNode
    
    def addLet(self, data: str, children = None) -> ProofNode:

        newNode = self.addFact(data, 'let value be', [self.lets], children)
        self.lets.children.append(newNode)

        return newNode

    def getNode(self, data: str) -> ProofNode:

        for vertex in self.vertices:
            if vertex.data == data:
                return vertex
        return None
    
    def traverseProof(self) -> str:

        result = ''
        printed = set() 
        output = []

        def visit(node):
            if node in printed:
                return

            printed.add(node)

            for p in node.parent:
                visit(p)

            if node.data not in ("Suppose", "LET") and all(p.data not in ("Suppose", "LET") for p in node.parent):
                if node.parent:
                    parents_str = ', '.join([p.data for p in node.parent])
                    output.append(f"From {parents_str} we get {node.data}")
                else:
                    output.append(node.data)

            for c in node.children:
                visit(c)

        if self.suppose.children:
            result += f"Suppose {', '.join([c.data for c in self.suppose.children])}\n"
        if self.lets.children:
            result += f"Let {', '.join([c.data for c in self.lets.children])}\n"

        visit(self.suppose)


        result += '.\n'.join(line for line in output)

        return result

if __name__ == '__main__':

    G = ProofGraph()
    G.addSuppose('a|b')
    G.addSuppose('b|c')
    print(G.vertices)

    print(G.getNode('a|b'))
