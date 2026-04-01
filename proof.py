# proof.py
# S imply Z
# by The Proof is Trivial
# author: Thomas Cosh

#Standard Library Imports
import re

#Customs imports
from propositiontree import PropositionTreeNode, PropositionTree
from proofgraph import ProofNode, ProofGraph
import symbols as sym

class PropositionError(Exception):
    """Exception Thrown for any proposition errors (ie. undefined symbols, invalid format)."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class Proof:
    """Class proof handles methods for creating propositions, resolving the proposition, and creating a proof."""
    def __init__(self, prop: str) -> None:
        """Initializes a proof with an infix proposition and predefined multi-char symbols (ie <=, <>, !=, =>).
        prop: the infix proposition
        """
        self.infixProp = Proof.symbolize(prop)
        self.validateProp()
        self.proposition = Proof.fromInfixToPostfix(Proof.implicitToExplicitMul(self.infixProp))
        self.pTree = PropositionTree(self.proposition)
        self.trees = [PropositionTree(self.fromInfixToPostfix(PropositionTree.inOrder(p, ''))) for p in self.pTree.trees]
        self.graphs = [ProofGraph(t) for t in self.trees]
        self.proof = self.getProof()


    def validateProp(self) -> bool:

        format = r'[A-Za-z0-9' + sym.validOps + r']+' + r'[' + sym.validIfs + r'][A-Za-z0-9' + sym.validOps + r']+'
        for char in self.infixProp:
            if not char.isalnum() and char not in sym.precedence.keys() and char != sym._lbr and char != sym._rbr:
                raise PropositionError('Invalid operator ' + char + ' found in proposition ' + self.infixProp + '.')
        if not re.match(format, self.infixProp):
            raise PropositionError('Invalid proposition format. Expected if(f) P then Q.')

    @staticmethod
    def symbolize(prop: str) -> str:

        symbols = {
            '&&': sym._and,
            '||': sym._or,
            '<=>': sym._iff,
            '=>': sym._if,
            '>=': sym._ge,
            '<=': sym._le,
            '<>': sym._neq,
            '!=': sym._neq,
            '!': sym._not
        }

        converted = prop
        for old, new in symbols.items():
            converted = converted.replace(old, new)

        unary = ''
        for i, char in enumerate(converted):
            if char == sym._subt and (i == 0 or prop[i - 1] == sym._lbr or not prop[i - 1].isalnum()):
                unary += sym._neg
            else:
                unary += char

        return unary

    @staticmethod
    def implicitToExplicitMul(implicit: str) -> str:

        explicit = ''
        for i, char in enumerate(implicit[0:-1]):
            if char.isalnum() and implicit[i + 1].isalnum():
                explicit += char + sym._mul
            else:
                explicit += char
        explicit += implicit[-1]

        return str(explicit)

    @staticmethod
    def fromInfixToPostfix(infix: str) -> str:

        stack = []
        result = []

        for char in infix:

            #if symbol is operand, add to result
            if char.isalnum():
                result += char

                while stack and stack[-1] in sym.unaryOps:
                    result.append(stack.pop())

            elif char in sym.unaryOps:
                stack.append(char)

            # symbol is an operator
            elif char in sym.precedence.keys():

                while stack and stack[-1] != sym._lbr and (sym.precedence[stack[-1]] > sym.precedence[char] or (sym.precedence[stack[-1]] == sym.precedence[char] and sym.associativity[stack[-1]] == 'l')):
                    result.append(stack.pop())
                stack.append(char)

            elif char == sym._lbr:
                stack.append(char)

            elif char == sym._rbr:
                while stack and stack[-1] != sym._lbr:
                    result.append(stack.pop())
                stack.pop()

                while(stack and stack[-1] in sym.unaryOps):
                    result.append(stack.pop())

        while stack:
            result.append(stack.pop())

        return ''.join(result)

    def createPropTree(self) -> PropositionTreeNode:
        self.pTree = PropositionTree(self.proposition)

    def getProof(self) -> str:

        for g in self.graphs:
            g.discoverFacts()
        output = ''
        if len(self.graphs) > 1:
            output += f'Suppose {self.infixProp.split(sym._if)[0]}'
            for case, g in enumerate(self.graphs):
                #print(f'case {case + 1}: \n{g}')
                
                output += f'\nCase {case + 1}: Suppose {g.traverseProof()}\n'

            output += f'We see that in all cases, {self.infixProp.split(sym._if)[1]} ∎\n'
        else:
            #print(g)
            output += f'Suppose {g.traverseProof()} ∎\n'

        return output

    def getOperands(self) -> list:
        return sorted(self.pTree.operands)

    def __str__(self) -> str:

        output = ''
        output += 'Proposition: ' + self.infixProp + '\n'
        output += 'Known:\n'
        for i, line in enumerate(self.getKnown()):
            output += 'Case ' + str(i) + ': ' + str(line) + '\n'
        output += 'Want: ' + str(self.getWant())

        return output

    def combineKnown(self) -> None:
        self.pTree.combineKnown()


