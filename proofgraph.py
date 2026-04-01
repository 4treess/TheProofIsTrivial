from propositiontree import PropositionTreeNode, PropositionTree
from collections import deque
import symbols as sym

class ProofNode:

    def __init__(self, relation, lhs, rhs, rule: str, parent = None, children: list = None) -> None:

        self.relation = relation
        self.lhs = ''.join(sorted(lhs)) if lhs.isalnum() else lhs
        self.rhs = ''.join(sorted(rhs)) if rhs.isalnum() else rhs
        self.data = f'{self.lhs}{self.relation}{self.rhs}'
        self.rule = rule
        self.parent = parent if parent else []
        self.children = children if children else []

    def __str__(self) -> str:

        return f'{self.data} {f"{self.rule}" if self.rule else ""}'

    def __repr__(self) -> str:

        return str(self)
    
    def __hash__(self):
        return hash(self.data)
    
    def __eq__(self, other) -> bool:

        eq = False
        if isinstance(other, ProofNode):
            eq = self.data == other.data

        elif isinstance(other, str):
            eq = self.data == other

        return eq

class ProofGraph:

    def __init__(self, propositionTree: PropositionTree = None) -> None:

        self.suppose = []
        self.result = []
        self.lets = []
        self.vertices = []
        self.partitions = []
        self.target = None
        self.pTree = propositionTree
        self.graphFromPropTree(self.pTree)

    def __str__(self) -> str:

        output = 'Vertices:\n'
        for v in self.vertices:
            output += f'{v.parent}=>{v} ({v.rule})\n'

        return output
    
    def __repr__(self) -> str:
        return self.__str__()

    def addFact(self, relation, lhs, rhs, rule: str, parent = None, children = None) -> ProofNode:

        newNode = None
        data = f'{lhs}{relation}{rhs}'
        if data not in self.vertices:
            newNode = ProofNode(relation, lhs, rhs, rule, parent, children)
            self.vertices.append(newNode)
        else:
            newNode = self.getNode(data)
            if parent:
                newNode.parent.extend([p for p in parent if p not in newNode.parent])

            if children:
                newNode.children.extend([c for c in children if c not in newNode.children])

        if parent:
            for p in parent:
                if newNode not in p.children:
                    p.children.append(newNode)
        if children:
            for c in children:
                if newNode not in c.parent:
                    c.parent.append(newNode)

        return newNode
    
    def addAndFromNode(self, node1: ProofNode, node2: ProofNode) -> ProofNode:

        andNode = self.addFact(sym._and, node1.data, node2.data, None, None, [node1, node2])
        return andNode

    def addOrFromNodes(self, node1: ProofNode, node2: ProofNode) -> ProofNode:

        orNode = self.addFact(sym._or, node1.data, node2.data, None, None, [node1, node2])
        return orNode

    def addLet(self, data: str, children = None) -> ProofNode:

        newNode = self.addFact(data, 'let value be', [self.lets], children)

        return newNode

    def getNode(self, data: str) -> ProofNode:

        for vertex in self.vertices:
            if vertex.data == data:
                return vertex
        return None

    def addNode(self, relation: str, lhs: str, rhs: str, rule: str, parent = None, children = None) -> ProofNode:

        return self.addFact(f'{lhs}{relation}{rhs}', rule, parent, children, relation, lhs, rhs)

    def graphFromPropTree(self, tree: PropositionTree) -> None:

        self.resolveTree(tree.root.right, 'α')
        self.suppose = self.resolveTree(tree.root.left, 'a')

    def resolveTree(self, node: PropositionTreeNode, alphabet: str) -> PropositionTreeNode:

        result = None
        lhs = None
        rhs = None

        if node.left:
            lhs = self.resolveTree(node.left, alphabet)

        if node.right:
            rhs = self.resolveTree(node.right, alphabet)

        if not node.data.isalnum():
            result = self.resolveOperator(node, lhs, rhs, alphabet)

        else:
            result = node.data

        return result

    def resolveOperator(self, node: PropositionTreeNode, lhs: ProofNode, rhs: ProofNode, alphabet: str) -> ProofNode:

        op = node.data
        result = None

        if op == sym._and:
            result = self.addAndFromNode(lhs, rhs)

        if op == sym._dvds:
            newOperand = self.pTree.newOperand(alphabet)
            statement = f'{lhs}{sym._dvds}{rhs}'
            fact = f'{rhs}={lhs}{newOperand}'
            rule = 'definition of divides'
            if alphabet > 'a':
                result = ProofNode(sym._dvds, lhs, rhs, rule)
                self.target = ProofNode(sym._eq, rhs, lhs+newOperand, rule, None, [result])
                result.parent.append(self.target)
            else:
                result = self.addFact(sym._dvds, lhs, rhs, None)
                self.addFact(sym._eq, rhs, f'{lhs}{newOperand}', rule, [result])

        if op == sym._mul:
            result = f'{lhs}{rhs}'
        return result

    def discoverFacts(self) -> bool:

        discovery = True
        foundTarget = False
        while discovery and not foundTarget:
            discovery = False
            discovery |= self.findTransitivitySubstitutions()
            discovery |= self.findTransitivityChains()
            discovery |= self.removeCommonFactors()
            discovery |= self.multiplyByEquality()

            if self.getTarget():
                return True

        return foundTarget

    def multiplyByEquality(self) -> bool:

        for char in self.target.lhs:
            char_comp = ''.join(c for c in self.target.lhs if c != char)
            for v1 in (v for v in self.vertices if v.relation == sym._eq):
                if char in v1.lhs and not char_comp in v1.lhs:
                    multiplier = char_comp
                    if any(c not in v1.rhs for c in multiplier):
                        lhs = v1.lhs + multiplier
                        rhs = v1.rhs + multiplier
                        fact = f'{lhs}{sym._eq}{rhs}'
                        if fact not in self.vertices:
                            self.addFact(sym._eq, lhs, rhs, f'multiply both sides by {multiplier}', [v1])
                            return True
                    
        return False

    def getTarget(self) -> bool:
        # i need to find all ors that i can not just the first one
        for v1 in (v for v in self.vertices if v.relation == sym._eq):
            if v1.lhs == self.target.lhs:
                pattern = ''.join(char for char in self.target.rhs if char <= 'z')
                if all(p in v1.rhs for p in pattern):
                    rhs = ''.join(char for char in v1.rhs if char not in pattern)
                    lhs = ''.join(char for char in self.target.rhs if char > 'z')
                    #self.lets = self.addFact(sym._eq, lhs, rhs, f'let {lhs}={rhs}')
                    self.vertices.append(self.target) 
                    self.vertices.extend(self.target.children)
                    self.target.parent = [v1]
                    self.target.rule = f'let {lhs}={rhs}'
                    v1.children.append(self.target)
                    #self.lets.children.append(self.target)

                    return True

        return False

    def findTransitivitySubstitutions(self) -> None:

        foundFact = False
        for v1 in (v for v in self.vertices if v.relation == sym._eq):
            for v2 in (v for v in self.vertices if v.relation == sym._eq):
                if v1.lhs in v2.rhs:
                    lhs = v2.lhs
                    rhs = v2.rhs.replace(v1.lhs, v1.rhs)
                    fact = f'{lhs}{sym._eq}{rhs}'
                    if fact not in self.vertices:
                        self.addFact(sym._eq, lhs, rhs, f'substite {v1.lhs} for {v1.rhs}', [v1, v2])
                        return True

        return False

    def findTransitivityChains(self) -> bool:

        foundFact = False
        for v1 in (v for v in self.vertices if v.relation == sym._eq):
            for v2 in (v for v in self.vertices if v.relation == sym._eq):
                if v1.lhs == v2.lhs and v1.rhs != v2.rhs:
                    lhs = v1.rhs
                    rhs = v2.rhs
                    fact = f'{lhs}{sym._eq}{rhs}'
                    inverse = f'{rhs}{sym._eq}{lhs}'
                    if fact not in self.vertices and inverse not in self.vertices and lhs != rhs:
                        self.addFact(sym._eq, lhs, rhs, 'transitivity of equals / sub', [v1, v2])
                        return True

        return False

    def removeCommonFactors(self) -> bool:

        for v1 in (v for v in self.vertices if v.relation == sym._eq):
            for char in (c for c in v1.lhs if c in v1.rhs):
                lhs = v1.lhs.replace(char, '')
                rhs = v1.rhs.replace(char, '')
                fact = f'{lhs}{sym._eq}{rhs}'
                if fact not in self.vertices:
                    self.addFact(sym._eq, lhs, rhs, f'factor out {char}, {char}!= 0', [v1])
                    return True

        return False

    def traverseProof(self) -> str:

        stack = []
        visited = set()

        def dfs(node: ProofNode) -> None:

            if node in visited:
                return
            
            visited.add(node)

            for parent in getattr(node, 'parent'):
                dfs(parent)

            stack.append(node)

        dfs(self.target.children[0])

        return '\n'.join(f'{"From " + ", ".join(p.data for p in getattr(n, "parent")) + " we get " if n.parent else ""}{n.data} {f"({n.rule})" if n.rule else ""}' for n in stack)


if __name__ == '__main__':

    g = ProofGraph()
    g.addResult('a|c')
    g.addFact('c=az', 'def of |', None, [g.getNode('a|c')])
    g.addSuppose('a|b')
    g.addFact('b=ax', 'def of |', [g.getNode('a|b')])
    g.addSuppose('b|c')
    g.addFact('c=by', 'def of |', [g.getNode('b|c')])
    g.addFact('c=axy', 'combine facts', [g.getNode('b=ax'), g.getNode('c=by')])
    g.addLet('xy=z')
    g.addFact('c=az', 'substitute variables', [g.getNode('c=axy'), g.getNode('xy=z')])
    g.addFact('a|c', 'def of |2', [g.getNode('c=az')]) 

    r = g.getNode('a|c')
    print('rule:', r.rule, r.parent, r.children)
    print( g.getNode('a|c'))
    for v in g.vertices:
        print(f'{str(v.parent) + "=>" if v.parent else ""}{v, v.rule} => {v.children}')