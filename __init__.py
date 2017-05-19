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
        if not name or not isinstance(name, basestring):
            raise ValueError('Property name must be string and cannot be empty')
        self.name = name

    def __str__(self):
        return Dialect.property(self)

    def __repr__(self):
        return "{%s}" % self.name

    def __eq__(self, value):
        return Expression(self, 'eq', value)

    def __ne__(self, value):
        return Expression(self, 'ne', value)

    def __gt__(self, value):
        return Expression(self, 'gt', value)

    def __ge__(self, value):
        return Expression(self, 'ge', value)

    def __lt__(self, value):
        return Expression(self, 'lt', value)

    def __le__(self, value):
        return Expression(self, 'le', value)

P = Property


class Dialect(object):
    """
    Define serialization dialect.
    TODO: make a pluggable dialect design.
    """
    operators = {'and': 'and',
                 'or': 'or',
                 'eq': 'eq',
                 'ne': 'ne',
                 'gt': 'gt',
                 'ge': 'ge',
                 'lt': 'lt',
                 'le': 'le'}

    # values = {(True, type(True)): True,
    #           (False, type(False)): False,
    #           (None, type(None)): None}

    @classmethod
    def property(cls, property):
        """
        Serialize Property object.
        """
        return property.name

    # @classmethod
    # def value(cls, value):
    #     """
    #     Serialize property value.
    #     """
    #     return cls.values.get((value, type(value)), value)

    @classmethod
    def expression(cls, expression):
        """
        Serialize Expression object.
        """
        return "({left} {operator} {right})".format(
            left=expression.left,
            operator=cls.operators[expression.operator],
            right=expression.right)

class Expression(object):
    left = None
    operator = None
    right = None

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self):
        return Dialect.expression(self)

    def __repr__(self):
        if isinstance(self, Expression):
            return "({0}<-{1}->{2})".format(repr(self.left),
                                            self.operator,
                                            repr(self.right))

    def __and__(self, other):
        return Expression(self, 'and', other)

    def __or__(self, other):
        return Expression(self, 'or', other)

    def add(self, operator, *operands):
        return self.__class__.factory(operator, self, *operands)

    def and_(self, *operands):
        """
        Add the given operands to the Expression using the OR operator.
        """
        return self.add('and', *operands)

    def or_(self, *operands):
        """
        Add the given operands to the Expression using the AND operator.
        """
        return self.add('or', *operands)

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
    return Expression.factory('and', *operands)

def or_(*operands):
    """
    Produce an Expression object with operands and the OR operator.
    """
    return Expression.factory('or', *operands)


if __name__ == '__main__':
    """
    Examples and tests (TODO).
    """
    # print factory_by(name='k', a=1, b=2, z=9)
    ex = e(P.first == 1)
    print ex
    ex = ex.and_(P.last == 'n').or_(P.tail == 'yes')
    print ex
    print or_(ex, P.opt == False, P.may == True, P.no == None)
    print ex.or_(P.opt == False, P.may == True, P.no == None)
    #print e(P.a == 'a', P.b >= 'b', or_(P.x == 1, P.y == 2), or_(P.xxx == 1, P.yyy == 2))
