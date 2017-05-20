"""
Logical Expression Microframework (WIP).
"""

class PropertyType(type):
    """
    Property type is used to generate Property objets.
    """
    def __getattr__(self, name):
        return Property(name)

    def __setattr__(self, name):
        raise AttributeError('PropertyType is read-only') #FIXME: exception class

class Property(object):
    """
    Represent a named and comparable property.
    """
    __metaclass__ = PropertyType
    name = None

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "P.%s" % self.name

    def __str__(self):
        return Dialect.property(self)

    def __eq__(self, value):
        return Expression(self, '==', value)

    def __ne__(self, value):
        return Expression(self, '<>', value)

    def __gt__(self, value):
        return Expression(self, '>', value)

    def __ge__(self, value):
        return Expression(self, '>=', value)

    def __lt__(self, value):
        return Expression(self, '<', value)

    def __le__(self, value):
        return Expression(self, '<=', value)

P = Property


class Dialect(object):
    """
    Define serialization dialect.
    TODO: make a pluggable dialect design.
    """
    operators = {'&':  'and',
                 '|':  'or',
                 '==': 'eq',
                 '<>': 'ne',
                 '>':  'gt',
                 '>=': 'ge',
                 '<':  'lt',
                 '<=': 'le'}

    values = {(True, type(True)): True,
              (False, type(False)): False,
              (None, type(None)): None}

    @classmethod
    def property(cls, property):
        """
        Serialize Property object.
        """
        return property.name

    @classmethod
    def value(cls, value):
        """
        Serialize property value.
        """
        return "'%s'" % cls.values.get((value, type(value)), value)

    @classmethod
    def expression(cls, expression):
        """
        Serialize Expression object.
        """
        return "{left} {operator} {right}".format(
            left = expression.left
                   if isinstance(expression.left, (Property, Expression))
                   else cls.value(expression.left),
            operator = cls.operators[expression.operator],
            right = expression.right
                    if isinstance(expression.right, (Property, Expression))
                    else cls.value(expression.right))

class Expression(object):
    left = None
    operator = None
    right = None

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __and__(self, other):
        return self.and_(other)

    def __or__(self, other):
        return self.or_(other)

    def __str__(self):
        return Dialect.expression(self)

    def __repr__(self):
        return "({0} {1} {2})".format(repr(self.left),
                                            self.operator,
                                            repr(self.right))

    def add(self, operator, *operands):
        return self.factory(operator, self, *operands)

    def and_(self, *operands):
        """
        Add the given operands to the Expression using the OR operator.
        """
        return self.add('&', *operands)

    def or_(self, *operands):
        """
        Add the given operands to the Expression using the AND operator.
        """
        return self.add('|', *operands)

    @staticmethod
    def factory(operator, *operands):
        """
        Produce an Expression object from the given operands.
        """
        operands = list(operands)
        left = operands.pop(0)
        for operand in operands:
            left = Expression(left, operator, operand)
        return left

def e(*operands):
    """
    Alias for and_().
    """
    return and_(*operands)

def and_(*operands):
    """
    Produce an Expression object with operands and AND operator.
    """
    return Expression.factory('&', *operands)

def or_(*operands):
    """
    Produce an Expression object with operands and the OR operator.
    """
    return Expression.factory('|', *operands)


if __name__ == '__main__':
    """
    Examples and tests (TODO).
    """
    # print factory_by(name='k', a=1, b=2, z=9)
    ex = e(P.first == 1)
    print ex
    ex = ex.and_(P.last == 'n').or_(P.tail == 'yes')
    print ex
    print eval(repr(ex))
    print or_(ex, P.opt == False, P.may == True, P.no == None)
    print ex.or_(P.opt == False, P.may == True, P.no == None)
    #print e(P.a == 'a', P.b >= 'b', or_(P.x == 1, P.y == 2), or_(P.xxx == 1, P.yyy == 2))
